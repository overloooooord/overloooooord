#!/usr/bin/env python3
"""Glyph kit for the live contribution log.

contrib_turtle.py draws that panel every day inside GitHub Actions, where the profile fonts are not installed, so
everything it needs from this machine is baked here: glyph outlines for the few styles it sets (in font units, y down,
the same outlines typeset.Doc uses), the two theme palettes and the halftone at the right edge.
Run after a font or palette change: python3 log_kit.py  (writes data/log-kit.json, commit it).
"""
import json
from build_assets import DARK, LIGHT, INK, PAPER, AKA, NEON, HERE, halftone_x
from typeset import font

ASCII = ''.join(chr(c) for c in range(0x20, 0x7f)) + '·×'
STYLES = {   # kit name: (typeset key, characters)
    'mono700': ('mono700', ASCII),
    'mono500': ('mono500', ASCII),
    'num900': ('sans900', '0123456789,+'),      # Latin-only sans text is Montserrat, as everywhere else
    'cjk700': ('sans700', '修行'),
    'cjk900': ('sans900', '連続'),
}
THEME_KEYS = ('bg', 'panel', 'text', 'muted', 'dim', 'line', 'frame', 'frame_op', 'akatext', 'hot', 'tone', 'cell')

def main():
    kit = {'styles': {}, 'themes': {}, 'aka': AKA}
    for name, (key, chars) in STYLES.items():
        fnt = font(key, chars.strip() or 'A')
        glyphs = {}
        for ch in chars:
            gid, adv = fnt.shape(ch)[0][:2]
            glyphs[ch] = [adv, fnt.path(gid) if ch != ' ' else '']
        kit['styles'][name] = {'upm': fnt.upm, 'glyphs': glyphs}
    for T in (DARK, LIGHT):
        th = {k: T[k] for k in THEME_KEYS}
        th['flash'] = '#ffffff' if T['name'] == 'dark' else INK
        th['dots'] = [[round(x, 1), y, round(r, 2)] for x, y, r in halftone_x(900 - 190, 900, 0, 420, 7, 1.5)]
        th['dots_op'] = .22 if T['name'] == 'dark' else .14
        kit['themes'][T['name']] = th
    out = HERE / 'data' / 'log-kit.json'
    out.write_text(json.dumps(kit, ensure_ascii=False, separators=(',', ':')))
    print(out, f'{out.stat().st_size / 1024:.0f} KB')

if __name__ == '__main__':
    main()
