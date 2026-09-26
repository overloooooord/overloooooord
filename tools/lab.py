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

AUTO = [
    ('BROWSER & HTTP', 'ブラウザ',
     'Playwright and Camoufox where a page needs a real browser, curl_cffi and aiohttp where it does not. Async pipelines with retries, proxy pools and per-account profiles, a React + Flask dashboard to watch them run.',
     'PLAYWRIGHT · CURL_CFFI · AIOHTTP'),
    ('MAIL & AUTH FLOWS', 'メール',
     'IMAP polling for verification links and OTP codes, OAuth 2.0 and XOAUTH2 chains, session cookies and 2FA steps scripted end to end. Results land in SQLite or CSV, errors in a journal, never in a screenshot.',
     'IMAP · OAUTH 2.0 · SQLITE · CSV'),
    ('BOTS & SCHEDULERS', 'ボット',
     'Telegram as the control panel: aiogram bots with a publishing queue and scheduler (igtg, 251 tests), weekly report jobs (SMM Radar), lead collection from OpenStreetMap (227 leads). GitHub Actions and Azure Functions for the rest.',
     'AIOGRAM · CRON · GITHUB ACTIONS'),
]

def auto_panel(T):
    W, H = 900, 300; D = Doc(); dark = T['name'] == 'dark'; CW = W / 3
    style = ('@keyframes flow{0%{stroke-dashoffset:0}100%{stroke-dashoffset:-36px}}.flow{animation:flow 1.2s linear infinite}'
             '@keyframes hot{0%,100%{opacity:1}50%{opacity:.35}}.hot{animation:hot 2.4s ease-in-out infinite}')
    b = ['<defs>' + ''.join(f'<clipPath id="a{i}"><rect x="{i*CW}" y="0" width="{CW}" height="{H-52}"/></clipPath>' for i in range(3)) + '</defs>',
         f'<rect width="{W}" height="{H}" fill="{T["panel"]}"/>',
         D.text('自動化', W - 20, H - 66, 120, 'sans900', T['wine'], anchor='end', opacity=T['wine_op'] * .8)]
    for i, (title, kana, body, tech) in enumerate(AUTO):
        x = i * CW
        if i: b.append(f'<line x1="{x}" y1="18" x2="{x}" y2="{H-52}" stroke="{T["line"]}" stroke-width="1.5"/>')
        b.append(f'<g clip-path="url(#a{i})">' + dots(halftone_x(x + CW - 110, x + CW, 0, H - 52, 6, 1.1), T['tone'], .18 if dark else .1) + '</g>')
        b.append(tab(x, 0, 46, 28, AKA))
        b.append(D.text(f'0{i+1}', x + 23, 19, 11, 'mono700', PAPER, ls=2, anchor='middle'))
        b.append(D.text(kana, x + CW - 22, 20, 12, 'sans700', T['muted'], anchor='end'))
        b.append(D.text(title, x + 24, 66, 15, 'sans900', T['text'], ls=2))
        inner = CW - 48
        lines = D.wrap(body, 12.5, 'sans400', inner)
        assert len(lines) <= 7, (title, len(lines), lines)
        assert D.measure(tech, 10.5, 'mono500', 1.2) <= inner, tech
        y = 94
        for ln in lines:
            b.append(D.text(ln, x + 24, y, 12.5, 'sans400', T['text'], opacity=.84)); y += 18
        b.append(f'<rect x="{x+24}" y="{H-94}" width="28" height="2.5" fill="{AKA}"/>')
        b.append(D.text(tech, x + 24, H - 72, 10.5, 'mono500', T['muted'], ls=1.2))
    # pipeline strip: source -> worker -> store -> telegram
    b.append(f'<rect x="0" y="{H-52}" width="{W}" height="1.5" fill="{T["line"]}"/>')
    steps = ['SOURCE', 'ASYNC WORKERS', 'RETRY · PROXY · OTP', 'SQLITE / CSV', 'TELEGRAM ALERT']
    xs = [30, 190, 380, 600, 760]
    for j, (st, sx) in enumerate(zip(steps, xs)):
        b.append(f'<circle{" class=\"hot\"" if j == len(steps)-1 else ""} cx="{sx}" cy="{H-26}" r="4" fill="{T["hot"] if j == len(steps)-1 else AKA}"/>')
        b.append(D.text(st, sx + 12, H - 22, 11, 'mono700', T['akatext'] if j == len(steps)-1 else T['text'], ls=2))
        if j < len(steps) - 1:
            tw = D.measure(st, 11, 'mono700', 2)
            b.append(f'<line class="flow" x1="{sx+22+tw}" y1="{H-26}" x2="{xs[j+1]-12}" y2="{H-26}" stroke="{AKA}" stroke-width="1.5" stroke-dasharray="6 6"/>')
    b.append(frame(W, H, T, 1, 2))
    alt = ('Automation. Browser and HTTP: Playwright and Camoufox where a page needs a real browser, curl_cffi and aiohttp where it does not, '
           'async pipelines with retries, proxy pools and per-account profiles, a React and Flask dashboard. Mail and auth flows: IMAP polling '
           'for verification links and OTP codes, OAuth 2.0 chains, session cookies and 2FA scripted end to end. Bots and schedulers: aiogram '
           'Telegram bots with a publishing queue (igtg, 251 tests), weekly report jobs, lead collection from OpenStreetMap, GitHub Actions and Azure Functions.')
    write('automation', T, D.svg(W, H, '\n'.join(b), alt, style))

OPS = [
    ('TICKET MANAGER', '券', 'OPS DESK · PRIVATE REPO',
     'Support case desk for a fleet of accounts: CSV import, OAuth login chain, 2FA codes over IMAP, per-account proxies and sessions, batch case creation with delays and a stop button. FastAPI + WebSocket live feed, SQLite, Vite SPA. 9k lines of Python.',
     'FASTAPI · WEBSOCKET · AIOHTTP · SQLITE · VITE'),
    ('ACCOUNT AUTOMATION', '運用', 'CLOUDFLARE · YOUTUBE · INSTAGRAM · TIKTOK',
     'Registration and onboarding flows for Cloudflare, YouTube, Instagram and TikTok. Camoufox where the page needs a real browser, pure requests on curl_cffi where it does not: 30 to 40 seconds per account, mail verification and OTP parsing, proxy pools, results to JSON and CSV, errors to a journal, live console dashboard.',
     'CAMOUFOX · CURL_CFFI · IMAP · PROXIES · CSV'),
]

def ops_panel(T):
    W, H = 900, 250; D = Doc(); dark = T['name'] == 'dark'; CW = W / 2
    b = ['<defs>' + ''.join(f'<clipPath id="o{i}"><rect x="{i*CW}" y="0" width="{CW}" height="{H}"/></clipPath>' for i in range(2)) + '</defs>',
         f'<rect width="{W}" height="{H}" fill="{T["panel"]}"/>']
    for i, (title, kanji, stamp, body, tech) in enumerate(OPS):
        x = i * CW
        if i: b.append(f'<line x1="{x}" y1="18" x2="{x}" y2="{H-18}" stroke="{T["line"]}" stroke-width="1.5"/>')
        b.append(f'<g clip-path="url(#o{i})">' + dots(halftone_x(x + CW - 150, x + CW, 0, H, 6, 1.2), T['tone'], .2 if dark else .12)
                 + D.text(kanji, x + CW - 14, H - 16, 110, 'sans900', T['wine'], anchor='end', opacity=T['wine_op']) + '</g>')
        b.append(tab(x, 0, 46, 28, AKA))
        b.append(D.text(f'0{i+1}', x + 23, 19, 11, 'mono700', PAPER, ls=2, anchor='middle'))
        b.append(D.text(stamp, x + CW - 22, 19, 10.5, 'mono700', T['akatext'], ls=2, anchor='end'))
        b.append(D.text(title, x + 24, 66, 17, 'sans900', T['text'], ls=2))
        inner = CW - 48
        lines = D.wrap(body, 12.5, 'sans400', inner)
        assert len(lines) <= 6, (title, len(lines))
        assert D.measure(tech, 10.5, 'mono500', 1.2) <= inner, tech
        y = 94
        for ln in lines:
            b.append(D.text(ln, x + 24, y, 12.5, 'sans400', T['text'], opacity=.84)); y += 18
        b.append(f'<rect x="{x+24}" y="{H-42}" width="28" height="2.5" fill="{AKA}"/>')
        b.append(D.text(tech, x + 24, H - 20, 10.5, 'mono500', T['muted'], ls=1.2))
    b.append(frame(W, H, T, 1, 2))
    alt = ('Ticket Manager, private repo: support case desk for a fleet of accounts with CSV import, OAuth login chain, 2FA over IMAP, '
           'per-account proxies, batch case creation, FastAPI and WebSocket live feed, SQLite, Vite SPA, 9k lines of Python. '
           'Account automation for Cloudflare, YouTube, Instagram and TikTok on Camoufox and curl_cffi: mail verification, OTP parsing, '
           'proxy pools, results to JSON and CSV, live console dashboard.')
    write('ops', T, D.svg(W, H, '\n'.join(b), alt))

CLIENTS = [
    ('Finance Bridge', 'LIVE', 'Landing for an accounting firm in Kazakhstan.', 'REACT 19 · VITE 7 · TAILWIND 4 · TIKTOK EVENTS API'),
    ('SHADE Creative People Club', 'LIVE', 'Site for the KBTU creative club: drawing, art therapy, crafts.', 'REACT · VITE · TAILWIND 4 · FRAMER MOTION · QR'),
]

def client_grid(T):
    RH = 96; rows = (len(CLIENTS) + 1) // 2; W, H = 900, 20 + rows * RH; D = Doc(); dark = T['name'] == 'dark'; CW = W / 2
    b = [f'<rect width="{W}" height="{H}" fill="{T["panel"]}"/>',
         dots(halftone_x(W - 150, W, 0, H, 6, 1.2), T['tone'], .2 if dark else .12)]
    for i, (name, tag, desc, tech) in enumerate(CLIENTS):
        x = (i % 2) * CW; y = 12 + (i // 2) * RH
        b.append(tab(x + 12, y + 4, 30, 22, AKA))
        b.append(D.text(f'0{i+1}', x + 27, y + 19.5, 10.5, 'mono700', PAPER, ls=1, anchor='middle'))
        b.append(D.text(name, x + 54, y + 21, 15.5, 'sans900', T['text']))
        b.append(D.text(tag, x + CW - 18, y + 20, 10.5, 'mono700', T['akatext'] if tag == 'LIVE' else T['muted'], ls=2, anchor='end'))
        b.append(D.text(desc, x + 54, y + 42, 12.5, 'sans400', T['text'], opacity=.84))
        b.append(D.text(tech, x + 54, y + 60, 10.5, 'mono500', T['muted'], ls=.8))
        assert D.measure(tech, 10.5, 'mono500', .8) < CW - 72 and D.measure(desc, 12.5, 'sans400') < CW - 72, name
        if i < len(CLIENTS) - 2: b.append(f'<line x1="{x+54}" y1="{y+RH-6:.1f}" x2="{x+CW-18}" y2="{y+RH-6:.1f}" stroke="{T["line"]}" stroke-width="1.2"/>')
    b.append(f'<line x1="{CW}" y1="18" x2="{CW}" y2="{H-18}" stroke="{T["line"]}" stroke-width="1.5"/>')
    b.append(frame(W, H, T, 1, 2))
    alt = ('Frontend. Finance Bridge: landing for an accounting firm in Kazakhstan, React 19, Vite 7, Tailwind 4, TikTok Events API, live. '
           'SHADE Creative People Club: site for the KBTU creative club, React, Vite, Tailwind 4, Framer Motion, QR code, live. '
           '')
    write('clients', T, D.svg(W, H, '\n'.join(b), alt))

def divider(T):
    """katana divider between chapters: blade across the column, a glint that runs along it"""
    W, H = 900, 54; D = Doc(); dark = T['name'] == 'dark'
    style = '@keyframes dg{0%{transform:translateX(0) skewX(-30deg)}100%{transform:translateX(720px) skewX(-30deg)}}.dg{animation:dg 3s cubic-bezier(.4,0,.2,1) infinite}'
    b = [f'<line x1="0" y1="27" x2="900" y2="27" stroke="{AKA}" stroke-opacity=".25"/>',
         f'<g transform="translate(40 27)">{katana(T, 820, "dg")}</g>',
         D.text('斬', 892, 40, 22, 'sans900', T['wine'] if dark else AKA, anchor='end', opacity=.9 if dark else .5)]
    write('divider', T, D.svg(W, H, '\n'.join(b), 'Katana divider', style))

def katana_panel(T):
    """next-episode companion: a katana over the red sun, focus lines, blood drops; replaces the external GIF"""
    W = 448; H = round(W * (0.5 * 280 / 498) / 0.498); D = Doc(); dark = T['name'] == 'dark'
    SX, SY, SR = 250, 132, 92; rnd = random.Random(21)
    style = ('@keyframes kp{0%{transform:translateX(0) skewX(-30deg)}100%{transform:translateX(300px) skewX(-30deg)}}.kp{animation:kp 2.2s cubic-bezier(.2,.7,.2,1) infinite}'
             + ''.join(f'@keyframes dr{i}{{0%{{transform:translateY(0);opacity:0}}10%{{opacity:1}}100%{{transform:translateY({70+i*20}px);opacity:0}}}}.dr{i}{{animation:dr{i} {2.4+i*.7:.1f}s ease-in {i*.9:.1f}s infinite}}' for i in range(3)))
    b = [f'<defs><clipPath id="pf"><rect width="{W}" height="{H}"/></clipPath></defs>',
         f'<rect width="{W}" height="{H}" fill="{T["panel"]}"/>', '<g clip-path="url(#pf)">',
         dots(halftone_ring(SX, SY, SR, 120, 0, W, 0, H, 7, 2.2), T['tone'], .5 if dark else .35)]
    ls = []
    for i in range(40):
        a = math.radians(rnd.uniform(0, 360)); r1 = rnd.uniform(SR + 10, SR + 40); r2 = 330
        ls.append(f'<line x1="{SX+r1*math.cos(a):.0f}" y1="{SY+r1*math.sin(a):.0f}" x2="{SX+r2*math.cos(a):.0f}" y2="{SY+r2*math.sin(a):.0f}" stroke-width="{rnd.uniform(.6,2):.1f}"/>')
    b.append(f'<g stroke="{AKA}" opacity=".55">{"".join(ls)}</g>')
    b.append(f'<circle cx="{SX}" cy="{SY}" r="{SR}" fill="{AKA}"/>')
    b.append(D.text('斬', W - 16, H - 18, 96, 'sans900', T['wine'], anchor='end', opacity=T['wine_op'] * 1.1))
    b.append(f'<g transform="translate(36 {H-26}) rotate(-38)">{katana(T, 400, "kp")}</g>')
    for i, (dx, dy) in enumerate([(300, 96), (322, 78), (284, 112)]):
        b.append(f'<path class="dr{i}" d="M{dx} {dy} c-3 5 -3 9 0 11 c3 -2 3 -6 0 -11z" fill="{T["hot"]}"/>')
    b.append('</g>')
    b.append(D.text('一刀', 24, 40, 24, 'sans900', T['text'], ls=2))
    b.append(D.text('ONE CUT · SHIPPED', 24, 58, 10.5, 'mono700', T['akatext'], ls=3))
    b.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" fill="none" stroke="{T["frame"]}" stroke-opacity="{T["frame_op"]}" stroke-width="2"/>')
    write('katana', T, D.svg(W, H, '\n'.join(b), 'A katana drawn across the red sun, focus lines, three drops', style))

if __name__ == '__main__':
    for T in (DARK, LIGHT):
        divider(T)
        katana_panel(T)
        auto_panel(T)
        ops_panel(T)
        client_grid(T)
        lab_panel(T)
        chapter(T, '04', '第四話', 'AUTOMATION', 'BROWSERS  ·  MAIL AND AUTH  ·  BOTS  ·  TICKET MANAGER  ·  ACCOUNTS', 'Chapter 4: automation')
        chapter(T, '06', '第六話', 'FRONTEND', 'FINANCE BRIDGE  ·  SHADE CREATIVE PEOPLE CLUB  ·  REACT  ·  VITE  ·  TAILWIND', 'Chapter 6: frontend')
        chapter(T, '05', '第五話', 'IN THE LAB', 'FOOTFALL  ·  FACETABEL  ·  SPREAD SCANNER  ·  SEPTEMBER 2026', 'Chapter 5: in the lab')
