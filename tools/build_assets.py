#!/usr/bin/env python3
"""Akai (赤) Anime profile: builds every SVG in ../assets, dark and paper-white light twins.

All text is typeset to vector paths by typeset.py (HarfBuzz + Noto Sans CJK JP / Source Code Pro),
so nothing depends on the viewer's fonts. Facts come from variants/FACTS.md; the contribution
calendar is the snapshot in data/ (refresh it with: python3 build_assets.py --refresh).
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
DATA = HERE / 'data' / 'contributions-2026-09-26.json'
SNAP = 'SNAPSHOT · 2026.09'

INK = '#0b0b0d'; INK2 = '#120d10'; BLOOD = '#3a0a10'; WINE = '#7a0a1a'
AKA = '#c8102e'; SHU = '#ef454a'; NEON = '#ff2a2a'; PAPER = '#f3ede4'

DARK = dict(name='dark', bg=INK, panel=INK2, text=PAPER, muted='#b5b0aa', dim='#8a8a8a', line=BLOOD,
            frame=PAPER, frame_op=.75, aka=AKA, akatext=SHU, hot=NEON, wine=WINE, wine_op=.42,
            tone=AKA, cell=['#21161a', '#4a0d17', '#7a0a1a', '#c8102e', '#ff2a2a'])
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

# ------------------------------------------------------------------ hero poster
def hero(T):
    W, H = 900, 320; SX, SY, SR = 668, 158, 118; rnd = random.Random(7); D = Doc(); dark = T['name'] == 'dark'
    style = ('@keyframes spark{0%{transform:translateX(0)}100%{transform:translateX(330px)}}.spark{animation:spark 2.8s ease-in-out infinite alternate}'
             '@keyframes fall{0%{transform:translate(0,0) rotate(0deg);opacity:0}8%{opacity:.8}92%{opacity:.8}100%{transform:translate(-150px,300px) rotate(320deg);opacity:0}}'
             + ''.join(f'.p{i}{{animation:fall {7+i*1.3:.1f}s linear {i*1.7:.1f}s infinite}}' for i in range(6))
             + f'@keyframes shimmer{{0%,100%{{opacity:{.18 if dark else .22}}}50%{{opacity:{.5 if dark else .55}}}}}'
             + ''.join(f'.l{i}{{animation:shimmer {3+(i%4)*.9:.1f}s ease-in-out {i*.37:.2f}s infinite}}' for i in range(8)))
    b = [f'<defs><linearGradient id="rule" x1="0" x2="1"><stop offset="0" stop-color="{T["aka"]}"/><stop offset="1" stop-color="{T["aka"]}" stop-opacity="0"/></linearGradient>'
         f'<clipPath id="fr"><rect width="{W}" height="{H}"/></clipPath></defs>',
         f'<rect width="{W}" height="{H}" fill="{T["bg"]}"/>', '<g clip-path="url(#fr)">']
    # halftone falloff around the sun (dot size drops with distance), kept off the katakana
    fade_left = lambda x, y: max(0, min(1, (x - 470) / 90))
    b.append(dots(halftone_ring(SX, SY, SR, 175, 440, 900, 0, 324, 8, 2.8, fade_left), T['aka'], .55 if dark else .5))
    # screen tone in the lower left, growing towards the bottom edge
    tone = [(x, y, r) for x, y, r in ((x + (4 if (y // 7) % 2 else 0), y, 1.5 * ((y - 214) / 106) ** 1.3)
            for y in range(214, 322, 7) for x in range(0, 430, 7)) if r > .35 and x < 430 - (y - 214) * .5]
    b.append(dots(tone, WINE if dark else INK, .6 if dark else .16))
    # focus lines (集中線) radiating from the sun, kept off the kicker
    lines = []
    for i in range(64):
        ang = math.radians(rnd.uniform(96, 264))
        r1 = SR + rnd.uniform(14, 60); r2 = r1 + rnd.uniform(70, 420)
        x1, y1 = SX + r1 * math.cos(ang), SY + r1 * math.sin(ang)
        x2, y2 = SX + r2 * math.cos(ang), SY + r2 * math.sin(ang)
        if any(40 <= x1 + (x2 - x1) * t <= 600 and 30 <= y1 + (y2 - y1) * t <= 62 for t in (0, .25, .5, .75, 1)):
            continue
        lines.append(f'<line class="l{i%8}" x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke-width="{rnd.uniform(.7,2.2):.1f}"/>')
    b.append(f'<g stroke="{T["aka"]}" stroke-linecap="round">{"".join(lines)}</g>')
    # the sun: one flat disc, poster style
    b.append(f'<circle cx="{SX}" cy="{SY}" r="{SR}" fill="{T["aka"]}"/>')
    # katakana name: knockout, red offset print, face
    kx, ky, ks = 54, 214, 150
    b.append(D.text('クリム', kx, ky, ks, 'sans900', T['bg'], ls=-6, extra=f' stroke="{T["bg"]}" stroke-width="{14/ks*1000:.0f}" stroke-linejoin="round"'))
    b.append(D.text('クリム', kx + 7, ky + 7, ks, 'sans900', T['aka'], ls=-6))
    b.append(D.text('クリム', kx, ky, ks, 'sans900', T['text'], ls=-6))
    b.append(D.text('AKAI · BACKEND DEVELOPER · KBTU · ALMATY, KZ', 56, 52, 11.5, 'mono700', T['akatext'], ls=4))
    b.append(D.text('KLIM KASSYMKHAN', 56, 262, 27, 'sans900', T['text'], ls=3))
    b.append(f'<rect x="56" y="280" width="420" height="2" fill="url(#rule)"/>')
    b.append(f'<rect class="spark" x="56" y="280" width="70" height="2" fill="{T["text"]}" opacity=".9"/>')
    b.append(D.text('DJANGO · FASTAPI · POSTGRESQL · ANGULAR', 56, 303, 11.5, 'mono500', T['muted'], ls=3))
    # vertical kanji column, right edge
    b.append(D.vtext('開発者', 862, 34, 26, 'sans700', T['text'], gap=6))
    b.append(D.vtext('バックエンド', 836, 40, 13, 'sans700', T['akatext'], gap=3))
    b.append(f'<line x1="862" y1="140" x2="862" y2="228" stroke="{T["text"]}" stroke-width="1" opacity=".4"/>')
    b.append(f'<rect x="838" y="254" width="42" height="42" fill="{T["aka"]}"/>')
    b.append(D.text('赤', 859, 287, 30, 'sans900', PAPER, anchor='middle'))
    b.append(D.text('VOL.03', 829, 303, 10, 'mono500', T['dim'], ls=2, anchor='end'))
    petal = 'M0,-7 C4.5,-4.5 5.5,2.5 0,7 C-5.5,2.5 -4.5,-4.5 0,-7 Z'
    for i, (px, py, sc) in enumerate([(560, -10, 1), (700, -20, .8), (820, -6, 1.1), (640, -30, .7), (760, -12, .9), (880, -24, .75)]):
        b.append(f'<g class="p{i}"><path d="{petal}" transform="translate({px} {py}) scale({sc})" fill="{T["akatext"] if dark else AKA}"/></g>')
    b.append('</g>')
    b.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" fill="none" stroke="{T["line"] if dark else INK}" stroke-width="{1 if dark else 1.5}"/>')
    write('hero', T, D.svg(W, H, '\n'.join(b), 'Klim Kassymkhan, クリム, backend developer, KBTU, Almaty', style))

# ------------------------------------------------------------------ status ribbon (light: a red obi band)
def ribbon(T):
    W, H = 900, 44; D = Doc(); dark = T['name'] == 'dark'
    bg, tabc, tabt, txt, dot, rec = ((T['panel'], AKA, PAPER, T['text'], NEON, SHU) if dark
                                     else (AKA, INK, PAPER, PAPER, PAPER, PAPER))
    style = ('@keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}.dot{animation:pulse 2.4s ease-in-out infinite}'
             '@keyframes ring{0%{transform:scale(.6);opacity:.9}100%{transform:scale(2.6);opacity:0}}'
             '.ring{transform-box:fill-box;transform-origin:center;animation:ring 2.4s ease-out infinite}')
    b = [f'<rect width="{W}" height="{H}" fill="{bg}"/>', tab(0, 0, 128, H, tabc),
         D.text('STATUS', 60, 27, 12, 'mono700', tabt, ls=4, anchor='middle'),
         D.text('OPEN TO INTERNSHIPS · FREELANCE BACKEND WORK · HACKATHON TEAMS', 164, 27, 11.5, 'mono500', txt, ls=2.2, opacity=.92),
         f'<circle class="ring" cx="752" cy="22" r="4" fill="none" stroke="{dot}" stroke-width="1.2"/>',
         f'<circle class="dot" cx="752" cy="22" r="4" fill="{dot}"/>',
         D.text('RECRUITING', 874, 27, 11, 'mono700', rec, ls=3, anchor='end')]
    if dark: b.append(f'<rect x="0" y="{H-1}" width="{W}" height="1" fill="{BLOOD}"/>')
    write('ribbon-status', T, D.svg(W, H, '\n'.join(b), 'Status: open to internships, freelance backend work and hackathon teams', style))

# ------------------------------------------------------------------ chapter strips
def chapter(T, name, kanji, title, sub, label):
    W, H = 900, 56; D = Doc(); dark = T['name'] == 'dark'
    b = [f'<rect width="{W}" height="{H}" fill="{T["panel"]}"/>',
         dots(halftone_x(600, 900, 3, 56, 7, 1.6), T['tone'], .3 if dark else .2),
         tab(0, 0, 124, H, AKA), D.text(kanji, 62, 35, 19, 'sans900', PAPER, ls=1, anchor='middle'),
         D.text(title, 160, 35, 16, 'sans900', T['text'], ls=5)]
    tw = 160 + D.measure(title, 16, 'sans900', 5)
    ls = 2
    while 872 - D.measure(sub, 11.5, 'mono500', ls) < tw + 28 and ls > 0: ls -= .25
    b.append(D.text(sub, 872, 34, 11.5, 'mono500', T['muted'], ls=ls, anchor='end'))
    b.append(f'<rect x="0" y="{H-2}" width="{W}" height="2" fill="{AKA}"/>')
    b.append(f'<rect x="0" y="0" width="{W}" height="1" fill="{T["text"]}" opacity="{.18 if dark else .9}"/>')
    write(f'chapter-{name}', T, D.svg(W, H, '\n'.join(b), label))

# ------------------------------------------------------------------ portrait: ink silhouette against a flat red sun
SILHOUETTE = (  # side profile facing right in a 200x200 box; hair swept back by the wind
    'M16 222 C24 180 50 162 80 153 L86 147 L88 128 '
    'C82 127 76 126 72 125 L44 136 Q60 123 64 118 L28 118 Q54 108 60 103 L24 94 Q52 90 60 85 '
    'L30 70 Q58 72 66 71 L44 50 Q68 58 76 60 L66 36 Q86 50 92 54 L100 38 Q104 52 110 58 L128 57 '
    'Q120 64 118 68 '
    'C122 70 126 76 126 82 L125 86 L129 92 L134 99 L129 101 L129 105 L131 107 L128 110 L129 113 '
    'C128 119 124 122 117 124 L110 124 C108 130 108 136 110 142 L114 146 C146 152 174 166 186 222 Z')
EYE = 'M111 90 Q117 85.5 123.5 88.5 Q117 92 111 90 Z'
FIG = 'translate(100 118) scale(.8) translate(-100 -100)'   # figure placement inside the box

def portrait(T, cx, cy):
    """portrait disc (radius 72) centred at cx, cy: ink figure in profile against a flat red sun"""
    dark = T['name'] == 'dark'
    ox, oy = cx - 100, cy - 100                 # box origin
    sx, sy, sr = cx + 10, cy - 6, 44            # the sun sits behind the face
    s = [f'<clipPath id="pc"><circle cx="{cx}" cy="{cy}" r="72"/></clipPath>',
         f'<circle cx="{cx}" cy="{cy}" r="72" fill="{"#1c1216" if dark else PAPER}"/>']
    g = [dots(halftone_ring(sx, sy, sr, 34, cx - 76, cx + 76, cy - 76, cy + 76, 5, 1.8), AKA, .85),
         f'<circle cx="{sx}" cy="{sy}" r="{sr}" fill="{AKA}"/>']
    rnd = random.Random(3); ls = []
    for i in range(26):
        a = math.radians(rnd.uniform(0, 360)); r1 = rnd.uniform(sr + 6, sr + 14)
        ls.append(f'<line x1="{sx+r1*math.cos(a):.1f}" y1="{sy+r1*math.sin(a):.1f}" x2="{sx+86*math.cos(a):.1f}" y2="{sy+86*math.sin(a):.1f}" stroke-width="{rnd.uniform(.5,1.3):.1f}"/>')
    g.append(f'<g stroke="{AKA}" opacity=".6">{"".join(ls)}</g>')
    tf = f'translate({ox} {oy}) {FIG}'
    # rim light: a paper stroke under the ink fill leaves a hairline around the whole figure
    g.append(f'<path d="{SILHOUETTE}" transform="{tf}" fill="none" stroke="{PAPER}" stroke-width="2.4" stroke-linejoin="round" opacity="{.55 if dark else .9}"/>')
    g.append(f'<path d="{SILHOUETTE}" transform="{tf}" fill="{INK}"/>')
    # collar seam and the one glint in the eye
    g.append(f'<path d="M86 150 C92 160 102 164 114 150" transform="{tf}" fill="none" stroke="{WINE if dark else "#5c5459"}" stroke-width="1.4" stroke-linecap="round"/>')
    g.append(f'<g class="glint"><path d="{EYE}" transform="{tf}" fill="{NEON if dark else AKA}"/><circle cx="120" cy="88.6" r="1" fill="{PAPER}" transform="{tf}"/></g>')
    s.append(f'<g clip-path="url(#pc)">{"".join(g)}</g>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="72" fill="none" stroke="{AKA}" stroke-width="2.5"/>')
    s.append(f'<circle class="ring" cx="{cx}" cy="{cy}" r="81" fill="none" stroke="{T["text"]}" stroke-width="1" stroke-dasharray="3 9" opacity=".45"/>')
    for ang in (45, 135, 225, 315):
        x = cx + 81 * math.cos(math.radians(ang)); y = cy + 81 * math.sin(math.radians(ang))
        s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.5" fill="{T["akatext"]}"/>')
    return ''.join(s)

# ------------------------------------------------------------------ character sheet
SKILLS = [  # name, tier (3 main, 2 daily, 1 working), where it is used in the projects on this page
    ('Python · Django / DRF', 3, 'FLAVOR TREE · SMM RADAR · INVISION U · PETCARE'),
    ('PostgreSQL', 3, 'FLAVOR TREE · INVISION U'),
    ('Telegram bots · aiogram', 2, 'SMM RADAR · INVISION U'),
    ('Angular · TypeScript', 2, 'FLAVOR TREE (ANGULAR 18) · PETCARE'),
    ('Automation · Playwright', 2, 'SMM RADAR · IGTG BOT · LEAD TOOLS · QA DASHBOARDS'),
    ('Claude API', 1, 'FLAVOR TREE SOMMELIER · SMM RADAR SUMMARIES'),
    ('Docker', 1, 'SMM RADAR (DOCKER + CADDY)'),
    ('Java', 1, 'UNIVERSITY ROLE MANAGEMENT (OOP)'),
]
TIER = {3: 'MAIN', 2: 'DAILY', 1: 'WORKING'}
INVENTORY = 'FastAPI · React · Next.js · Redis · SQLite · Linux · GitHub Actions · Vercel · Azure · Cloudflare'

def sheet(T):
    W, H = 900, 574; D = Doc(); dark = T['name'] == 'dark'
    style = ('@keyframes spin{to{transform:rotate(360deg)}}.ring{transform-origin:150px 170px;animation:spin 40s linear infinite}'
             '@keyframes hot{0%,100%{opacity:1}50%{opacity:.35}}.hot{animation:hot 2.4s ease-in-out infinite}'
             '@keyframes glint{0%,70%,100%{opacity:1}80%{opacity:.2}}.glint{animation:glint 3.2s ease-in-out infinite}')
    C1, C2 = 290, 648
    b = [f'<rect width="{W}" height="{H}" fill="{T["panel"]}"/>',
         dots(halftone_x(0, C1, 44, 250, 6, 1.3, rising=False), T['tone'], .22 if dark else .12)]
    # header bar
    b.append(f'<rect width="{W}" height="44" fill="{AKA}"/>')
    b.append(D.text('CHARACTER SHEET', 28, 27, 12, 'mono700', PAPER, ls=5))
    b.append(D.text('キャラクターシート', 240, 28, 14, 'sans700', PAPER, ls=1, opacity=.92))
    b.append(D.text('3 YEARS OF PRACTICE', 734, 27, 11, 'mono600', PAPER, ls=2, anchor='end', opacity=.9))
    b.append(D.text('LV', 782, 28, 11, 'mono700', PAPER, ls=3, anchor='end', opacity=.9))
    b.append(D.text('03', 792, 33, 26, 'sans900', PAPER))
    # portrait + identity
    b.append(portrait(T, 150, 170))
    rows = [('NAME', 'Klim Kassymkhan'), ('CLASS', 'Backend Developer'), ('GUILD', 'KBTU · Software Engineering'),
            ('REGION', 'Almaty, Kazakhstan'), ('TITLE', 'pythoooooooooon')]
    y = 294
    for k, v in rows:
        b.append(D.text(k, 28, y, 11, 'mono500', T['muted'], ls=2.5))
        b.append(D.text(v, 96, y, 13.5, 'sans700' if k == 'NAME' else 'sans400', T['text']))
        b.append(f'<line x1="28" y1="{y+11}" x2="{C1-18}" y2="{y+11}" stroke="{T["text"]}" stroke-opacity="{.1 if dark else .16}"/>')
        y += 31
    for x in (C1, C2):
        b.append(f'<line x1="{x}" y1="44" x2="{x}" y2="{H-92}" stroke="{T["line"]}" stroke-width="1.5"/>')
    # skills with tiers and where they were used
    x0 = C1 + 24; xr = C2 - 22
    b.append(D.text('SKILLS', x0, 76, 11.5, 'mono700', T['akatext'], ls=4))
    b.append(D.text('スキル', x0 + D.measure('SKILLS', 11.5, 'mono700', 4) + 10, 77, 12, 'sans700', T['muted']))
    b.append(D.text('TIER', xr, 76, 11, 'mono500', T['muted'], ls=2.5, anchor='end'))
    y = 108
    for name, tier, used in SKILLS:
        b.append(D.text(name, x0, y, 14, 'sans700', T['text']))
        word = TIER[tier]
        ww = D.measure(word, 11, 'mono700', 1.5)
        b.append(D.text(word, xr, y, 11, 'mono700', T['akatext'] if tier == 3 else T['muted'], ls=1.5, anchor='end'))
        px = xr - ww - 12 - 3 * 15
        for i in range(3):
            on = i < tier
            hot = on and tier == 3 and i == 2
            cls = ' class="hot"' if hot else ''
            fill = (T['hot'] if hot else AKA) if on else (BLOOD if dark else T['line'])
            b.append(f'<rect{cls} x="{px + i*15}" y="{y-9}" width="12" height="9" fill="{fill}"/>')
        b.append(D.text(used, x0, y + 17, 11, 'mono500', T['muted']))
        y += 46
    # records
    x0 = C2 + 24
    b.append(D.text('RECORDS', x0, 76, 11.5, 'mono700', T['akatext'], ls=4))
    b.append(D.text('記録', x0 + D.measure('RECORDS', 11.5, 'mono700', 4) + 10, 77, 12, 'sans700', T['muted']))
    recs = [('484', 'contributions, last 12 months'), ('60', 'day streak, Jul 22 to Sep 19'),
            ('18', 'public repositories'), ('850+', 'tests across two products')]
    y = 118
    for num, lab in recs:
        b.append(D.text(num, x0, y, 30, 'sans900', T['text']))
        b.append(D.text(lab, x0, y + 18, 11, 'mono500', T['muted']))
        y += 56
    b.append(D.text(SNAP, x0, y - 18, 11, 'mono500', T['dim'], ls=1.5))
    b.append(D.text('QUESTS CLEARED', x0, 358, 11.5, 'mono700', T['akatext'], ls=4))
    quests = [('OneIdea Championship 2026', 'EFES KAZAKHSTAN · FLAVOR TREE'), ('Decentrathon 5.0', 'AI INDRIVE TRACK · INVISION U')]
    y = 384
    for q, sub in quests:
        b.append(f'<path d="M{x0} {y-5} l5 -5 l5 5 l-5 5 z" fill="{T["hot"]}"/>')
        b.append(D.text(q, x0 + 16, y, 13.5, 'sans700', T['text']))
        b.append(D.text(sub, x0 + 16, y + 17, 11, 'mono500', T['muted']))
        y += 42
    # vertical status label
    b.append(D.vtext('ステータス', 880, 60, 13, 'sans700', AKA, gap=4))
    # inventory strip along the bottom
    b.append(f'<rect x="0" y="{H-92}" width="{W}" height="1.5" fill="{T["line"]}"/>')
    b.append(D.text('INVENTORY', 28, H - 58, 11.5, 'mono700', T['akatext'], ls=4))
    b.append(D.text('持ち物', 28 + D.measure('INVENTORY', 11.5, 'mono700', 4) + 10, H - 57, 12, 'sans700', T['muted']))
    b.append(D.text(INVENTORY, 214, H - 58, 13, 'sans400', T['text'], opacity=.88))
    b.append(f'<line x1="28" y1="{H-42}" x2="{W-28}" y2="{H-42}" stroke="{T["text"]}" stroke-opacity="{.1 if dark else .16}"/>')
    b.append(D.text('PASSIVE', 28, H - 24, 11.5, 'mono700', T['akatext'], ls=4))
    b.append(D.text('特技', 28 + D.measure('PASSIVE', 11.5, 'mono700', 4) + 10, H - 23, 12, 'sans700', T['muted']))
    b.append(D.text('SEO, several years  ·  Public speaking, several years  ·  Camoufox and curl_cffi account automation', 214, H - 24, 13, 'sans400', T['text'], opacity=.88))
    b.append(frame(W, H, T))
    b.append(f'<rect x="5.5" y="49.5" width="{W-11}" height="{H-55}" fill="none" stroke="{T["text"]}" stroke-opacity="{.12 if dark else .18}"/>')
    alt = ('Character sheet. Class: Backend Developer, level 3 for three years of practice, guild KBTU Software Engineering, '
           'Almaty. Skills by tier: main Python, Django and DRF, PostgreSQL; daily Telegram bots with aiogram, Angular and '
           'TypeScript, automation with Playwright and asyncio; working Claude API, Docker, Java. Records: 484 contributions in the last 12 months, 60 day streak, '
           '18 public repositories, 850 plus tests. Passive: SEO and public speaking, several years each; account automation on Camoufox and curl_cffi. Snapshot September 2026.')
    write('sheet', T, D.svg(W, H, '\n'.join(b), alt, style))

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
def jpeg_data(path, width=None, crop=None, q=86):
    im = Image.open(path).convert('RGB')
    if crop: im = im.crop(crop)
    if width and im.width != width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
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
    src, (iw, ih) = jpeg_data(SHOTS / 'flavor-tree-champ-desktop.png', 1200, q=84)
    x0, y0, x1 = 10, 34, 890; sh = (x1 - x0) / iw * ih
    yb_l, yb_r = y0 + sh - 4, y0 + sh - 26
    d = f'M{x0} {y0} H{x1} V{yb_r:.1f} L{x0} {yb_l:.1f} Z'
    b = [f'<defs><clipPath id="a"><path d="{d}"/></clipPath></defs>',
         f'<image href="{src}" x="{x0}" y="{y0}" width="{x1-x0}" height="{sh:.1f}" clip-path="url(#a)" preserveAspectRatio="xMidYMid slice"/>',
         ink_frame(d)]
    t, tw = kanji_tab(D, 26, 8, '選手権')
    b.append(t)
    b.append(caption_box(D, 26 + tw + 22, 12, ['CHAMPIONSHIP BUILD · ONEIDEA 2026 × EFES KAZAKHSTAN']))
    b.append(caption_box(D, x1 - 18, yb_r - 50, ['efesccl-champ.vercel.app'], 12.5, 'mono700', anchor='end'))
    write_neutral('ft-page-champ', D.svg(W, H, '\n'.join(b), 'Flavor Tree championship build: dark hero, five Efes brands, one search box for what is on your table'))

    # page B: public desktop build (slanted right edge) + the phone in a red focus-line panel
    W, H = 900, 424; D = Doc()
    top_l, top_r = 26, 4                       # parallel to page A's bottom edge
    src, (iw, ih) = jpeg_data(SHOTS / 'flavor-tree-desktop.png', 1000, q=86)
    xl0, xl1t, xl1b, yb = 10, 604, 586, 414
    ytop = lambda x: top_l + (top_r - top_l) * x / W
    dl = f'M{xl0} {ytop(xl0):.1f} L{xl1t} {ytop(xl1t):.1f} L{xl1b} {yb} L{xl0} {yb} Z'
    ph = yb - ytop(xl0); pw = ph * iw / ih
    b = [f'<defs><clipPath id="l"><path d="{dl}"/></clipPath>']
    xr0t, xr0b, xr1 = 622, 604, 890
    dr = f'M{xr0t} {ytop(xr0t):.1f} L{xr1} {ytop(xr1):.1f} L{xr1} {yb} L{xr0b} {yb} Z'
    b.append(f'<clipPath id="r"><path d="{dr}"/></clipPath>')
    msrc, (mw, mh) = jpeg_data(SHOTS / 'flavor-tree-mobile.png', 390, q=88)
    b.append('<clipPath id="scr"><rect x="-73" y="-158" width="146" height="316" rx="17"/></clipPath></defs>')
    b.append(f'<image href="{src}" x="{xl0 - 8}" y="{ytop(xl0):.1f}" width="{pw:.1f}" height="{ph:.1f}" clip-path="url(#l)" preserveAspectRatio="xMinYMin slice"/>')
    # right panel: red, halftone, focus lines around the phone
    pcx, pcy = 752, 214
    g = [f'<rect x="590" y="0" width="310" height="{H}" fill="{AKA}"/>',
         dots(halftone_ring(pcx, pcy, 120, 150, 590, 900, 0, H, 7, 2.2), INK, .35)]
    rnd = random.Random(11); ls = []
    for i in range(46):
        a = math.radians(rnd.uniform(0, 360)); r1 = rnd.uniform(150, 175); r2 = 330
        ls.append(f'<line x1="{pcx+r1*math.cos(a):.0f}" y1="{pcy+r1*math.sin(a):.0f}" x2="{pcx+r2*math.cos(a):.0f}" y2="{pcy+r2*math.sin(a):.0f}" stroke-width="{rnd.uniform(.8,2.6):.1f}"/>')
    g.append(f'<g stroke="{PAPER}" opacity=".55">{"".join(ls)}</g>')
    b.append(f'<g clip-path="url(#r)">{"".join(g)}</g>')
    b.append(ink_frame(dl)); b.append(ink_frame(dr))
    # the phone, tilted, breaking the panel frame a little
    b.append(f'<g transform="translate({pcx} {pcy}) rotate(-6)">'
             f'<rect x="-84" y="-170" width="168" height="340" rx="26" fill="{INK}" stroke="{PAPER}" stroke-width="2"/>'
             f'<image href="{msrc}" x="-73" y="-158" width="146" height="{146*mh/mw:.1f}" clip-path="url(#scr)" preserveAspectRatio="xMidYMin slice"/>'
             f'<rect x="-22" y="-152" width="44" height="11" rx="5.5" fill="{INK}"/>'
             '</g>')
    t, tw = kanji_tab(D, 26, ytop(26) - 18, '公開版')
    b.append(t)
    b.append(caption_box(D, 26 + tw + 22, ytop(26 + tw + 22) - 14, ['PUBLIC BUILD · efes-ccl.vercel.app']))
    t, tw = kanji_tab(D, 640, ytop(640) - 18, 'スマホ', fill=INK)
    b.append(t)
    b.append(caption_box(D, 870, yb - 44, ['390 PX VIEWPORT'], 11.5, 'mono700', anchor='end'))
    write_neutral('ft-page-public', D.svg(W, H, '\n'.join(b), 'Flavor Tree public build on desktop, find the perfect pair from a dish or from a beer, and the same page on a phone'))

def write_neutral(name, content):
    (OUT / f'{name}.svg').write_text(content)
    print(f'{name + ".svg":30s} {len(content.encode())/1024:7.1f} KB')

# ------------------------------------------------------------------ side quest panels
QUESTS = [
    ('invision', '02', 'InVision U', 'DECENTRATHON 5.0', '選',
     'AI candidate scoring for the inDrive youth grant (16 to 22 y.o.): Telegram intake, essay NLP on ONNX, leadership scenarios, XGBoost + SHAP explanations, fairness audit, human in the loop.',
     'DJANGO / DRF · POSTGRESQL · AIOGRAM · XGBOOST', 'InVision U, Decentrathon 5.0 AI inDrive track. AI candidate scoring for the inDrive youth grant: Telegram intake, essay NLP on ONNX, leadership scenarios, XGBoost with SHAP explanations, fairness audit, human in the loop.'),
    ('steppe', '03', 'SteppeAI', 'STARTUP LANDING', '牧',
     'AI + IoT virtual fencing for livestock. Trilingual RU / EN / KZ landing, pitch deck and commercial proposals.',
     'NEXT.JS · TAILWIND · TYPESCRIPT', 'SteppeAI. AI and IoT virtual fencing for livestock: trilingual landing, pitch deck and commercial proposals. Next.js, Tailwind, TypeScript.'),
    ('petcare', '04', 'Petcare Web', 'COURSE FINAL', '犬',
     'Pet shop and adoption listings: catalog, cart, orders, JWT auth. Angular SPA over a Django REST API. KBTU Web Development final, built with Adelllya.',
     'ANGULAR · DJANGO REST · JWT', 'Petcare Web. Pet shop and adoption listings with catalog, cart, orders and JWT auth. Angular over Django REST. KBTU Web Development final, built with Adelllya.'),
    ('oop', '05', 'University Role Management', 'KBTU OOP', '学',
     'Students, teachers, managers, admins, researchers. Course registration, grading, transcripts, requests. Pure Java, no frameworks.',
     'JAVA · OOP · NO FRAMEWORKS', 'University Role Management System. Students, teachers, managers, admins, researchers; course registration, grading, transcripts, requests. Pure Java.'),
]
QW, QH, QGAP = 440, 214, 12  # QGAP: transparent strip under each card = row gutter

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
    if len(lines) > 4: raise SystemExit(f'{key}: body needs {len(lines)} lines')
    write(f'quest-{key}', T, D.svg(QW, H + QGAP, '\n'.join(b), alt))

def quest_smm(T):
    W, H = 900, 236; D = Doc(); dark = T['name'] == 'dark'
    RX, RY, RR = 752, 118, 94
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
    b.append(D.text('SMM Radar', 28, 72, 28, 'sans900', T['text'], ls=-.3))
    body = ['Weekly Telegram competitor reports for SMM freelancers.',
            'Up to 10 public channels per client, branded PDF + XLSX every Monday.',
            'Public t.me/s pages only, no userbots. 18k lines, 703 tests.']
    y = 104
    for ln in body:
        b.append(D.text(ln, 28, y, 14.5, 'sans400', T['text'], opacity=.86)); y += 22
    b.append(f'<rect x="28" y="{H-50}" width="28" height="2.5" fill="{AKA}"/>')
    b.append(D.text('DJANGO 6 · PLAYWRIGHT · XLSXWRITER · AIOGRAM · DOCKER + CADDY', 28, H - 26, 11, 'mono500', T['muted'], ls=1.2))
    b.append(frame(W, H, T, 1, 2))
    alt = ('SMM Radar, private beta, own product. Weekly Telegram competitor reports for SMM freelancers: up to 10 public '
           'channels per client, branded PDF and XLSX every Monday. Public t.me/s pages only, no userbots. 18k lines, 703 tests. '
           'Django 6, Playwright, XlsxWriter, aiogram, Docker and Caddy.')
    write('quest-smm', T, D.svg(W, H + QGAP, '\n'.join(b), alt, style))

# ------------------------------------------------------------------ client work panel, sits next to the spider lily GIF
def client_panel(T):
    # GIF 498x283 at 42 % beside this panel at 57.8 %: equal heights at every width
    W = 520; H = round(W * (0.42 * 283 / 498) / 0.578); D = Doc(); dark = T['name'] == 'dark'
    x0 = 12
    b = [f'<rect x="{x0}" y="0" width="{W-x0}" height="{H}" fill="{T["panel"]}"/>',
         dots(halftone_x(W - 150, W, 0, H, 6, 1.2), T['tone'], .2 if dark else .12)]
    items = [('Finance Bridge', 'LIVE', 'Landing for an accounting firm in Kazakhstan.', 'REACT 19 · VITE 7 · TAILWIND 4 · TIKTOK EVENTS API'),
             ('rdrightnow.com', 'PRIVATE REPO', 'Corporate site with an Azure Functions contact form.', 'AZURE STATIC WEB APPS · FUNCTIONS · ACS EMAIL'),
             ('Fara Ideal LED', 'PRIVATE REPO', 'Landing with a Telegram lead form and a PDF proposal.', 'HTML / JS · NODE · VERCEL')]
    y = 14; step = (H - 20) / 3
    for i, (name, tag, desc, tech) in enumerate(items):
        yy = y + i * step
        b.append(tab(x0, yy + 2, 30, 22, AKA))
        b.append(D.text(f'0{i+1}', x0 + 15, yy + 17.5, 10.5, 'mono700', PAPER, ls=1, anchor='middle'))
        b.append(D.text(name, x0 + 52, yy + 19, 16, 'sans900', T['text']))
        b.append(D.text(tag, W - 18, yy + 18, 11, 'mono700', T['akatext'] if tag == 'LIVE' else T['muted'], ls=2, anchor='end'))
        b.append(D.text(desc, x0 + 52, yy + 39, 13, 'sans400', T['text'], opacity=.84))
        b.append(D.text(tech, x0 + 52, yy + 56, 11, 'mono500', T['muted'], ls=.8))
        if i < 2: b.append(f'<line x1="{x0+52}" y1="{yy+step-3:.1f}" x2="{W-18}" y2="{yy+step-3:.1f}" stroke="{T["line"]}" stroke-width="1.2"/>')
    b.append(f'<rect x="{x0+1}" y="1" width="{W-x0-2}" height="{H-2}" fill="none" stroke="{T["frame"]}" stroke-opacity="{T["frame_op"]}" stroke-width="2"/>')
    alt = ('Client work. Finance Bridge: landing for an accounting firm in Kazakhstan, React 19, Vite 7, Tailwind 4, server-side '
           'TikTok Events API tracking, live. rdrightnow.com: corporate site with an Azure Functions contact form and Azure '
           'Communication Services email, private repo. Fara Ideal LED: landing with a Telegram lead form and a PDF proposal, '
           'HTML and JS, Node, Vercel, private repo.')
    write('client-work', T, D.svg(W, H, '\n'.join(b), alt))

# ------------------------------------------------------------------ contribution log: 2026 heatmap + streak combo
def training_log(T):
    W, H = 900, 236; D = Doc(); dark = T['name'] == 'dark'
    data = json.loads(DATA.read_text())['days']
    start = dt.date(2025, 12, 28); end = dt.date(2026, 9, 26)   # Sunday-based weeks, 2026 only
    def lvl(c): return 0 if c == 0 else 1 if c == 1 else 2 if c <= 3 else 3 if c <= 9 else 4
    X0, Y0, P, S = 28, 74, 15, 12
    style = ('@keyframes run{0%{transform:translateX(0)}100%{transform:translateX(118px)}}.run{animation:run 2.6s ease-in-out infinite alternate}'
             '@keyframes hot{0%,100%{opacity:1}50%{opacity:.55}}.hot{animation:hot 2.4s ease-in-out infinite}')
    b = [f'<rect width="{W}" height="{H}" fill="{T["panel"]}"/>',
         dots(halftone_x(640, 900, 0, H, 7, 1.5), T['tone'], .24 if dark else .13)]
    b.append(D.text('TRAINING LOG 2026', X0, 34, 11.5, 'mono700', T['akatext'], ls=4))
    b.append(D.text('修行', X0 + D.measure('TRAINING LOG 2026', 11.5, 'mono700', 4) + 10, 35, 12, 'sans700', T['muted']))
    cells = []; months = {}; streak = []; apr5 = None
    d = start
    while d <= end:
        w = (d - start).days // 7; wd = (d.weekday() + 1) % 7
        x = X0 + w * P; y = Y0 + wd * P
        if d.year == 2026:
            c = data.get(d.isoformat(), 0)
            cls = ' class="hot"' if lvl(c) == 4 else ''
            cells.append(f'<rect{cls} x="{x}" y="{y}" width="{S}" height="{S}" fill="{T["cell"][lvl(c)]}"/>')
            if d.day == 1: months.setdefault(d.month, x)
            if dt.date(2026, 7, 22) <= d <= dt.date(2026, 9, 19): streak.append(x)
            if d == dt.date(2026, 4, 5): apr5 = (x, y)
        d += dt.timedelta(days=1)
    b.append(''.join(cells))
    for m, x in months.items():
        b.append(D.text(dt.date(2026, m, 1).strftime('%b').upper(), x, Y0 - 10, 11, 'mono500', T['muted'], ls=1))
    # streak bracket
    sx0, sx1 = min(streak), max(streak) + S
    yb = Y0 + 7 * P + 6
    b.append(f'<path d="M{sx0} {yb-5} V{yb} H{sx1} V{yb-5}" fill="none" stroke="{T["hot"]}" stroke-width="2"/>')
    b.append(f'<rect class="run" x="{sx0}" y="{yb-1.5}" width="14" height="3" fill="{T["text"]}"/>')
    b.append(D.text('60 DAY STREAK · JUL 22 TO SEP 19', sx1, yb + 20, 11, 'mono700', T['akatext'], ls=1.2, anchor='end'))
    # decentrathon marker on the April spike
    ax, ay = apr5
    b.append(f'<path d="M{ax+S/2} {Y0-24} V{ay-3}" stroke="{T["hot"]}" stroke-width="1.5" stroke-dasharray="2 3"/>')
    b.append(f'<circle cx="{ax+S/2}" cy="{ay+S/2}" r="10" fill="none" stroke="{T["hot"]}" stroke-width="1.5"/>')
    b.append(D.text('DECENTRATHON 5.0', ax + S / 2 - 6, Y0 - 30, 11, 'mono700', T['akatext'], ls=1.2))
    # legend
    lx = X0; ly = H - 22
    b.append(D.text('LESS', lx, ly + 9, 11, 'mono500', T['muted'], ls=1))
    for i in range(5):
        b.append(f'<rect x="{lx + 40 + i*15}" y="{ly}" width="{S}" height="{S}" fill="{T["cell"][i]}"/>')
    b.append(D.text('MORE', lx + 40 + 5 * 15 + 4, ly + 9, 11, 'mono500', T['muted'], ls=1))
    # combo counter
    cx = 648
    b.append(f'<line x1="{cx-14}" y1="22" x2="{cx-14}" y2="{H-22}" stroke="{T["line"]}" stroke-width="1.5"/>')
    b.append(D.text('ゴゴゴ', 896, 70, 34, 'sans900', T['wine'], ls=2, anchor='end', opacity=T['wine_op'] * 1.2, skew=-14))
    b.append(D.text('60', cx + 7, 126, 92, 'sans900', AKA, ls=-4, skew=-10))
    b.append(D.text('60', cx, 120, 92, 'sans900', T['text'], ls=-4, skew=-10))
    b.append(D.text('DAY COMBO', cx + 2, 148, 14, 'mono700', T['akatext'], ls=4))
    b.append(D.text('連続', cx + 2 + D.measure('DAY COMBO', 14, 'mono700', 4) + 10, 149, 15, 'sans900', T['text']))
    b.append(D.text('484 contributions in 2026', cx + 2, 176, 11.5, 'mono500', T['text'], opacity=.9))
    b.append(D.text('18 public repositories', cx + 2, 194, 11.5, 'mono500', T['text'], opacity=.9))
    b.append(D.text(SNAP, cx + 2, H - 22, 11, 'mono500', T['dim'], ls=1.5))
    b.append(frame(W, H, T, 1, 2))
    alt = ('Contribution log, snapshot September 2026: heatmap of 2026 with 484 contributions, a spike in April during '
           'Decentrathon 5.0 and a 60 day streak from July 22 to September 19. 18 public repositories.')
    write('contrib-log', T, D.svg(W, H, '\n'.join(b), alt, style))

# ------------------------------------------------------------------ next episode panel, sits next to the katana GIF
def next_panel(T):
    # GIF 498x280 at 50 % beside this panel at 49.8 %
    W = 448; H = round(W * (0.5 * 280 / 498) / 0.498); D = Doc(); dark = T['name'] == 'dark'
    x0 = 12
    b = [f'<rect x="{x0}" y="0" width="{W-x0}" height="{H}" fill="{T["panel"]}"/>',
         dots(halftone_x(W - 160, W, 0, H, 6, 1.3), T['tone'], .22 if dark else .13),
         D.text('予告', W - 12, H - 12, 96, 'sans900', T['wine'], anchor='end', opacity=T['wine_op'] * .8)]
    b.append(tab(x0, 0, 108, 34, AKA))
    b.append(D.text('次回予告', x0 + 58, 24, 16, 'sans900', PAPER, ls=1, anchor='middle'))
    b.append(D.text('NEXT EPISODE', x0 + 142, 22, 11, 'mono700', T['akatext'], ls=3))
    b.append(D.text('The next episode', x0 + 22, 72, 25, 'sans900', T['text'], ls=-.3))
    b.append(D.text('needs a party.', x0 + 22, 102, 25, 'sans900', T['text'], ls=-.3))
    lines = ['Internships, freelance backend work,', 'hackathon squads. Almaty or remote.',
             'Django, FastAPI, Angular, Telegram bots,', 'or wiring Claude into a real product.']
    y = 134
    for i, ln in enumerate(lines):
        b.append(D.text(ln, x0 + 22, y, 14, 'sans400', T['text'], opacity=.86)); y += 20 + (6 if i == 1 else 0)
    b.append(D.text('FASTEST REPLY → TELEGRAM', x0 + 22, H - 20, 11.5, 'mono700', T['akatext'], ls=1.5))
    b.append(f'<rect x="{x0+1}" y="1" width="{W-x0-2}" height="{H-2}" fill="none" stroke="{T["frame"]}" stroke-opacity="{T["frame_op"]}" stroke-width="2"/>')
    alt = ('Next episode needs a party: internships, freelance backend work, hackathon squads, Almaty or remote. Django, FastAPI, '
           'Angular, Telegram bots, or wiring Claude into a real product. Fastest reply on Telegram.')
    write('next-episode', T, D.svg(W, H, '\n'.join(b), alt))

# ------------------------------------------------------------------ footer with a katakana seal
def footer(T):
    W, H = 900, 124; D = Doc(); dark = T['name'] == 'dark'
    b = [f'<defs><filter id="rough" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="7" result="n"/>'
         f'<feDisplacementMap in="SourceGraphic" in2="n" scale="2.6"/></filter></defs>',
         f'<rect width="{W}" height="{H}" fill="{T["bg"]}"/>',
         dots(halftone_ring(512, 62, 26, 44, 440, 590, 0, H, 5, 1.6), AKA, .6 if dark else .5),
         f'<circle cx="512" cy="62" r="26" fill="{AKA}"/>',
         D.text('つづく', 40, 76, 46, 'sans900', T['text'], ls=2),
         D.text('TO BE CONTINUED  ·  NEXT COMMIT TOMORROW', 42, 101, 11, 'mono700', T['akatext'], ls=3),
         D.text('KLIM KASSYMKHAN', 548, 52, 12, 'mono700', T['text'], ls=4),
         D.text('ALMATY  ·  KBTU  ·  2026', 548, 74, 11, 'mono500', T['muted'], ls=2.5),
         D.text('github.com/overloooooord', 548, 94, 11, 'mono500', T['muted'], ls=.5)]
    # square seal, read in columns right to left: ク リ | ム 印
    g = [f'<rect x="-40" y="-40" width="80" height="80" rx="7" fill="none" stroke="{AKA}" stroke-width="4.5"/>',
         f'<rect x="-33" y="-33" width="66" height="66" rx="3" fill="none" stroke="{AKA}" stroke-width="1.3"/>',
         D.text('ク', 14, -3, 27, 'serif900', AKA, anchor='middle'), D.text('リ', 14, 27, 27, 'serif900', AKA, anchor='middle'),
         D.text('ム', -14, -3, 27, 'serif900', AKA, anchor='middle'), D.text('印', -14, 27, 27, 'serif900', AKA, anchor='middle')]
    b.append(f'<g transform="translate(848 62) rotate(-7)" filter="url(#rough)" opacity=".95">{"".join(g)}</g>')
    b.append(f'<rect x="0" y="0" width="{W}" height="2" fill="{AKA}"/>')
    b.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" fill="none" stroke="{T["line"] if dark else INK}" stroke-width="{1 if dark else 1.5}"/>')
    write('footer', T, D.svg(W, H, '\n'.join(b), 'To be continued. Klim Kassymkhan, Almaty, KBTU, 2026. Seal: クリム印'))

# ------------------------------------------------------------------ link buttons, three per row
ICONS = {'telegram': 'M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z',
         'instagram': 'M7.0301.084c-1.2768.0602-2.1487.264-2.911.5634-.7888.3075-1.4575.72-2.1228 1.3877-.6652.6677-1.075 1.3368-1.3802 2.127-.2954.7638-.4956 1.6365-.552 2.914-.0564 1.2775-.0689 1.6882-.0626 4.947.0062 3.2586.0206 3.6671.0825 4.9473.061 1.2765.264 2.1482.5635 2.9107.308.7889.72 1.4573 1.388 2.1228.6679.6655 1.3365 1.0743 2.1285 1.38.7632.295 1.6361.4961 2.9134.552 1.2773.056 1.6884.069 4.9462.0627 3.2578-.0062 3.668-.0207 4.9478-.0814 1.28-.0607 2.147-.2652 2.9098-.5633.7889-.3086 1.4578-.72 2.1228-1.3881.665-.6682 1.0745-1.3378 1.3795-2.1284.2957-.7632.4966-1.636.552-2.9124.056-1.2809.0692-1.6898.063-4.948-.0063-3.2583-.021-3.6668-.0817-4.9465-.0607-1.2797-.264-2.1487-.5633-2.9117-.3084-.7889-.72-1.4568-1.3876-2.1228C21.2982 1.33 20.628.9208 19.8378.6165 19.074.321 18.2017.1197 16.9244.0645 15.6471.0093 15.236-.005 11.977.0014 8.718.0076 8.31.0215 7.0301.0839m.1402 21.6932c-1.17-.0509-1.8053-.2453-2.2287-.408-.5606-.216-.96-.4771-1.3819-.895-.422-.4178-.6811-.8186-.9-1.378-.1644-.4234-.3624-1.058-.4171-2.228-.0595-1.2645-.072-1.6442-.079-4.848-.007-3.2037.0053-3.583.0607-4.848.05-1.169.2456-1.805.408-2.2282.216-.5613.4762-.96.895-1.3816.4188-.4217.8184-.6814 1.3783-.9003.423-.1651 1.0575-.3614 2.227-.4171 1.2655-.06 1.6447-.072 4.848-.079 3.2033-.007 3.5835.005 4.8495.0608 1.169.0508 1.8053.2445 2.228.408.5608.216.96.4754 1.3816.895.4217.4194.6816.8176.9005 1.3787.1653.4217.3617 1.056.4169 2.2263.0602 1.2655.0739 1.645.0796 4.848.0058 3.203-.0055 3.5834-.061 4.848-.051 1.17-.245 1.8055-.408 2.2294-.216.5604-.4763.96-.8954 1.3814-.419.4215-.8181.6811-1.3783.9-.4224.1649-1.0577.3617-2.2262.4174-1.2656.0595-1.6448.072-4.8493.079-3.2045.007-3.5825-.006-4.848-.0608M16.953 5.5864A1.44 1.44 0 1 0 18.39 4.144a1.44 1.44 0 0 0-1.437 1.4424M5.8385 12.012c.0067 3.4032 2.7706 6.1557 6.173 6.1493 3.4026-.0065 6.157-2.7701 6.1506-6.1733-.0065-3.4032-2.771-6.1565-6.174-6.1498-3.403.0067-6.156 2.771-6.1496 6.1738M8 12.0077a4 4 0 1 1 4.008 3.9921A3.9996 3.9996 0 0 1 8 12.0077',
         'tiktok': 'M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z',
         'vercel': 'm12 1.608 12 20.784H0Z',
         'github': 'M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12'}

def button(T, name, icon, label, handle, alt, pos):
    W, H = 300, 48; D = Doc(); dark = T['name'] == 'dark'
    x0 = {'left': 0, 'mid': 4, 'right': 8}[pos]; x1 = x0 + 292
    b = [f'<rect x="{x0}" y="0" width="292" height="{H}" fill="{T["panel"]}"/>',
         f'<rect x="{x0}" y="0" width="48" height="{H}" fill="{AKA}"/>',
         f'<path d="{ICONS[icon]}" transform="translate({x0+13} 13) scale(.9167)" fill="{PAPER}"/>',
         D.text(label, x0 + 62, 19, 11, 'mono500', T['muted'], ls=1.5),
         D.text(handle, x0 + 62, 37, 14.5, 'sans700', T['text']),
         f'<path d="M{x1-20} 18 l6 6 l-6 6" fill="none" stroke="{T["akatext"]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
         f'<rect x="{x0+.75}" y=".75" width="290.5" height="{H-1.5}" fill="none" stroke="{T["frame"]}" stroke-opacity="{T["frame_op"]}" stroke-width="1.5"/>']
    write(f'btn-{name}', T, D.svg(W, H, '\n'.join(b), alt))


def refresh():
    q = ('query{user(login:"overloooooord"){repositories(privacy:PUBLIC,ownerAffiliations:OWNER){totalCount} '
         'contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}')
    r = json.loads(subprocess.run([str(Path.home() / '.local/bin/gh'), 'api', 'graphql', '-f', f'query={q}'], capture_output=True, check=True).stdout)
    u = r['data']['user']; cal = u['contributionsCollection']['contributionCalendar']
    days = {x['date']: x['contributionCount'] for w in cal['weeks'] for x in w['contributionDays']}
    DATA.write_text(json.dumps({'source': 'GitHub GraphQL contributionCalendar', 'total_last_12_months': cal['totalContributions'],
                                'public_repos': u['repositories']['totalCount'], 'days': days}, separators=(',', ':')))
    print('refreshed', DATA)


if __name__ == '__main__':
    if '--refresh' in sys.argv: refresh()
    only = [a for a in sys.argv[1:] if not a.startswith('--')]
    def want(n): return not only or n in only
    for T in (DARK, LIGHT):
        if want('hero'): hero(T)
        if want('ribbon'): ribbon(T)
        if want('sheet'): sheet(T)
        if want('stats'): flavor_stats(T)
        if want('chapters'):
            chapter(T, '01', '第一話', 'CHARACTER SHEET', 'WHO IS PLAYING', 'Chapter 1: character sheet')
            chapter(T, '02', '第二話', 'FLAVOR TREE', 'FLAGSHIP  ·  ONEIDEA CHAMPIONSHIP 2026 × EFES KAZAKHSTAN', 'Chapter 2: Flavor Tree')
            chapter(T, '03', '第三話', 'SIDE QUESTS', 'SMM RADAR  ·  INVISION U  ·  STEPPEAI  ·  PETCARE  ·  UNIVERSITY RMS', 'Chapter 3: side quests')
            chapter(T, '06', '第六話', 'CLIENT WORK', 'FINANCE BRIDGE  ·  RDRIGHTNOW.COM  ·  FARA IDEAL LED', 'Chapter 6: client work')
            chapter(T, '07', '第七話', 'CONTRIBUTION LOG', SNAP, 'Chapter 7: contribution log')
            chapter(T, 'next', '次回予告', 'NEXT EPISODE', 'TELEGRAM  ·  INSTAGRAM  ·  TIKTOK', 'Next episode: contact')
        if want('quests'):
            quest_smm(T)
            for (key, num, title, stamp, kanji, body, tech, alt), side, lean in zip(QUESTS, ('left', 'right', 'left', 'right'), (1, 1, -1, -1)):
                quest_card(T, key, num, title, stamp, kanji, body, tech, alt, side, lean)
        if want('client'): client_panel(T)
        if want('log'): training_log(T)
        if want('next'): next_panel(T)
        if want('footer'): footer(T)
        if want('buttons'):
            button(T, 'live', 'vercel', 'LIVE · VERCEL', 'efes-ccl.vercel.app', 'Live: efes-ccl.vercel.app', 'left')
            button(T, 'devrepo', 'github', 'DEV REPO · 93 COMMITS', 'overloooooord/efesccl-champ', 'Dev repo: overloooooord/efesccl-champ, 93 commits', 'mid')
            button(T, 'teamrepo', 'github', 'TEAM REPO', 'Adelllya/Efes-ccl-Flavor', 'Team repo: Adelllya/Efes-ccl-Flavor', 'right')
            button(T, 'telegram', 'telegram', 'TELEGRAM · FASTEST REPLY', '@dreamdrainer', 'Telegram @dreamdrainer', 'left')
            button(T, 'instagram', 'instagram', 'INSTAGRAM', '@_abutalifuly_', 'Instagram @_abutalifuly_', 'mid')
            button(T, 'tiktok', 'tiktok', 'TIKTOK', '@machiavellistt', 'TikTok @machiavellistt', 'right')
    if want('pages'): flavor_pages()
