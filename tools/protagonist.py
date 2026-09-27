#!/usr/bin/env python3
"""Prologue portrait (主人公) and the Arsenal (武器庫) inventory, dark and light twins.

The face is a two-ink manga print made by variants/face/print.py from his selfie (the photo itself stays out of the
repo); only the print and its alpha mask live in data/. Logos are Simple Icons (CC0) in data/icons.
Run: python3 protagonist.py
"""
import base64, math, random, re
from PIL import Image
from build_assets import *

ICON_DIR = HERE / 'data' / 'icons'

def b64(path, mime):
    return f'data:{mime};base64,' + base64.b64encode(path.read_bytes()).decode()

def icon_path(slug):
    return re.search(r' d="([^"]+)"', (ICON_DIR / f'{slug}.svg').read_text()).group(1)

# ------------------------------------------------------------------ prologue: the protagonist
NOW = [('BUILDING', 'SMM Radar, Telegram analytics, private beta'),
       ('SHIPPED', 'Flavor Tree for OneIdea 2026 × Efes'),
       ('STUDYING', 'Software Engineering at KBTU, final years'),
       ('OPEN TO', 'Internships · freelance backend · hackathons'),
       ('ALSO', 'SEO · public speaking, several years each')]
BACKDROP = 'sun'   # behind the photo: 'sun' (the hero's red sun on dark), 'dark' or 'red'; the photo's look is set in variants/face/print.py

def protagonist(T, backdrop=BACKDROP, fig=None, name='protagonist'):
    """a quiet portrait: the photo in a plain frame, the title and the NOW list; the hero keeps all the noise"""
    W, H = 900, 452; D = Doc(); dark = T['name'] == 'dark'
    fig = fig or HERE / 'data' / 'face-print.jpg'
    x0, y0, x1, y1 = 10, 10, 392, H - 10                                 # photo box
    pw, ph = Image.open(fig).size
    fw = 404; fh = fw * ph / pw; fx = x0 - 12; fy = y1 - fh + 2         # shoulders resting on the bottom edge
    hx, hy = fx + .453 * fw, fy + .366 * fh                             # centre of the head
    style = ('@keyframes rv{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}'
             + ''.join(f'.rv{i}{{animation:rv .7s cubic-bezier(.16,1,.3,1) {0.35 + i*0.08:.2f}s both}}' for i in range(9))
             + '@keyframes ph{from{opacity:0}to{opacity:1}}.ph{animation:ph 1.1s ease-out .05s both}'
             + '@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:.15}}.live{animation:blink 1.1s steps(1) infinite}')
    b = [f'<defs><clipPath id="pb"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}"/></clipPath>'
         f'<mask id="fm" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><image href="{b64(HERE / "data" / "face-alpha.png", "image/png")}" x="{fx}" y="{fy:.1f}" width="{fw}" height="{fh:.1f}"/></mask>'
         f'<linearGradient id="bd" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1f252d"/><stop offset="1" stop-color="{INK}"/></linearGradient>'
         f'<linearGradient id="rule" x1="0" x2="1"><stop offset="0" stop-color="{AKA}"/><stop offset="1" stop-color="{AKA}" stop-opacity="0"/></linearGradient></defs>',
         f'<rect width="{W}" height="{H}" fill="{T["panel"]}"/>',
         dots(halftone_x(W - 150, W, 0, H, 7, 1.3), T['tone'], .16 if dark else .1)]
    g = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{AKA if backdrop == "red" else "url(#bd)"}"/>']
    if backdrop == 'sun':
        g.append(f'<circle cx="{hx:.1f}" cy="{hy - 6:.1f}" r="148" fill="{AKA}"/>')
    g.append(f'<g class="ph"><image href="{b64(fig, "image/jpeg")}" x="{fx}" y="{fy:.1f}" width="{fw}" height="{fh:.1f}" mask="url(#fm)" preserveAspectRatio="none"/></g>')
    b.append(f'<g clip-path="url(#pb)">{"".join(g)}</g>')
    b.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="none" stroke="{T["line"] if dark else INK}" stroke-width="1.5" stroke-opacity="{1 if dark else .5}"/>')
    # a small straight seal, the way a print is signed
    sx, sy, ss = 858, 44, 34
    b.append(f'<g class="rv8"><rect x="{sx - ss/2}" y="{sy - ss/2}" width="{ss}" height="{ss}" rx="3" fill="{AKA}"/>'
             + D.text('侍', sx, sy + 8.5, 23, 'sans900', PAPER, anchor='middle') + '</g>')
    X = 440; VX = 548
    kw = D.measure('第零話', 14, 'sans900', 1)
    b.append('<g class="rv0">' + D.text('第零話', X, 64, 14, 'sans900', T['akatext'], ls=1)
             + D.text('PROLOGUE', X + kw + 14, 63, 11.5, 'mono700', T['akatext'], ls=3.2) + '</g>')
    b.append('<g class="rv1">' + D.text('Backend developer.', X - 1, 122, 34, 'sans900', T['text']) + '</g>')
    b.append('<g class="rv2">' + D.text('Python first.', X - 1, 162, 34, 'sans900', T['akatext']) + '</g>')
    b.append(f'<g class="rv3"><rect x="{X}" y="190" width="420" height="2" fill="url(#rule)"/></g>')
    b.append('<g class="rv3">' + D.text('NOW', X, 232, 12, 'mono700', T['text'], ls=4) + D.text('今', X + 48, 233, 14, 'sans900', T['akatext'])
             + f'<circle class="live" cx="{X + 76}" cy="228" r="4" fill="{T["hot"]}"/>' + '</g>')
    y = 268
    for i, (lab, val) in enumerate(NOW):
        assert D.measure(val, 14, 'sans500') < W - 18 - VX, (val, D.measure(val, 14, 'sans500'))
        b.append(f'<g class="rv{4 + min(i, 3)}">' + D.text(lab, X, y, 10.5, 'mono700', T['akatext'], ls=2.5)
                 + D.text(val, VX, y + .5, 14, 'sans500', T['text'], opacity=.94)
                 + f'<rect x="{X}" y="{y + 13}" width="{W - 18 - X}" height="1" fill="{T["line"]}"/>' + '</g>')
        y += 34
    b.append(frame(W, H, T))
    alt = ('Prologue: a portrait of Klim Kassymkhan. Backend developer, Python first. Now: '
           + '; '.join(f'{l.lower()} {v}' for l, v in NOW) + '.')
    write(name, T, D.svg(W, H, '\n'.join(b), alt, style))

# ------------------------------------------------------------------ arsenal
# (label, simple-icons slug or a drawn glyph, main stack)
ARSENAL = [
    ('01', '刀', 'LANGUAGES', [('PYTHON', 'python', 1), ('TYPESCRIPT', 'typescript', 0), ('JAVASCRIPT', 'javascript', 0),
                               ('C++', 'cplusplus', 0), ('JAVA', 'openjdk', 0), ('SQL', ':db', 0)]),
    ('02', '城', 'BACKEND', [('DJANGO', 'django', 1), ('DRF', ':drf', 1), ('FASTAPI', 'fastapi', 0),
                             ('POSTGRESQL', 'postgresql', 1), ('REDIS', 'redis', 0), ('SQLITE', 'sqlite', 0)]),
    ('03', '弓', 'FRONTEND', [('ANGULAR', 'angular', 0), ('REACT', 'react', 0), ('NEXT.JS', 'nextdotjs', 0),
                              ('VITE', 'vite', 0), ('TAILWIND', 'tailwindcss', 0)]),
    ('04', '忍', 'AUTOMATION', [('PLAYWRIGHT', 'playwright', 0), ('CAMOUFOX', ':fox', 0), ('CURL_CFFI', 'curl', 0),
                                ('AIOGRAM', 'telegram', 0), ('OPENCV', 'opencv', 0), ('CLAUDE API', 'claude', 0)]),
    ('05', '蔵', 'INFRA', [('DOCKER', 'docker', 0), ('GH ACTIONS', 'githubactions', 0), ('VERCEL', 'vercel', 0),
                           ('AZURE', 'microsoftazure', 0), ('CLOUDFLARE', 'cloudflare', 0), ('LINUX', 'linux', 0)]),
]
CURSOR = [(0, 0), (1, 0), (1, 1), (1, 3), (3, 0), (3, 3), (2, 0), (4, 0)]    # where the selector stops, in order

def arsenal(T):
    W = 900; D = Doc(); dark = T['name'] == 'dark'
    top, TH, RG = 22, 70, 12; GX0, GX1 = 214, 880; TW = 104; CG = (GX1 - GX0 - 6 * TW) / 5
    H = top + 5 * (TH + RG) - RG + 50
    tile_bg = INK if dark else '#ffffff'; ink = PAPER if dark else INK
    pos = lambda r, c: (GX0 + c * (TW + CG), top + r * (TH + RG))
    n = len(CURSOR); hold = 1.25; move = .28; dur = n * (hold + move)
    kf = []
    for i, (r, c) in enumerate(CURSOR):
        x, y = pos(r, c); x0c, y0c = pos(*CURSOR[0])
        t0 = i * (hold + move) / dur * 100; t1 = (i * (hold + move) + hold) / dur * 100
        kf.append(f'{t0:.2f}%,{t1:.2f}%{{transform:translate({x - x0c:.1f}px,{y - y0c:.1f}px)}}')
    kf.append(f'100%{{transform:translate(0px,0px)}}')
    style = ('@keyframes rv{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}'
             + ''.join(f'.t{i}{{animation:rv .5s cubic-bezier(.16,1,.3,1) {0.15 + i*0.035:.3f}s both}}' for i in range(40))
             + f'@keyframes cur{{{"".join(kf)}}}.cur{{animation:cur {dur:.2f}s cubic-bezier(.7,0,.2,1) 1.3s infinite both}}'
             + '@keyframes br{0%,100%{opacity:1}50%{opacity:.55}}.br{animation:br .9s ease-in-out infinite}'
             + '@keyframes cin{from{opacity:0}to{opacity:1}}.cin{animation:cin .3s ease-out 1.25s both}'   # the selector shows up once the tiles are in
             + '@keyframes gl{0%{transform:translateX(0)}40%,100%{transform:translateX(900px)}}.gl{animation:gl 5.5s cubic-bezier(.4,0,.2,1) 2s infinite}')
    b = [f'<rect width="{W}" height="{H}" fill="{T["panel"]}"/>',
         dots(halftone_x(W - 160, W, 0, H, 7, 1.4), T['tone'], .2 if dark else .12)]
    tiles_clip = []
    k = 0
    for r, (num, kanji, cat, items) in enumerate(ARSENAL):
        ry = top + r * (TH + RG)
        b.append(f'<g class="t{k}">' + tab(20, ry + 4, 38, 22, AKA) + D.text(num, 39, ry + 19.5, 11, 'mono700', PAPER, ls=1, anchor='middle')
                 + D.text(kanji, 86, ry + 25, 22, 'sans900', T['akatext'])
                 + D.text(cat, 21, ry + 50, 11.5, 'mono700', T['text'], ls=3)
                 + f'<rect x="20" y="{ry + 60}" width="{GX0 - 36}" height="1.5" fill="{T["line"]}"/>' + '</g>')
        k += 1
        for c, (label, slug, main) in enumerate(items):
            x, y = pos(r, c); cx = x + TW / 2
            tiles_clip.append(f'<rect x="{x:.1f}" y="{y}" width="{TW}" height="{TH}" rx="3"/>')
            g = [f'<rect x="{x:.1f}" y="{y}" width="{TW}" height="{TH}" rx="3" fill="{tile_bg}" stroke="{T["line"]}" stroke-width="1.2"/>']
            if main:
                g.append(f'<path d="M{x:.1f} {y + 3} Q{x:.1f} {y} {x + 3:.1f} {y} H{x + 18:.1f} L{x:.1f} {y + 18} Z" fill="{AKA}"/>')
            iy = y + 9; S = 26
            if slug == ':db':        # SQL: a drawn database drum
                g.append(f'<g fill="none" stroke="{ink}" stroke-width="2.2"><ellipse cx="{cx:.1f}" cy="{iy + 5}" rx="10" ry="4"/>'
                         f'<path d="M{cx - 10:.1f} {iy + 5} V{iy + 21} A10 4 0 0 0 {cx + 10:.1f} {iy + 21} V{iy + 5}"/>'
                         f'<path d="M{cx - 10:.1f} {iy + 13} A10 4 0 0 0 {cx + 10:.1f} {iy + 13}"/></g>')
            elif slug == ':drf':     # Django REST framework has no mark of its own: a code bracket badge
                g.append(f'<rect x="{cx - 17:.1f}" y="{iy + 2}" width="34" height="22" rx="4" fill="none" stroke="{ink}" stroke-width="2"/>'
                         + D.text('{ }', cx, iy + 18.5, 14, 'mono700', ink, anchor='middle'))
            elif slug == ':fox':     # Camoufox, a Firefox build for stealth scraping: the fox, in kanji
                g.append(D.text('狐', cx, iy + 23, 25, 'sans900', ink, anchor='middle'))
            else:
                g.append(f'<path d="{icon_path(slug)}" transform="translate({cx - S / 2:.1f} {iy}) scale({S / 24:.4f})" fill="{ink}"/>')
            assert D.measure(label, 10.5, 'mono600', 1.2) < TW - 8, label
            g.append(D.text(label, cx, y + TH - 11, 10.5, 'mono600', T['muted'] if not main else T['text'], ls=1.2, anchor='middle'))
            b.append(f'<g class="t{k}">' + ''.join(g) + '</g>'); k += 1
        for c in range(len(items), 6):   # rows with five pieces keep an open slot, like an unfilled inventory
            x, y = pos(r, c); cx = x + TW / 2
            b.append(f'<g class="t{k}"><rect x="{x + .6:.1f}" y="{y + .6}" width="{TW - 1.2}" height="{TH - 1.2}" rx="3" fill="none" stroke="{T["line"]}" stroke-width="1.2" stroke-dasharray="4 4"/>'
                     + D.text('空', cx, y + 34, 20, 'sans700', T['dim'], anchor='middle', opacity=.7)
                     + D.text('OPEN SLOT', cx, y + TH - 11, 10.5, 'mono600', T['dim'], ls=1.2, anchor='middle') + '</g>'); k += 1
    # glint sweeping over the tiles
    b.append(f'<defs><clipPath id="tc">{"".join(tiles_clip)}</clipPath><linearGradient id="glg" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
             f'<stop offset=".5" stop-color="#fff" stop-opacity="{.13 if dark else .5}"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>')
    b.append(f'<g clip-path="url(#tc)"><g class="gl"><rect x="-120" y="0" width="80" height="{H}" fill="url(#glg)" transform="skewX(-20)"/></g></g>')
    # the selector: a red wash on the tile and four brackets
    x, y = pos(*CURSOR[0]); p = 5; L = 14
    br = ''.join(f'<path d="M{bx} {by + sy * L} V{by} H{bx + sx * L}"/>' for bx, by, sx, sy in
                 ((x - p, y - p, 1, 1), (x + TW + p, y - p, -1, 1), (x - p, y + TH + p, 1, -1), (x + TW + p, y + TH + p, -1, -1)))
    b.append(f'<g class="cin"><g class="cur"><rect x="{x:.1f}" y="{y}" width="{TW}" height="{TH}" rx="3" fill="{AKA}" fill-opacity="{.2 if dark else .1}" stroke="{AKA}" stroke-width="1.6"/>'
             f'<g class="br" fill="none" stroke="{T["hot"]}" stroke-width="3" stroke-linecap="square">{br}</g></g></g>')
    fy = H - 20
    lab_w = D.measure('MAIN STACK', 10.5, 'mono700', 2.5)
    cnt = f'{sum(len(r[3]) for r in ARSENAL)} ITEMS'
    b.append(f'<path d="M{GX0} {fy + 2} H{GX0 + 13} L{GX0} {fy - 11} Z" fill="{AKA}"/>'
             + D.text('MAIN STACK', GX0 + 22, fy, 10.5, 'mono700', T['muted'], ls=2.5)
             + D.text('主力', GX0 + 34 + lab_w, fy + 1, 12, 'sans700', T['akatext'])
             + D.text('武器庫', GX1, fy + 1, 12, 'sans700', T['akatext'], anchor='end')
             + D.text(cnt, GX1 - D.measure('武器庫', 12, 'sans700') - 12, fy, 10.5, 'mono700', T['muted'], ls=2.5, anchor='end'))
    b.append(frame(W, H, T))
    alt = 'Arsenal. ' + ' '.join(f'{cat.title()}: ' + ', '.join(l.title() if l not in ('SQL', 'DRF', 'C++') else l for l, _, _ in items) + '.' for _, _, cat, items in ARSENAL)
    write('arsenal', T, D.svg(W, H, '\n'.join(b), alt, style))

if __name__ == '__main__':
    for T in (DARK, LIGHT):
        protagonist(T)
        arsenal(T)
