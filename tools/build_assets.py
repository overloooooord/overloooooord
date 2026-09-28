#!/usr/bin/env python3
"""Akai (赤) Anime profile: builds every SVG in ../assets, dark and paper-white light twins.

All text is typeset to vector paths by typeset.py (HarfBuzz + Noto Sans CJK JP / Source Code Pro),
so nothing depends on the viewer's fonts. Facts come from variants/FACTS.md. The contribution log is
not built here: GitHub Actions draws it daily with contrib_turtle.py (glyphs baked by log_kit.py).
Flavor Tree panels embed the shared screenshots from the repo root assets/shots/ as JPEG data.
Run: python3 build_assets.py
"""
import base64, io, json, math, random, subprocess, sys, datetime as dt
from pathlib import Path
from PIL import Image
from typeset import Doc, f2

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'assets'
SHOTS = HERE.parent / 'assets' / 'shots'

# dark neutrals are GitHub's own (canvas #0d1117, overlay #161b22, border #30363d) so the panels sit in the page, not on it
INK = '#0d1117'; INK2 = '#161b22'; BLOOD = '#30363d'; WINE = '#7a0a1a'
AKA = '#c8102e'; SHU = '#ef454a'; NEON = '#ff2a2a'; PAPER = '#f3ede4'

DARK = dict(name='dark', bg=INK, panel=INK2, text=PAPER, muted='#9198a1', dim='#6e7681', line=BLOOD,
            frame=PAPER, frame_op=.55, aka=AKA, akatext=SHU, hot=NEON, wine=WINE, wine_op=.35,
            tone=AKA, cell=['#151b23', '#4a0d17', '#7a0a1a', '#c8102e', '#ff2a2a'])
LIGHT = dict(name='light', bg=PAPER, panel=PAPER, text=INK, muted='#5c5459', dim='#857b75', line='#d9cbbd',
             frame=INK, frame_op=1, aka=AKA, akatext='#a50d25', hot=AKA, wine=AKA, wine_op=.13,
             tone=INK, cell=['#e4d9cc', '#f2b3bc', '#e2717e', '#c8102e', '#6e0a18'])

def write(name, T, content):
    fn = name + ('-light' if T['name'] == 'light' else '') + '.svg'
    (OUT / fn).write_text(content)
    print(f'{fn:30s} {len(content.encode())/1024:7.1f} KB')

def frame(W, H, T, inset=.75, sw=1.5):
    return (f'<rect x="{inset}" y="{inset}" width="{W-2*inset}" height="{H-2*inset}" fill="none" '
            f'stroke="{T["frame"]}" stroke-opacity="{T["frame_op"]}" stroke-width="{sw}"/>')

def tab(x, y, w, h, fill):
    return f'<path d="M{x} {y} H{x+w} L{x+w+h/4:.1f} {y+h/2:.1f} L{x+w} {y+h} H{x} Z" fill="{fill}"/>'

def dots(pts, fill, op=1):
    c = ''.join(f'<circle cx="{f2(x)}" cy="{f2(y)}" r="{f2(r)}"/>' for x, y, r in pts)
    return f'<g fill="{fill}" opacity="{op}">{c}</g>'

def halftone_x(x0, x1, y0, y1, step, rmax, rising=True):
    """dots that grow towards x1 (rising) or x0"""
    pts = []
    for i, x in enumerate(range(int(x0), int(x1), step)):
        t = (x - x0) / (x1 - x0)
        if not rising: t = 1 - t
        r = rmax * t ** 1.4
        if r < .35: continue
        for j, y in enumerate(range(int(y0), int(y1), step)):
            pts.append((x + (step / 2 if j % 2 else 0), y, r))
    return pts

def halftone_ring(cx, cy, r0, spread, x0, x1, y0, y1, step, rmax, avoid=None):
    """halftone falloff around a disc: largest dots at the rim, fading to nothing at r0 + spread"""
    pts = []
    for j, y in enumerate(range(int(y0), int(y1), step)):
        for x in range(int(x0), int(x1), step):
            xx = x + (step / 2 if j % 2 else 0)
            d = math.hypot(xx - cx, y - cy)
            if d < r0 + 3: continue
            t = (d - r0) / spread
            if t >= 1: continue
            r = rmax * (1 - t) ** 1.5
            if avoid: r *= avoid(xx, y)
            if r >= .4: pts.append((xx, y, r))
    return pts

# ------------------------------------------------------------------ katana illustrations live in katana.py
from katana import Katana, GOLD

LANGS = 'Python · TypeScript · JavaScript · C++ · Java · SQL'
STACK = 'Django · DRF · FastAPI · Angular · React · aiogram · Playwright'

def taper_slash(x1, y1, x2, y2, cls, widths=((1.6, 0.0, 1.0), (3.4, 0.14, 0.86), (5.6, 0.3, 0.7))):
    """a tapered slash drawn as stacked strokes of shrinking length; each layer draws in on its own delay"""
    out = []
    for w, a, b in widths:
        ax, ay = x1 + (x2 - x1) * a, y1 + (y2 - y1) * a
        bx, by = x1 + (x2 - x1) * b, y1 + (y2 - y1) * b
        out.append(f'<path class="{cls}{int(a*100)}" d="M{ax:.1f} {ay:.1f} L{bx:.1f} {by:.1f}" pathLength="1" stroke-width="{w}" stroke-linecap="round"/>')
    return ''.join(out)

# ------------------------------------------------------------------ hero poster
def hero(T):
    W, H = 900, 344; SX, SY, SR = 668, 158, 118; rnd = random.Random(7); D = Doc(); dark = T['name'] == 'dark'
    th = math.radians(-12); u = (math.cos(th), math.sin(th)); n = (-u[1], u[0])          # blade direction and its normal
    off = 55; Q = (SX + off * n[0], SY + off * n[1]); half = math.sqrt(SR * SR - off * off)
    k = Katana(430, 'hk', ito='red', hamon='notare', hi=True, red_glow=.14, rim_light=PAPER if dark else None)
    t0 = k.x_t + 4 + half + 6
    P0 = (Q[0] - t0 * u[0], Q[1] - t0 * u[1])
    kdefs, kbody = k.svg(glint_class='kgl')
    gap = 7.2
    sag = k.S * k.L / 4 * 0.9                                # the blade bows below its chord; centre the cut on the steel
    Qc = (Q[0] + sag * n[0], Q[1] + sag * n[1])
    cut_a = (Q[0] - 150 * u[0] + 6 * n[0], Q[1] - 150 * u[1] + 6 * n[1]); cut_b = (Q[0] + 170 * u[0] + 6 * n[0], Q[1] + 170 * u[1] + 6 * n[1])
    T_SL = 2.6                                              # load sequence length, s
    style = ('@keyframes spark{0%{transform:translateX(0)}100%{transform:translateX(330px)}}.spark{animation:spark 2.8s ease-in-out infinite alternate}'
             '@keyframes fall{0%{transform:translate(0,0) rotate(0deg);opacity:0}8%{opacity:.8}92%{opacity:.8}100%{transform:translate(-150px,300px) rotate(320deg);opacity:0}}'
             + ''.join(f'.p{i}{{animation:fall {7+i*1.3:.1f}s linear {i*1.7:.1f}s infinite}}' for i in range(6))
             + f'@keyframes shimmer{{0%,100%{{opacity:{.18 if dark else .22}}}50%{{opacity:{.5 if dark else .55}}}}}'
             + ''.join(f'.l{i}{{animation:shimmer {3+(i%4)*.9:.1f}s ease-in-out {i*.37:.2f}s infinite}}' for i in range(8))
             # reveal, the way rdrightnow.com brings its hero in: rise 14px and fade, 70 ms apart
             + '@keyframes rv{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}'
             + ''.join(f'.rv{i}{{animation:rv .7s cubic-bezier(.16,1,.3,1) {0.05 + i*0.07:.2f}s both}}' for i in range(7))
             # the cut: a slash draws along the blade line, then the sun parts along it and the steel shows in the gap
             + ''.join(f'@keyframes sl{a}{{0%,{int(28+a*0.12)}%{{stroke-dashoffset:1}}{int(36+a*0.12)}%,100%{{stroke-dashoffset:0}}}}.sl{a}{{stroke-dasharray:1;animation:sl{a} {T_SL}s linear both}}' for a in (0, 14, 30))
             + '@keyframes slf{0%,48%{opacity:1}70%,100%{opacity:.32}}.slf{animation:slf 2.6s ease-out both}'
             + f'@keyframes su{{0%,40%{{transform:translate(0,0)}}58%,100%{{transform:translate({-n[0]*gap:.2f}px,{-n[1]*gap:.2f}px)}}}}.su{{animation:su {T_SL}s cubic-bezier(.2,.8,.2,1) both}}'
             + f'@keyframes sd{{0%,40%{{transform:translate(0,0)}}62%,100%{{transform:translate({n[0]*gap + u[0]*12:.2f}px,{n[1]*gap + u[1]*12:.2f}px)}}}}.sd{{animation:sd {T_SL}s cubic-bezier(.2,.8,.2,1) both}}'
             + '@keyframes kgl{0%{transform:translateX(-60px)}35%,100%{transform:translateX(330px)}}.kgl{animation:kgl 4.6s cubic-bezier(.3,0,.2,1) 1.4s infinite}')
    far = 1400
    def halfplane(sign):
        a = (Qc[0] - far * u[0], Qc[1] - far * u[1]); b = (Qc[0] + far * u[0], Qc[1] + far * u[1])
        c = (b[0] + sign * far * n[0], b[1] + sign * far * n[1]); d = (a[0] + sign * far * n[0], a[1] + sign * far * n[1])
        return ' '.join(f'{x:.1f},{y:.1f}' for x, y in (a, b, c, d))
    b = [f'<defs><linearGradient id="rule" x1="0" x2="1"><stop offset="0" stop-color="{T["aka"]}"/><stop offset="1" stop-color="{T["aka"]}" stop-opacity="0"/></linearGradient>'
         f'<clipPath id="fr"><rect width="{W}" height="{H}"/></clipPath><clipPath id="hu"><polygon points="{halfplane(-1)}"/></clipPath><clipPath id="hd"><polygon points="{halfplane(1)}"/></clipPath>'
         f'<filter id="glow" x="-10%" y="-200%" width="120%" height="500%"><feGaussianBlur stdDeviation="2.4"/></filter>{kdefs}</defs>',
         f'<rect width="{W}" height="{H}" fill="{T["bg"]}"/>', '<g clip-path="url(#fr)">']
    fade_left = lambda x, y: max(0, min(1, (x - 470) / 90))
    b.append(dots(halftone_ring(SX, SY, SR, 175, 440, 900, 0, H + 4, 8, 2.8, fade_left), T['aka'], .55 if dark else .5))
    tone = [(x, y, r) for x, y, r in ((x + (4 if (y // 7) % 2 else 0), y, 1.5 * ((y - 238) / 106) ** 1.3)
            for y in range(238, H + 2, 7) for x in range(0, 430, 7)) if r > .35 and x < 430 - (y - 238) * .5]
    b.append(dots(tone, WINE if dark else INK, .5 if dark else .12))
    lines = []
    for i in range(64):
        ang = math.radians(rnd.uniform(96, 264))
        r1 = SR + rnd.uniform(14, 60); r2 = r1 + rnd.uniform(70, 420)
        x1, y1 = SX + r1 * math.cos(ang), SY + r1 * math.sin(ang)
        x2, y2 = SX + r2 * math.cos(ang), SY + r2 * math.sin(ang)
        if any(40 <= x1 + (x2 - x1) * t <= 600 and 30 <= y1 + (y2 - y1) * t <= 62 for t in (0, .25, .5, .75, 1)):
            continue
        if any(40 <= x1 + (x2 - x1) * t <= 640 and 282 <= y1 + (y2 - y1) * t <= H for t in (0, .25, .5, .75, 1)):
            continue
        lines.append(f'<line class="l{i%8}" x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke-width="{rnd.uniform(.7,2.2):.1f}"/>')
    b.append(f'<g stroke="{T["aka"]}" stroke-linecap="round">{"".join(lines)}</g>')
    # the sword sits behind the sun: handle and tip outside, the blade hidden until the cut opens
    b.append(f'<g transform="translate({P0[0]:.1f} {P0[1]:.1f}) rotate({math.degrees(th) + k.level():.2f})">{kbody}</g>')
    sun = f'<circle cx="{SX}" cy="{SY}" r="{SR}" fill="{T["aka"]}"/>'
    b.append(f'<g class="su" transform="translate({-n[0]*gap:.2f} {-n[1]*gap:.2f})"><g clip-path="url(#hu)">{sun}</g></g>')
    b.append(f'<g class="sd" transform="translate({n[0]*gap + u[0]*12:.2f} {n[1]*gap + u[1]*12:.2f})"><g clip-path="url(#hd)">{sun}</g></g>')
    sl = taper_slash(*cut_a, *cut_b, 'sl')
    b.append(f'<g class="slf" fill="none"><g stroke="{T["hot"]}" filter="url(#glow)" opacity=".9">{sl}</g><g stroke="{PAPER if dark else "#ffffff"}">{sl}</g></g>')
    kx, ky, ks = 54, 214, 150
    b.append('<g class="rv1">' + D.text('エラリ', kx, ky, ks, 'sans900', T['bg'], ls=-6, extra=f' stroke="{T["bg"]}" stroke-width="{14/ks*1000:.0f}" stroke-linejoin="round"')
             + D.text('エラリ', kx + 7, ky + 7, ks, 'sans900', T['aka'], ls=-6) + D.text('エラリ', kx, ky, ks, 'sans900', T['text'], ls=-6) + '</g>')
    b.append('<g class="rv0">' + D.text('AKAI · BACKEND DEVELOPER · KBTU · ALMATY, KZ', 56, 52, 11.5, 'mono700', T['akatext'], ls=4) + '</g>')
    b.append('<g class="rv2">' + D.text('YERALY ABUTALIFULY', 56, 262, 27, 'sans900', T['text'], ls=3) + '</g>')
    b.append(f'<g class="rv3"><rect x="56" y="278" width="440" height="2" fill="url(#rule)"/><rect class="spark" x="56" y="278" width="70" height="2" fill="{T["text"]}" opacity=".9"/></g>')
    lw = max(D.measure(l, 10.5, 'mono700', 3) for l in ('LANG', 'STACK'))
    for i, (lab, txt, y) in enumerate((('LANG', LANGS, 304), ('STACK', STACK, 327))):
        b.append(f'<g class="rv{4+i}">' + D.text(lab, 57, y, 10.5, 'mono700', T['akatext'], ls=3, skew=-12)
                 + f'<rect x="{57 + lw + 8:.1f}" y="{y-4.5}" width="10" height="1.4" fill="{T["aka"]}"/>'
                 + D.text(txt, 57 + lw + 26, y, 13, 'sans500', T['text'], opacity=.94) + '</g>')
    assert 57 + lw + 26 + D.measure(STACK, 13, 'sans500') < 820, 'stack line too long'
    b.append('<g class="rv6">' + D.vtext('開発者', 862, 34, 26, 'sans700', T['text'], gap=6) + D.vtext('バックエンド', 836, 40, 13, 'sans700', T['akatext'], gap=3)
             + f'<rect x="838" y="254" width="42" height="42" fill="{T["aka"]}"/>'
             + D.text('赤', 859, 287, 30, 'sans900', PAPER, anchor='middle') + D.text('VOL.03', 880, 322, 10, 'mono500', T['dim'], ls=2, anchor='end') + '</g>')
    petal = 'M0,-7 C4.5,-4.5 5.5,2.5 0,7 C-5.5,2.5 -4.5,-4.5 0,-7 Z'
    for i, (px, py, sc) in enumerate([(560, -10, 1), (700, -20, .8), (820, -6, 1.1), (640, -30, .7), (760, -12, .9), (880, -24, .75)]):
        b.append(f'<g class="p{i}"><path d="{petal}" transform="translate({px} {py}) scale({sc})" fill="{T["akatext"] if dark else AKA}"/></g>')
    b.append('</g>')
    b.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" fill="none" stroke="{T["line"] if dark else INK}" stroke-width="{1 if dark else 1.5}"/>')
    alt = (f'Yeraly Abutalifuly, エラリ, backend developer, KBTU, Almaty. A katana passes behind a red sun and cuts it in two. '
           f'Languages: {LANGS}. Frameworks: {STACK}.')
    write('hero', T, D.svg(W, H, '\n'.join(b), alt, style))

# ------------------------------------------------------------------ status ribbon (light: a red obi band)
TICKER = ['OPEN TO INTERNSHIPS', 'FREELANCE BACKEND WORK', 'HACKATHON TEAMS', 'ALMATY OR REMOTE',
          'FASTEST REPLY ON TELEGRAM @DREAMDRAINER', 'DJANGO · FASTAPI · ANGULAR · PLAYWRIGHT']

def ribbon(T):
    """status band with a running ticker, the same device rdrightnow.com uses for its stack line"""
    W, H = 900, 44; D = Doc(); dark = T['name'] == 'dark'
    bg, tabc, tabt, txt, dot, rec = ((T['panel'], AKA, PAPER, T['text'], NEON, SHU) if dark
                                     else (AKA, INK, PAPER, PAPER, PAPER, PAPER))
    X0, X1 = 150, 728
    items = []; x = 0
    for it in TICKER:
        items.append(D.text(it, x, 27, 11.5, 'mono500', txt, ls=2.2, opacity=.92))
        x += D.measure(it, 11.5, 'mono500', 2.2) + 20
        items.append(f'<circle cx="{x:.1f}" cy="22.5" r="2.2" fill="{dot if dark else PAPER}" opacity=".8"/>')
        x += 22
    wr = x
    speed = 38.0
    style = ('@keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}.dot{animation:pulse 2.4s ease-in-out infinite}'
             '@keyframes ring{0%{transform:scale(.6);opacity:.9}100%{transform:scale(2.6);opacity:0}}'
             '.ring{transform-box:fill-box;transform-origin:center;animation:ring 2.4s ease-out infinite}'
             f'@keyframes tick{{from{{transform:translateX(0)}}to{{transform:translateX({-wr:.1f}px)}}}}.tick{{animation:tick {wr / speed:.1f}s linear infinite}}')
    row = ''.join(items)
    b = [f'<defs><linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".08" stop-color="#fff"/>'
         f'<stop offset=".92" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
         f'<mask id="mk"><rect x="{X0}" y="0" width="{X1 - X0}" height="{H}" fill="url(#fade)"/></mask></defs>',
         f'<rect width="{W}" height="{H}" fill="{bg}"/>',
         f'<g mask="url(#mk)"><g transform="translate({X0 + 14} 0)"><g class="tick">{row}<g transform="translate({wr:.1f} 0)">{row}</g></g></g></g>',
         tab(0, 0, 128, H, tabc),
         D.text('STATUS', 60, 27, 12, 'mono700', tabt, ls=4, anchor='middle'),
         f'<circle class="ring" cx="752" cy="22" r="4" fill="none" stroke="{dot}" stroke-width="1.2"/>',
         f'<circle class="dot" cx="752" cy="22" r="4" fill="{dot}"/>',
         D.text('RECRUITING', 874, 27, 11, 'mono700', rec, ls=3, anchor='end')]
    if dark: b.append(f'<rect x="0" y="{H-1}" width="{W}" height="1" fill="{BLOOD}"/>')
    write('ribbon-status', T, D.svg(W, H, '\n'.join(b), 'Status: ' + ', '.join(t.lower() for t in TICKER), style))

# ------------------------------------------------------------------ chapter strips
def chapter(T, name, kanji, title, sub, label, fold=False):
    """fold: the strip is the clickable summary of a collapsed <details>, so it carries an expand button on the right"""
    W, H = 900, 56; D = Doc(); dark = T['name'] == 'dark'
    style = ('@keyframes cut{0%{transform:translateX(-160px)}100%{transform:translateX(1100px)}}.cut{animation:cut 1.1s cubic-bezier(.3,0,.2,1) .2s both;opacity:.9}'
             '@keyframes bob{0%,60%,100%{transform:translateY(0)}30%{transform:translateY(3px)}}.bob{animation:bob 2.4s ease-in-out 1.4s infinite}')
    sub_x = 832 if fold else 872
    b = [f'<rect width="{W}" height="{H}" fill="{T["panel"]}"/>',
         f'<defs><linearGradient id="cg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{AKA}" stop-opacity="0"/><stop offset=".5" stop-color="{T["hot"]}"/><stop offset="1" stop-color="{AKA}" stop-opacity="0"/></linearGradient></defs>',
         f'<g transform="skewX(-28)"><rect class="cut" x="0" y="-6" width="1.6" height="68" fill="url(#cg)"/></g>',
         dots(halftone_x(600, 900, 3, 56, 7, 1.6), T['tone'], .3 if dark else .2),
         tab(0, 0, 124, H, AKA), D.text(kanji, 62, 35, 19, 'sans900', PAPER, ls=1, anchor='middle'),
         D.text(title, 160, 35, 16, 'sans900', T['text'], ls=5)]
    tw = 160 + D.measure(title, 16, 'sans900', 5)
    ls = 2
    while sub_x - D.measure(sub, 11.5, 'mono500', ls) < tw + 28 and ls > 0: ls -= .25
    b.append(D.text(sub, sub_x, 34, 11.5, 'mono500', T['muted'], ls=ls, anchor='end'))
    if fold:
        b.append(f'<rect x="847.5" y="13.5" width="33" height="29" rx="3" fill="{T["bg"]}" stroke="{T["line"] if dark else INK}" stroke-width="1.5" stroke-opacity="{1 if dark else .4}"/>'
                 f'<path class="bob" d="M857 25 L864 32 L871 25" fill="none" stroke="{T["akatext"]}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>')
    b.append(f'<rect x="0" y="{H-2}" width="{W}" height="2" fill="{AKA}"/>')
    b.append(f'<rect x="0" y="0" width="{W}" height="1" fill="{T["text"]}" opacity="{.18 if dark else .9}"/>')
    write(f'chapter-{name}', T, D.svg(W, H, '\n'.join(b), label, style))

# ------------------------------------------------------------------ flavor tree numbers
def flavor_stats(T):
    W, H = 900, 108; D = Doc(); dark = T['name'] == 'dark'
    b = [f'<rect width="{W}" height="{H}" fill="{T["panel"]}"/>',
         D.text('麦', 886, 102, 110, 'sans900', T['wine'], anchor='end', opacity=T['wine_op'] * .7)]
    tiles = [('412', 'drinks, each with a', 'Top · Heart · Base pyramid'), ('50+', 'dishes across', 'six cuisines'),
             ('4', 'pairing types: complement,', 'contrast, cleanse, bridge'), ('150+', 'backend tests, plus a', 'business plan in the repo')]
    tw = W / 4
    for i, (n, l1, l2) in enumerate(tiles):
        x = i * tw
        if i: b.append(f'<line x1="{x}" y1="16" x2="{x}" y2="{H-16}" stroke="{T["line"]}" stroke-width="1.5"/>')
        b.append(f'<rect x="{x+24}" y="18" width="26" height="3" fill="{AKA}"/>')
        b.append(D.text(n, x + 23, 58, 34, 'sans900', T['text']))
        b.append(D.text(l1, x + 24, 77, 11, 'mono500', T['muted']))
        b.append(D.text(l2, x + 24, 92, 11, 'mono500', T['muted']))
    b.append(frame(W, H, T))
    write('flavor-stats', T, D.svg(W, H, '\n'.join(b), 'Flavor Tree: 412 drinks, 50+ dishes, 4 pairing types, 150+ backend tests'))

# ------------------------------------------------------------------ Flavor Tree manga pages (one file for both themes)
RED_STOPS = [(0, (34, 4, 10)), (.32, (122, 10, 26)), (.58, (200, 16, 46)), (.82, (239, 69, 74)), (1, (250, 196, 196))]

def two_ink(im):
    """reprint a screenshot in two inks like the Kuniyoshi panel: grey ramp from INK to PAPER, anything saturated goes red"""
    import numpy as np
    hexrgb = lambda h: np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], float)
    ink, paper = hexrgb(INK), hexrgb(PAPER)
    a = np.asarray(im.convert('RGB')).astype(float)
    L = (a @ np.array([.299, .587, .114])) / 255
    C = (a.max(-1) - a.min(-1)) / 255
    base = ink + (paper - ink) * (np.clip((L - .06) / .9, 0, 1) ** 1.08)[..., None]
    t = np.clip((C - .10) / .24, 0, 1); w = (t * t * (3 - 2 * t))[..., None]
    red = np.stack([np.interp(L, [s for s, _ in RED_STOPS], [c[k] for _, c in RED_STOPS]) for k in range(3)], -1)
    return Image.fromarray((base * (1 - w) + red * w).clip(0, 255).astype(np.uint8))

def jpeg_data(path, width=None, crop=None, q=86, tone=False):
    im = Image.open(path).convert('RGB')
    if crop: im = im.crop(crop)
    if width and im.width != width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    if tone: im = two_ink(im)
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=q, optimize=True, progressive=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode(), im.size

def ink_frame(d, ink=5, paper=2.5):
    """theme-neutral manga panel border: ink outside (reads on white), paper inside (reads on dark)"""
    return (f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{ink+paper*2}" stroke-linejoin="miter"/>'
            f'<path d="{d}" fill="none" stroke="{PAPER}" stroke-width="{paper}" stroke-linejoin="miter"/>')

def caption_box(D, x, y, lines, size=11.5, fkey='mono600', pad=9, anchor='start'):
    w = max(D.measure(t, size, fkey, 1) for t in lines) + 2 * pad
    h = len(lines) * (size + 5) + 2 * pad - 5
    if anchor == 'end': x -= w
    out = [f'<rect x="{f2(x)}" y="{f2(y)}" width="{f2(w)}" height="{f2(h)}" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>']
    for i, t in enumerate(lines):
        out.append(D.text(t, x + pad, y + pad + size * .8 + i * (size + 5), size, fkey, INK, ls=1))
    return ''.join(out)

def kanji_tab(D, x, y, kanji, size=20, fill=AKA, color=PAPER):
    w = D.measure(kanji, size, 'sans900', 2) + 26
    return (f'<path d="M{x} {y} H{x+w+10} L{x+w} {y+size+16} H{x-10} Z" fill="{fill}" stroke="{INK}" stroke-width="2"/>'
            + D.text(kanji, x + w / 2, y + size + 3, size, 'sans900', color, ls=2, anchor='middle')), w

def flavor_pages():
    # page A: the championship build, bottom edge slants up to the right
    W, H = 900, 588; D = Doc()
    src, (iw, ih) = jpeg_data(SHOTS / 'flavor-tree-home.jpg', 1200, q=84, tone=True)
    x0, y0, x1 = 10, 34, 890; sh = (x1 - x0) / iw * ih
    yb_l, yb_r = y0 + sh - 4, y0 + sh - 26
    d = f'M{x0} {y0} H{x1} V{yb_r:.1f} L{x0} {yb_l:.1f} Z'
    b = [f'<defs><clipPath id="a"><path d="{d}"/></clipPath></defs>',
         f'<image href="{src}" x="{x0}" y="{y0}" width="{x1-x0}" height="{sh:.1f}" clip-path="url(#a)" preserveAspectRatio="xMidYMid slice"/>',
         ink_frame(d)]
    t, tw = kanji_tab(D, 26, 8, '本番')
    b.append(t)
    b.append(caption_box(D, 26 + tw + 22, 12, ['PRODUCTION BUILD · ONEIDEA 2026 × EFES KAZAKHSTAN']))
    msrc, (mw, mh) = jpeg_data(SHOTS / 'flavor-tree-home-mobile.jpg', 390, q=88, tone=True)
    pcx, pcy, rot = 786, 392, -6                                    # the phone overlaps the right edge and the bottom
    b.insert(0, '<defs><clipPath id="scr"><rect x="-73" y="-158" width="146" height="316" rx="17"/></clipPath>'
             '<filter id="sh" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="9"/></filter></defs>')
    b.append(f'<g transform="translate({pcx + 10} {pcy + 14}) rotate({rot})"><rect x="-84" y="-170" width="168" height="340" rx="26" fill="{INK}" opacity=".55" filter="url(#sh)"/></g>')
    b.append(f'<g transform="translate({pcx} {pcy}) rotate({rot})">'
             f'<rect x="-84" y="-170" width="168" height="340" rx="26" fill="{INK}" stroke="{PAPER}" stroke-width="2.5"/>'
             f'<image href="{msrc}" x="-73" y="-158" width="146" height="{146*mh/mw:.1f}" clip-path="url(#scr)" preserveAspectRatio="xMidYMin slice"/>'
             f'<rect x="-22" y="-152" width="44" height="11" rx="5.5" fill="{INK}"/></g>')
    t, tw = kanji_tab(D, pcx - 66, pcy - 206, 'スマホ', size=16, fill=INK)
    b.append(t)
    b.append(caption_box(D, 26, yb_l - 52, ['flavor-tree-frontend.vercel.app'], 12.5, 'mono700'))
    write_neutral('ft-page-champ', D.svg(W, H, '\n'.join(b), 'Flavor Tree home on desktop and on a phone: what will you choose today, 14 Efes KZ beers, flavor pyramid, sommelier bot, one search box for the dish on your table'))

def write_neutral(name, content):
    (OUT / f'{name}.svg').write_text(content)
    print(f'{name + ".svg":30s} {len(content.encode())/1024:7.1f} KB')

# ------------------------------------------------------------------ side quest panels
QUESTS = [
    ('invision', '02', 'InVision U', 'DECENTRATHON 5.0 · TEAM OF 3', '選',
     'AI scoring for the inDrive youth grant: essay NLP, XGBoost + SHAP explanations, a fairness audit.',
     'DJANGO / DRF · POSTGRESQL · AIOGRAM · XGBOOST', 'InVision U, Decentrathon 5.0 AI inDrive track, a team of three with Ilyas Aitkhozha and Denis: AI scoring for the inDrive youth grant with essay NLP, XGBoost and SHAP explanations and a fairness audit. Full source with backend and ML at commit 3c30480. Django REST, PostgreSQL, aiogram.'),
    ('igtg', '03', 'igtg · Instagram publisher', 'OWN TOOL · 251 TESTS', '発',
     'Telegram bot that queues and publishes reels, carousels and stories to my own Instagram accounts.',
     'AIOGRAM 3 · INSTAGRAPI · GRAPH API · SQLITE', 'igtg, own tool, 251 tests. Telegram bot on aiogram 3 that publishes reels, photos, carousels and stories to my own Instagram accounts. Scheduling queue in SQLite, three swappable backends: private API, Graph API, fake for tests.'),
]
QW, QH, QGAP = 440, 170, 12  # QGAP: transparent strip under each card = row gutter

def quest_card(T, key, num, title, stamp, kanji, body, tech, alt, side, lean):
    """side: left/right card of a row. lean: +1 gutter leans right at the top, -1 leans left."""
    D = Doc(); dark = T['name'] == 'dark'; H = QH
    s, g1, g2 = 14, 6, 14
    if side == 'left':
        xt, xb = (QW - g1, QW - g1 - s) if lean > 0 else (QW - g1 - s, QW - g1)
        poly = f'M0 0 H{xt} L{xb} {H} H0 Z'; xin = 22; xmax = min(xt, xb) - 22
    else:
        xt, xb = (g2, g2 - s) if lean > 0 else (g2 - s, g2)
        poly = f'M{xt} 0 H{QW} V{H} H{xb} Z'; xin = max(xt, xb) + 20; xmax = QW - 22
    b = [f'<defs><clipPath id="c"><path d="{poly}"/></clipPath></defs>', '<g clip-path="url(#c)">',
         f'<rect width="{QW}" height="{H}" fill="{T["panel"]}"/>',
         dots(halftone_x(QW - 170, QW, 0, H, 6, 1.3), T['tone'], .22 if dark else .14),
         D.text(kanji, QW - 16 if side == 'right' else QW - 32, H - 14, 120, 'sans900', T['wine'], anchor='end', opacity=T['wine_op']),
         '</g>',
         tab(0 if side == 'left' else xt, 0, 46, 28, AKA),
         D.text(num, (0 if side == 'left' else xt) + 23, 19, 11, 'mono700', PAPER, ls=2, anchor='middle'),
         D.text(stamp, xmax, 19, 11, 'mono700', T['akatext'], ls=2.5, anchor='end'),
         D.text(title, xin, 62, 21, 'sans900', T['text'], ls=-.2)]
    lines = D.wrap(body, 13.5, 'sans400', xmax - xin)
    y = 88
    for ln in lines:
        b.append(D.text(ln, xin, y, 13.5, 'sans400', T['text'], opacity=.84)); y += 19.5
    b.append(f'<rect x="{xin}" y="{H-40}" width="28" height="2.5" fill="{AKA}"/>')
    b.append(D.text(tech, xin, H - 18, 11, 'mono500', T['muted'], ls=1.5))
    b.append(f'<path d="{poly}" fill="none" stroke="{T["frame"]}" stroke-opacity="{T["frame_op"]}" stroke-width="2"/>')
    if len(lines) > 2: raise SystemExit(f'{key}: body needs {len(lines)} lines')
    write(f'quest-{key}', T, D.svg(QW, H + QGAP, '\n'.join(b), alt))

def quest_smm(T):
    W, H = 900, 204; D = Doc(); dark = T['name'] == 'dark'
    RX, RY, RR = 752, 96, 78
    style = (f'@keyframes sweep{{to{{transform:rotate(360deg)}}}}.sw{{transform-origin:{RX}px {RY}px;animation:sweep 4s linear infinite}}'
             '@keyframes blip{0%,100%{opacity:.25}12%{opacity:1}40%{opacity:.4}}'
             + ''.join(f'.b{i}{{animation:blip 4s ease-out {i*0.4:.1f}s infinite}}' for i in range(10)))
    b = [f'<defs><linearGradient id="sg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{AKA}" stop-opacity="0"/><stop offset="1" stop-color="{T["hot"]}" stop-opacity=".55"/></linearGradient>'
         f'<clipPath id="rc"><circle cx="{RX}" cy="{RY}" r="{RR}"/></clipPath></defs>',
         f'<rect width="{W}" height="{H}" fill="{T["panel"]}"/>',
         dots(halftone_ring(RX, RY, RR, 110, 560, 900, 0, H, 7, 2.1), T['tone'], .3 if dark else .16),
         D.text('電波', 896, H - 12, 118, 'sans900', T['wine'], anchor='end', opacity=T['wine_op'] * .8)]
    # radar
    b.append(f'<circle cx="{RX}" cy="{RY}" r="{RR}" fill="{INK if dark else PAPER}" stroke="{AKA}" stroke-width="2"/>')
    for r in (RR * .33, RR * .66):
        b.append(f'<circle cx="{RX}" cy="{RY}" r="{r:.0f}" fill="none" stroke="{AKA}" stroke-opacity=".45"/>')
    b.append(f'<path d="M{RX-RR} {RY} H{RX+RR} M{RX} {RY-RR} V{RY+RR}" stroke="{AKA}" stroke-opacity=".35"/>')
    wedge = f'M{RX} {RY} L{RX+RR} {RY} A{RR} {RR} 0 0 0 {RX+RR*math.cos(math.radians(-50)):.1f} {RY+RR*math.sin(math.radians(-50)):.1f} Z'
    b.append(f'<g clip-path="url(#rc)"><g class="sw"><path d="{wedge}" fill="url(#sg)"/><line x1="{RX}" y1="{RY}" x2="{RX+RR}" y2="{RY}" stroke="{T["hot"]}" stroke-width="1.5"/></g></g>')
    rnd = random.Random(5)
    for i in range(10):  # up to 10 public channels per client
        a = math.radians(i * 36 + rnd.uniform(-12, 12)); r = rnd.uniform(.25, .88) * RR
        b.append(f'<circle class="b{i}" cx="{RX + r*math.cos(a):.1f}" cy="{RY + r*math.sin(a):.1f}" r="3.4" fill="{T["hot"]}"/>')
    b.append(f'<circle cx="{RX}" cy="{RY}" r="3" fill="{T["text"]}"/>')
    b.append(D.text('ピッ', RX + 58, RY - 66, 22, 'sans900', T['akatext'], skew=-12))
    b.append(D.text('10 CHANNELS', RX, RY + RR + 20, 11, 'mono600', T['muted'], ls=2.5, anchor='middle'))
    # copy
    b.append(tab(0, 0, 46, 28, AKA))
    b.append(D.text('01', 23, 19, 11, 'mono700', PAPER, ls=2, anchor='middle'))
    b.append(D.text('PRIVATE BETA · OWN PRODUCT', 76, 19, 11, 'mono700', T['akatext'], ls=2.5))
    b.append(D.text('SMM Radar', 28, 70, 28, 'sans900', T['text'], ls=-.3))
    body = ['Weekly Telegram competitor reports for SMM freelancers.',
            'Branded PDF + XLSX every Monday. 18k lines, 703 tests.']
    y = 100
    for ln in body:
        b.append(D.text(ln, 28, y, 14.5, 'sans400', T['text'], opacity=.86)); y += 22
    b.append(f'<rect x="28" y="{H-50}" width="28" height="2.5" fill="{AKA}"/>')
    b.append(D.text('DJANGO 6 · PLAYWRIGHT · XLSXWRITER · AIOGRAM · DOCKER + CADDY', 28, H - 26, 11, 'mono500', T['muted'], ls=1.2))
    b.append(frame(W, H, T, 1, 2))
    alt = ('SMM Radar, private beta, own product. Weekly Telegram competitor reports for SMM freelancers: up to 10 public '
           'channels per client, branded PDF and XLSX every Monday. Public t.me/s pages only, no userbots. 18k lines, 703 tests. '
           'Django 6, Playwright, XlsxWriter, aiogram, Docker and Caddy.')
    write('quest-smm', T, D.svg(W, H + QGAP, '\n'.join(b), alt, style))

# ------------------------------------------------------------------ next episode panel, sits next to the katana GIF
def next_panel(T):
    # sits beside the Kuniyoshi print panel; both are 448 x 300
    W, H = 448, 300; D = Doc(); dark = T['name'] == 'dark'
    x0 = 12
    b = [f'<rect x="{x0}" y="0" width="{W-x0}" height="{H}" fill="{T["panel"]}"/>',
         dots(halftone_x(W - 160, W, 0, H, 6, 1.3), T['tone'], .22 if dark else .13),
         D.text('予告', W - 12, H - 12, 96, 'sans900', T['wine'], anchor='end', opacity=T['wine_op'] * .8)]
    b.append(tab(x0, 0, 108, 34, AKA))
    b.append(D.text('次回予告', x0 + 58, 24, 16, 'sans900', PAPER, ls=1, anchor='middle'))
    b.append(D.text('NEXT EPISODE', x0 + 142, 22, 11, 'mono700', T['akatext'], ls=3))
    b.append(D.text('The next episode', x0 + 22, 80, 25, 'sans900', T['text'], ls=-.3))
    b.append(D.text('needs a party.', x0 + 22, 110, 25, 'sans900', T['text'], ls=-.3))
    lines = ['Internships, freelance backend work,', 'hackathon squads. Almaty or remote.',
             'Django, FastAPI, Angular, Telegram bots,', 'browser automation, or wiring Claude', 'into a real product.']
    y = 146
    for i, ln in enumerate(lines):
        b.append(D.text(ln, x0 + 22, y, 14, 'sans400', T['text'], opacity=.86)); y += 21 + (8 if i == 1 else 0)
    b.append(D.text('FASTEST REPLY → TELEGRAM', x0 + 22, H - 20, 11.5, 'mono700', T['akatext'], ls=1.5))
    b.append(f'<rect x="{x0+1}" y="1" width="{W-x0-2}" height="{H-2}" fill="none" stroke="{T["frame"]}" stroke-opacity="{T["frame_op"]}" stroke-width="2"/>')
    alt = ('Next episode needs a party: internships, freelance backend work, hackathon squads, Almaty or remote. Django, FastAPI, '
           'Angular, Telegram bots, or wiring Claude into a real product. Fastest reply on Telegram.')
    write('next-episode', T, D.svg(W, H, '\n'.join(b), alt))

# ------------------------------------------------------------------ footer: the sun sets into a red sea, katakana seal
SEA = [  # base y, amplitude, wavelength, fill opacity, crest opacity, seconds per wavelength (far layers first)
    (120, 1.2, 60, .10, .55, 9), (129, 2.4, 90, .12, .45, 11), (143, 3.8, 150, .15, .4, 14),
    (161, 5.6, 225, .19, .35, 17), (182, 7.5, 300, .24, .3, 21)]

def wave_path(y0, amp, lam, x0, x1, bottom):
    """a periodic swell: base sine plus its second harmonic, so each layer repeats every lam px and can loop seamlessly"""
    pts = []
    for i in range(int((x1 - x0) / 6) + 1):
        x = x0 + i * 6; t = 2 * math.pi * (x - x0) / lam
        pts.append(f'{x:.0f},{y0 + amp * math.sin(t) + amp * .35 * math.sin(2 * t + 1.3):.1f}')
    crest = 'M' + ' L'.join(pts)
    return crest, crest + f' L{x1},{bottom} L{x0},{bottom} Z'

def footer(T):
    W, H = 900, 204; D = Doc(); dark = T['name'] == 'dark'
    SX, SY, SR, HZ = 492, 104, 30, 120                      # the sun sinks a little below the horizon HZ
    NX = 568                                                # name block
    style = (''.join(f'@keyframes w{i}{{from{{transform:translateX(0)}}to{{transform:translateX(-{lam}px)}}}}.w{i}{{animation:w{i} {sec}s linear infinite}}'
                     for i, (_, _, lam, _, _, sec) in enumerate(SEA))
             + '@keyframes swell{0%,100%{transform:translateY(0)}50%{transform:translateY(1.6px)}}'
             + ''.join(f'.s{i}{{animation:swell {4.2 + i*.9:.1f}s ease-in-out {i*.5:.1f}s infinite}}' for i in range(len(SEA)))
             + '@keyframes glint{0%,100%{opacity:.15}50%{opacity:.85}}'
             + ''.join(f'.g{i}{{animation:glint {1.6 + (i % 4) * .45:.2f}s ease-in-out {i * .23:.2f}s infinite}}' for i in range(12)))
    sub = 'TO BE CONTINUED  ·  NEXT COMMIT TOMORROW'
    sub_x1 = 42 + D.measure(sub, 11, 'mono700', 3) + 8
    clear_text = lambda x, y: 0 if x < sub_x1 and 80 < y < 104 else 1   # no dots under the subtitle
    b = [f'<defs><filter id="rough" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="7" result="n"/>'
         f'<feDisplacementMap in="SourceGraphic" in2="n" scale="2.6"/></filter>'
         f'<clipPath id="sky"><rect width="{W}" height="{HZ + 2}"/></clipPath><clipPath id="fr"><rect x="1" y="1" width="{W - 2}" height="{H - 2}"/></clipPath>'
         f'<linearGradient id="haze" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{AKA}" stop-opacity="0"/><stop offset="1" stop-color="{AKA}" stop-opacity="{.22 if dark else .16}"/></linearGradient></defs>',
         f'<rect width="{W}" height="{H}" fill="{T["bg"]}"/>', '<g clip-path="url(#fr)">',
         f'<rect x="0" y="{HZ - 46}" width="{W}" height="48" fill="url(#haze)"/>',          # warm air over the water
         f'<g clip-path="url(#sky)">' + dots(halftone_ring(SX, SY, SR, 46, 400, 590, 0, HZ, 5, 1.7, clear_text), AKA, .6 if dark else .5) + '</g>',
         f'<circle cx="{SX}" cy="{SY}" r="{SR}" fill="{AKA}"/>']
    # the sea: translucent layers, far to near, each drifting at its own speed; the sun's reflection sits between them
    rnd = random.Random(3); refl = []
    for j in range(11):                                   # broken glints, the column widens and fades towards the viewer
        y = HZ + 5 + j ** 1.25 * 4.4; spread = SR * (.55 + j * .16); fade = 1 - j / 13
        for k in range(rnd.choice((1, 2, 2, 3))):
            w = rnd.uniform(6, 14 + j * 2.2); x = SX + rnd.uniform(-spread, spread) - w / 2
            refl.append(f'<rect class="g{(j * 3 + k) % 12}" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{1.3 + j * .1:.1f}" rx=".8" fill="{T["hot"]}" fill-opacity="{fade:.2f}"/>')
    for i, (y0, amp, lam, fo, co, sec) in enumerate(SEA):
        crest, body = wave_path(y0, amp, lam, 0, W + lam, H + 2)
        b.append(f'<g class="s{i}"><g class="w{i}"><path d="{body}" fill="{AKA}" fill-opacity="{fo}"/>'
                 f'<path d="{crest}" fill="none" stroke="{SHU if dark else AKA}" stroke-opacity="{co}" stroke-width="{.9 + i * .15:.2f}"/></g></g>')
        if i == 1: b.append(f'<g opacity="{.8 if dark else .6}">{"".join(refl)}</g>')
    b.append('</g>')
    b += [D.text('つづく', 40, 70, 46, 'sans900', T['text'], ls=2),
          D.text(sub, 42, 96, 11, 'mono700', T['akatext'], ls=3),
          D.text('YERALY ABUTALIFULY', NX, 50, 12, 'mono700', T['text'], ls=4),
          D.text('ALMATY  ·  KBTU  ·  2026', NX, 72, 11, 'mono500', T['muted'], ls=2.5),
          D.text('github.com/overloooooord', NX, 92, 11, 'mono500', T['muted'], ls=.5)]
    assert NX + max(D.measure('YERALY ABUTALIFULY', 12, 'mono700', 4), D.measure('ALMATY  ·  KBTU  ·  2026', 11, 'mono500', 2.5)) < 796, 'name block runs into the seal'
    # square seal, read in columns right to left: エ ラ | リ 印
    g = [f'<rect x="-40" y="-40" width="80" height="80" rx="7" fill="none" stroke="{AKA}" stroke-width="4.5"/>',
         f'<rect x="-33" y="-33" width="66" height="66" rx="3" fill="none" stroke="{AKA}" stroke-width="1.3"/>',
         D.text('エ', 14, -3, 27, 'serif900', AKA, anchor='middle'), D.text('ラ', 14, 27, 27, 'serif900', AKA, anchor='middle'),
         D.text('リ', -14, -3, 27, 'serif900', AKA, anchor='middle'), D.text('印', -14, 27, 27, 'serif900', AKA, anchor='middle')]
    b.append(f'<g transform="translate(848 60) rotate(-7)" filter="url(#rough)" opacity=".95">{"".join(g)}</g>')
    b.append(f'<rect x="0" y="0" width="{W}" height="2" fill="{AKA}"/>')
    b.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" fill="none" stroke="{T["line"] if dark else INK}" stroke-width="{1 if dark else 1.5}"/>')
    write('footer', T, D.svg(W, H, '\n'.join(b), 'To be continued. A red sun sets into a translucent red sea. Yeraly Abutalifuly, Almaty, KBTU, 2026. Seal: エラリ印', style))

# ------------------------------------------------------------------ link buttons, three per row
ICONS = {'telegram': 'M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z',
         'instagram': 'M7.0301.084c-1.2768.0602-2.1487.264-2.911.5634-.7888.3075-1.4575.72-2.1228 1.3877-.6652.6677-1.075 1.3368-1.3802 2.127-.2954.7638-.4956 1.6365-.552 2.914-.0564 1.2775-.0689 1.6882-.0626 4.947.0062 3.2586.0206 3.6671.0825 4.9473.061 1.2765.264 2.1482.5635 2.9107.308.7889.72 1.4573 1.388 2.1228.6679.6655 1.3365 1.0743 2.1285 1.38.7632.295 1.6361.4961 2.9134.552 1.2773.056 1.6884.069 4.9462.0627 3.2578-.0062 3.668-.0207 4.9478-.0814 1.28-.0607 2.147-.2652 2.9098-.5633.7889-.3086 1.4578-.72 2.1228-1.3881.665-.6682 1.0745-1.3378 1.3795-2.1284.2957-.7632.4966-1.636.552-2.9124.056-1.2809.0692-1.6898.063-4.948-.0063-3.2583-.021-3.6668-.0817-4.9465-.0607-1.2797-.264-2.1487-.5633-2.9117-.3084-.7889-.72-1.4568-1.3876-2.1228C21.2982 1.33 20.628.9208 19.8378.6165 19.074.321 18.2017.1197 16.9244.0645 15.6471.0093 15.236-.005 11.977.0014 8.718.0076 8.31.0215 7.0301.0839m.1402 21.6932c-1.17-.0509-1.8053-.2453-2.2287-.408-.5606-.216-.96-.4771-1.3819-.895-.422-.4178-.6811-.8186-.9-1.378-.1644-.4234-.3624-1.058-.4171-2.228-.0595-1.2645-.072-1.6442-.079-4.848-.007-3.2037.0053-3.583.0607-4.848.05-1.169.2456-1.805.408-2.2282.216-.5613.4762-.96.895-1.3816.4188-.4217.8184-.6814 1.3783-.9003.423-.1651 1.0575-.3614 2.227-.4171 1.2655-.06 1.6447-.072 4.848-.079 3.2033-.007 3.5835.005 4.8495.0608 1.169.0508 1.8053.2445 2.228.408.5608.216.96.4754 1.3816.895.4217.4194.6816.8176.9005 1.3787.1653.4217.3617 1.056.4169 2.2263.0602 1.2655.0739 1.645.0796 4.848.0058 3.203-.0055 3.5834-.061 4.848-.051 1.17-.245 1.8055-.408 2.2294-.216.5604-.4763.96-.8954 1.3814-.419.4215-.8181.6811-1.3783.9-.4224.1649-1.0577.3617-2.2262.4174-1.2656.0595-1.6448.072-4.8493.079-3.2045.007-3.5825-.006-4.848-.0608M16.953 5.5864A1.44 1.44 0 1 0 18.39 4.144a1.44 1.44 0 0 0-1.437 1.4424M5.8385 12.012c.0067 3.4032 2.7706 6.1557 6.173 6.1493 3.4026-.0065 6.157-2.7701 6.1506-6.1733-.0065-3.4032-2.771-6.1565-6.174-6.1498-3.403.0067-6.156 2.771-6.1496 6.1738M8 12.0077a4 4 0 1 1 4.008 3.9921A3.9996 3.9996 0 0 1 8 12.0077',
         'tiktok': 'M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z',
         'vercel': 'm12 1.608 12 20.784H0Z',
         'mail': 'M2 4H22V20H2ZM4 6V18H20V6ZM4 6.8L12 12.6L20 6.8V9.2L12 15L4 9.2Z',
         'linkedin': 'M3.5 5.5a2 2 0 1 0 4 0a2 2 0 1 0-4 0ZM3.7 9h3.6v11.5H3.7ZM10 9h3.4v1.6c.6-1 1.9-1.9 3.8-1.9 3.4 0 4.3 2.2 4.3 5.2v6.6h-3.6v-5.9c0-1.5-.3-2.8-1.9-2.8s-2.1 1.2-2.1 2.8v5.9H10Z',
         'github': 'M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12'}

def button(T, name, icon, label, handle, alt, pos):
    W, H = 300, 48; D = Doc(); dark = T['name'] == 'dark'
    x0 = {'left': 0, 'mid': 4, 'right': 8}[pos]; x1 = x0 + 292
    b = [f'<rect x="{x0}" y="0" width="292" height="{H}" fill="{T["panel"]}"/>',
         f'<rect x="{x0}" y="0" width="48" height="{H}" fill="{AKA}"/>',
         f'<path d="{ICONS[icon]}" transform="translate({x0+13} 13) scale(.9167)" fill="{PAPER}"/>',
         D.text(label, x0 + 62, 19, 11, 'mono500', T['muted'], ls=1.5),
         D.text(handle, x0 + 62, 37, next(sz for sz in (14.5, 14, 13.5, 13, 12.5, 12) if D.measure(handle, sz, 'sans700') < 204 or sz == 12), 'sans700', T['text']),
         f'<path d="M{x1-20} 18 l6 6 l-6 6" fill="none" stroke="{T["akatext"]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
         f'<rect x="{x0+.75}" y=".75" width="290.5" height="{H-1.5}" fill="none" stroke="{T["frame"]}" stroke-opacity="{T["frame_op"]}" stroke-width="1.5"/>']
    write(f'btn-{name}', T, D.svg(W, H, '\n'.join(b), alt))


if __name__ == '__main__':
    only = [a for a in sys.argv[1:] if not a.startswith('--')]
    def want(n): return not only or n in only
    for T in (DARK, LIGHT):
        if want('hero'): hero(T)
        if want('ribbon'): ribbon(T)
        if want('stats'): flavor_stats(T)
        if want('chapters'):
            chapter(T, '01', '第一話', 'ARSENAL', 'LANGUAGES  ·  BACKEND  ·  FRONTEND  ·  AUTOMATION  ·  INFRA', 'Chapter 1: arsenal', fold=True)
            chapter(T, '02', '第二話', 'QUEST LOG', 'FLAVOR TREE  ·  SMM RADAR  ·  INVISION U  ·  IGTG', 'Chapter 2: quest log', fold=True)
            chapter(T, '03', '第三話', 'WORKSHOP', 'AUTOMATION  ·  IN THE LAB  ·  FRONTEND', 'Chapter 3: workshop', fold=True)
            chapter(T, '04', '第四話', 'CONTRIBUTION LOG', 'LIVE  ·  UPDATED DAILY', 'Chapter 4: contribution log', fold=True)
            chapter(T, 'next', '次回予告', 'NEXT EPISODE', 'TELEGRAM  ·  EMAIL  ·  LINKEDIN', 'Next episode: contact')
        if want('quests'):
            quest_smm(T)
            for (key, num, title, stamp, kanji, body, tech, alt), side, lean in zip(QUESTS, ('left', 'right'), (1, 1)):
                quest_card(T, key, num, title, stamp, kanji, body, tech, alt, side, lean)
        if want('next'): next_panel(T)
        if want('footer'): footer(T)
        if want('buttons'):
            button(T, 'live', 'vercel', 'LIVE · VERCEL.APP', 'flavor-tree-frontend', 'Live: flavor-tree-frontend.vercel.app', 'left')
            button(T, 'devrepo', 'github', 'DEV REPO · 93 COMMITS', 'overloooooord/efesccl-champ', 'Dev repo: overloooooord/efesccl-champ, 93 commits', 'mid')
            button(T, 'teamrepo', 'github', 'TEAM REPO', 'Adelllya/Efes-ccl-Flavor', 'Team repo: Adelllya/Efes-ccl-Flavor', 'right')
            button(T, 'telegram', 'telegram', 'TELEGRAM · FASTEST REPLY', '@dreamdrainer', 'Telegram @dreamdrainer', 'left')
            button(T, 'email', 'mail', 'EMAIL · CV ON REQUEST', 'e_abutalifuly@kbtu.kz', 'Email e_abutalifuly@kbtu.kz', 'mid')
            button(T, 'linkedin', 'linkedin', 'LINKEDIN', 'Yeraly Abutalifuly', 'LinkedIn: Yeraly Abutalifuly', 'right')
    if want('pages'): flavor_pages()
