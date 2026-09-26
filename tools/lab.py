#!/usr/bin/env python3
"""Chapter 6, the lab: three builds from September 2026 that live in private repos (Footfall, FaceTabel, Spread Scanner)."""
from build_assets import *

LAB = [
    ('01', 'Footfall', '人', 'PEOPLE COUNTER',
     'Visitor counter for shops and cafes on the Hikvision and Dahua cameras they already own. YOLOX on OpenCV DNN, line crossing, live dashboard.',
     'OPENCV 5 · ONNX · RTSP · FASTAPI'),
    ('02', 'FaceTabel', '顔', 'STAFF ATTENDANCE',
     'Consent-only face check-in for staff: YuNet and SFace on OpenCV 5, kiosk greeting screen. 0 false matches in 300 LFW pairs.',
     'OPENCV 5 · YUNET · SFACE · SQLITE'),
    ('03', 'Spread Scanner', '差', 'CRYPTO ARBITRAGE',
     'Spot spreads and funding arbitrage across seven exchanges: async adapters, route checks. Sold as a paid Telegram channel.',
     'PYTHON ASYNCIO · 7 EXCHANGES'),
]

def lab_panel(T):
    W, H = 900, 262; D = Doc(); dark = T['name'] == 'dark'; CW = W / 3
    style = '@keyframes hot{0%,100%{opacity:1}50%{opacity:.35}}.hot{animation:hot 2.4s ease-in-out infinite}'
    b = [f'<rect width="{W}" height="{H}" fill="{T["panel"]}"/>']
    for i, (num, title, kanji, stamp, body, tech) in enumerate(LAB):
        x = i * CW
        if i: b.append(f'<line x1="{x}" y1="18" x2="{x}" y2="{H-52}" stroke="{T["line"]}" stroke-width="1.5"/>')
        b.append(f'<g clip-path="url(#c{i})">' + dots(halftone_x(x + CW - 120, x + CW, 0, H - 52, 6, 1.2), T['tone'], .2 if dark else .12) + '</g>')
        b.append(D.text(kanji, x + CW - 14, 150, 104, 'sans900', T['wine'], anchor='end', opacity=T['wine_op']))
        b.append(tab(x, 0, 46, 28, AKA))
        b.append(D.text(num, x + 23, 19, 11, 'mono700', PAPER, ls=2, anchor='middle'))
        b.append(D.text(stamp, x + CW - 22, 19, 10.5, 'mono700', T['akatext'], ls=2, anchor='end'))
        b.append(D.text(title, x + 24, 68, 22, 'sans900', T['text'], ls=-.2))
        y = 98; inner = CW - 48
        lines = D.wrap(body, 12.5, 'sans400', inner)
        assert len(lines) <= 4, (title, lines)
        assert D.measure(tech, 10.5, 'mono500', 1.2) <= inner, tech
        for ln in lines:
            b.append(D.text(ln, x + 24, y, 12.5, 'sans400', T['text'], opacity=.84)); y += 18
        b.append(f'<rect x="{x+24}" y="{H-92}" width="28" height="2.5" fill="{AKA}"/>')
        b.append(D.text(tech, x + 24, H - 70, 10.5, 'mono500', T['muted'], ls=1.2))
    b.insert(0, '<defs>' + ''.join(f'<clipPath id="c{i}"><rect x="{i*CW}" y="0" width="{CW}" height="{H-52}"/></clipPath>' for i in range(3)) + '</defs>')
    # status strip
    b.append(f'<rect x="0" y="{H-52}" width="{W}" height="1.5" fill="{T["line"]}"/>')
    b.append(f'<circle class="hot" cx="34" cy="{H-26}" r="4" fill="{T["hot"]}"/>')
    b.append(D.text('IN PROGRESS · SEPTEMBER 2026 · PRIVATE REPOS UNTIL THE FIRST PAYING CLIENT', 50, H - 22, 11, 'mono700', T['akatext'], ls=2))
    b.append(D.text('3 BUILDS · 400+ TESTS', W - 24, H - 22, 11, 'mono600', T['muted'], ls=2, anchor='end'))
    b.append(frame(W, H, T, 1, 2))
    alt = ('In the lab, September 2026, private repos: Footfall, a visitor counter for shops and cafes on existing Hikvision and Dahua '
           'cameras with OpenCV DNN and a live dashboard; FaceTabel, consent-only face check-in for staff with YuNet and SFace on OpenCV 5, '
           '0 false matches in 300 LFW pairs; Spread Scanner, spot spread and funding arbitrage across seven crypto exchanges, sold as a Telegram channel.')
    write('lab', T, D.svg(W, H, '\n'.join(b), alt, style))

if __name__ == '__main__':
    for T in (DARK, LIGHT):
        lab_panel(T)
        chapter(T, '06', '第六話', 'IN THE LAB', 'FOOTFALL  ·  FACETABEL  ·  SPREAD SCANNER  ·  SEPTEMBER 2026', 'Chapter 6: in the lab')
