"""Tiny SVG typesetter for the Akai (赤) Anime assets.

Text is shaped with HarfBuzz (real kerning), every glyph is written once per SVG as a <path> in
<defs> and placed with <use>, so the SVGs need no web fonts and look identical on every OS.
Fonts: Noto Sans CJK JP (its Latin is Source Sans) for sans and kanji, Source Code Pro for mono,
Noto Serif CJK JP for the seal. All three are SIL OFL fonts that ship with Fedora.
"""
import hashlib, os, tempfile
from pathlib import Path
import uharfbuzz as hb
from fontTools.ttLib import TTCollection, TTFont
from fontTools import subset
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

CACHE = Path(os.environ.get('AKAI_FONT_CACHE', Path(tempfile.gettempdir()) / 'akai-fonts'))
CACHE.mkdir(parents=True, exist_ok=True)

SANS_VF = '/usr/share/fonts/google-noto-sans-cjk-vf-fonts/NotoSansCJK-VF.ttc'
SERIF_VF = '/usr/share/fonts/google-noto-serif-cjk-vf-fonts/NotoSerifCJK-VF.ttc'
MONT = {400: '/usr/share/fonts/julietaula-montserrat-fonts/Montserrat-Regular.otf',
        500: '/usr/share/fonts/julietaula-montserrat-fonts/Montserrat-Medium.otf',
        700: '/usr/share/fonts/julietaula-montserrat-fonts/Montserrat-Bold.otf',
        900: '/usr/share/fonts/julietaula-montserrat-fonts/Montserrat-Black.otf'}
MONT_SCALE = 0.93   # Montserrat runs wide; draw it a touch smaller than the nominal size so layouts built for Source Sans still fit

def has_cjk(s):
    return any(ord(c) > 0x2E80 for c in s)

MONO = {400: '/usr/share/fonts/adobe-source-code-pro-fonts/SourceCodePro-Regular.otf',
        500: '/usr/share/fonts/adobe-source-code-pro-fonts/SourceCodePro-Medium.otf',
        600: '/usr/share/fonts/adobe-source-code-pro-fonts/SourceCodePro-Semibold.otf',
        700: '/usr/share/fonts/adobe-source-code-pro-fonts/SourceCodePro-Bold.otf'}

# every CJK character any asset uses; the build fails loudly if a glyph is missing
CJK = ('クリム赤開発者バックエンド第一二三四五六零話次回予告キャラクターシートステータス記録スキル'
       '電波選牧犬学麦つづく選手権公開版スマホ連続日印依頼修行道具主力常用実戦ゴドピッ持ち物'
       '年月火水木金土本番研究所験人顔差計七自動化ウザブメルボト運用特技券斬刀')
LATIN = ''.join(chr(c) for c in range(0x20, 0x7f)) + '·×→←↓↑°…’'


def _instance(ttc_path, text, weight, tag):
    key = hashlib.md5((ttc_path + text + str(weight)).encode()).hexdigest()[:10]
    out = CACHE / f'{tag}-{weight}-{key}.ttf'
    if out.exists():
        return out
    ttc = TTCollection(ttc_path, lazy=True)
    f = [x for x in ttc.fonts if 'JP' in x['name'].getDebugName(1)][0]
    opts = subset.Options(); opts.notdef_outline = True; opts.hinting = False
    opts.layout_features = ['kern', 'liga', 'calt', 'palt', 'vert', 'vkrn']
    sub = subset.Subsetter(opts); sub.populate(text=text); sub.subset(f)
    tmp = CACHE / f'{tag}-{key}-subset.otf'; f.save(str(tmp))
    inst = instancer.instantiateVariableFont(TTFont(str(tmp)), {'wght': weight}, inplace=False, optimize=False)
    inst.save(str(out))
    return out


class Font:
    def __init__(self, key, path):
        self.key = key
        self.tt = TTFont(str(path))
        self.upm = self.tt['head'].unitsPerEm
        if key.startswith('lat'): self.upm = self.upm / MONT_SCALE
        self.cmap = self.tt.getBestCmap()
        self.order = self.tt.getGlyphOrder()
        self.gs = self.tt.getGlyphSet()
        blob = hb.Blob.from_file_path(str(path))
        self.hbfont = hb.Font(hb.Face(blob))
        self._paths = {}

    def check(self, text):
        missing = sorted({c for c in text if ord(c) not in self.cmap and c not in '\n'})
        if missing:
            raise SystemExit(f'font {self.key} lacks glyphs for {missing!r}')

    def shape(self, text):
        self.check(text)
        buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
        hb.shape(self.hbfont, buf, {'kern': True, 'liga': False})
        out = [(i.codepoint, p.x_advance, p.x_offset, p.y_offset) for i, p in zip(buf.glyph_infos, buf.glyph_positions)]
        dot = self.cmap.get(0xB7)
        if self.key.startswith('sans') and dot:
            # the CJK font's middle dot is JIS-wide; set it like a Latin interpunct
            gdot = self.order.index(dot); tight = int(self.upm * .3)
            out = [(g, tight, xo - (a - tight) // 2, yo) if g == gdot else (g, a, xo, yo) for g, a, xo, yo in out]
        return out

    def path(self, gid):
        if gid not in self._paths:
            pen = SVGPathPen(self.gs, ntos=lambda v: str(int(round(v))))
            self.gs[self.order[gid]].draw(TransformPen(pen, (1, 0, 0, -1, 0, 0)))
            self._paths[gid] = pen.getCommands()
        return self._paths[gid]

    def advance(self, ch):
        return self.tt['hmtx'][self.cmap[ord(ch)]][0]


_FONTS = {}
def font(key, text=''):
    """sans400 sans500 sans700 sans900 mono400..mono700 serif900; Latin-only sans text is set in Montserrat (key lat###)"""
    if key.startswith('sans') and text and not has_cjk(text):
        key = 'lat' + key[-3:]
    if key not in _FONTS:
        fam, w = key[:-3], int(key[-3:])
        if fam == 'lat':
            p = MONT[w]
        elif fam == 'sans':
            p = _instance(SANS_VF, LATIN + CJK, w, 'sans')
        elif fam == 'serif':
            p = _instance(SERIF_VF, LATIN + CJK, w, 'serif')
        else:
            p = MONO[w]
        _FONTS[key] = Font(key, p)
    return _FONTS[key]


def f2(v):
    s = f'{v:.2f}'.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


class Doc:
    """Collects glyph definitions for one SVG file."""
    def __init__(self):
        self.ids = {}; self.defs = []

    def _gid(self, fnt, gid):
        k = (fnt.key, gid)
        if k not in self.ids:
            i = f'{fnt.key[0]}{fnt.key[-3]}{len(self.ids):x}'
            self.ids[k] = i
            d = fnt.path(gid)
            self.defs.append(f'<path id="{i}" d="{d}"/>' if d else f'<path id="{i}" d=""/>')
        return self.ids[k]

    def measure(self, s, size, fkey='sans400', ls=0):
        fnt = font(fkey, s); k = size / fnt.upm
        adv = sum(a for _, a, _, _ in fnt.shape(s))
        return adv * k + ls * max(0, len(s) - 1)

    def text(self, s, x, y, size, fkey='sans400', fill='#000', ls=0, anchor='start', opacity=None, extra='', skew=0):
        fnt = font(fkey, s); k = size / fnt.upm
        glyphs = fnt.shape(s)
        w = sum(a for _, a, _, _ in glyphs) * k + ls * max(0, len(glyphs) - 1)
        if anchor == 'middle': x -= w / 2
        elif anchor == 'end': x -= w
        cur = 0.0; uses = []; lsu = ls / k
        for gid, adv, xo, yo in glyphs:
            if fnt.path(gid):
                ya = f' y="{-yo}"' if yo else ''
                uses.append(f'<use href="#{self._gid(fnt, gid)}" x="{int(round(cur + xo))}"{ya}/>')
            cur += adv + lsu
        op = f' opacity="{opacity}"' if opacity is not None else ''
        sk = f' skewX({skew})' if skew else ''
        return f'<g transform="translate({f2(x)} {f2(y)}){sk} scale({k:.5f})" fill="{fill}"{op}{extra}>{"".join(uses)}</g>'

    def vtext(self, s, cx, ytop, size, fkey='sans700', fill='#000', gap=0, opacity=None, extra=''):
        """Vertical column of upright CJK glyphs centred on cx, first em box starting at ytop."""
        fnt = font(fkey); k = size / fnt.upm
        uses = []; cy = 0.88 * fnt.upm
        for ch in s:
            fnt.check(ch)
            gid = fnt.shape(ch)[0][0]
            adv = fnt.tt['hmtx'][fnt.order[gid]][0]
            uses.append(f'<use href="#{self._gid(fnt, gid)}" x="{int(-adv / 2)}" y="{int(cy)}"/>')
            cy += fnt.upm + gap / k
        op = f' opacity="{opacity}"' if opacity is not None else ''
        return f'<g transform="translate({f2(cx)} {f2(ytop)}) scale({k:.5f})" fill="{fill}"{op}{extra}>{"".join(uses)}</g>'

    def wrap(self, s, size, fkey, width, ls=0):
        words = s.split(' '); lines = []; cur = ''
        for w in words:
            t = (cur + ' ' + w).strip()
            if self.measure(t, size, fkey, ls) <= width or not cur:
                cur = t
            else:
                lines.append(cur); cur = w
        if cur: lines.append(cur)
        return lines

    def svg(self, w, h, body, label, style=''):
        st = f'<style>{style}</style>\n' if style else ''
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{label}">\n'
                f'<title>{label}</title>\n{st}<defs>{"".join(self.defs)}</defs>\n{body}\n</svg>\n')
