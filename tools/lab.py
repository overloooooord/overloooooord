#!/usr/bin/env python3
"""Chapter 6, the lab: three builds from September 2026 that live in private repos (Footfall, FaceTabel, Spread Scanner)."""
from build_assets import *
from katana import Katana
from dividers import divider_saya, divider_draw, divider_daisho

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
    ('rdrightnow.com', 'LIVE', 'Multi-page site for an engineering studio: canvas hero, scroll reveals, stack ticker, contact form on Azure Functions.', 'HTML · CSS · JS · AZURE FUNCTIONS'),
    ('InVision U', 'LIVE', 'Admissions portal: application form, MBTI and language tests in RU, KZ and EN, and a review panel for the selection committee.', 'HTML · CSS · VANILLA JS · I18N'),
    ('SHADE', 'LIVE', 'Site for the KBTU creative club: drawing, art therapy, crafts, a links hub with a QR code.', 'REACT · VITE · TAILWIND 4 · MOTION'),
]

def client_grid(T):
    """three front ends side by side: name, status, two lines of what it is, the stack"""
    W, H = 900, 150; D = Doc(); dark = T['name'] == 'dark'; CW = W / 3
    b = [f'<rect width="{W}" height="{H}" fill="{T["panel"]}"/>', dots(halftone_x(W - 150, W, 0, H, 6, 1.2), T['tone'], .2 if dark else .12)]
    for i, (name, tag, desc, tech) in enumerate(CLIENTS):
        x = i * CW
        if i: b.append(f'<line x1="{x}" y1="18" x2="{x}" y2="{H - 18}" stroke="{T["line"]}" stroke-width="1.5"/>')
        b.append(tab(x, 0, 40, 26, AKA))
        b.append(D.text(f'0{i+1}', x + 20, 17.5, 10.5, 'mono700', PAPER, ls=1, anchor='middle'))
        b.append(D.text(tag, x + CW - 20, 18, 10.5, 'mono700', T['akatext'], ls=2, anchor='end'))
        b.append(D.text(name, x + 22, 56, 17, 'sans900', T['text']))
        lines = D.wrap(desc, 12.5, 'sans400', CW - 44)
        assert len(lines) <= 3, (name, lines)
        y = 80
        for ln in lines:
            b.append(D.text(ln, x + 22, y, 12.5, 'sans400', T['text'], opacity=.84)); y += 17
        assert D.measure(tech, 10.5, 'mono500', .8) < CW - 40, tech
        b.append(D.text(tech, x + 22, H - 16, 10.5, 'mono500', T['muted'], ls=.8))
    b.append(frame(W, H, T, 1, 2))
    alt = 'Frontend. ' + ' '.join(f'{n}: {d} {t.title()}. ' for n, _, d, t in CLIENTS)
    write('clients', T, D.svg(W, H, '\n'.join(b), alt))

def fe_pages():
    """the three sites as one manga page: a big panel and two stacked ones, slanted gutters, kanji tabs"""
    W, H = 900, 420; D = Doc()
    top_l, top_r = 22, 6
    ytop = lambda x: top_l + (top_r - top_l) * x / W
    # left: rdrightnow.com, slanted right edge
    xl0, xl1t, xl1b, yb = 10, 560, 536, 410
    dl = f'M{xl0} {ytop(xl0):.1f} L{xl1t} {ytop(xl1t):.1f} L{xl1b} {yb} L{xl0} {yb} Z'
    src, (iw, ih) = jpeg_data(SHOTS / 'rdrightnow-home.jpg', 1100, q=84, tone=True)
    ph = yb - ytop(xl0); pw = ph * iw / ih
    b = [f'<defs><clipPath id="l"><path d="{dl}"/></clipPath>']
    # right column: two panels split by a slanted gutter
    xr0t, xr0b, xr1 = 576, 552, 890
    ym_l, ym_r = 212, 196                     # gutter between InVision U and SHADE
    dt = f'M{xr0t} {ytop(xr0t):.1f} L{xr1} {ytop(xr1):.1f} L{xr1} {ym_r} L{xr0t - (xr0t - xr0b) * (ym_l - ytop(xr0t)) / (yb - ytop(xr0t)):.1f} {ym_l} Z'
    xg = xr0t - (xr0t - xr0b) * (ym_l + 14 - ytop(xr0t)) / (yb - ytop(xr0t))
    db = f'M{xg:.1f} {ym_l + 14} L{xr1} {ym_r + 14} L{xr1} {yb} L{xr0b} {yb} Z'
    b.append(f'<clipPath id="t"><path d="{dt}"/></clipPath><clipPath id="bb"><path d="{db}"/></clipPath></defs>')
    b.append(f'<image href="{src}" x="{xl0}" y="{ytop(xl0):.1f}" width="{pw:.1f}" height="{ph:.1f}" clip-path="url(#l)" preserveAspectRatio="xMinYMin slice"/>')
    for fn, clip, y0, h in (('invision-home.jpg', 't', ytop(xr0b), ym_l - ytop(xr0b)), ('shade-home.jpg', 'bb', ym_r + 14, yb - ym_r - 14)):
        s2, (w2, h2) = jpeg_data(SHOTS / fn, 760, crop=(170, 40, 1270, 730) if fn.startswith('invision') else None, q=84, tone=True)
        ww = xr1 - xr0b + 30; hh = ww * h2 / w2
        b.append(f'<image href="{s2}" x="{xr0b - 20}" y="{y0 - 4:.1f}" width="{ww:.1f}" height="{hh:.1f}" clip-path="url(#{clip})" preserveAspectRatio="xMinYMin slice"/>')
    for d in (dl, dt, db):
        b.append(ink_frame(d))
    for (x, y, kanji, cap, fill) in ((26, ytop(26) - 18, '研究', 'RDRIGHTNOW.COM', AKA), (xr0t + 14, ytop(xr0t + 14) - 18, '入学', 'INVISION U', INK), (xg + 16, ym_l + 2, '美術', 'SHADE', AKA)):
        t, tw = kanji_tab(D, x, y, kanji, fill=fill)
        b.append(t)
        b.append(caption_box(D, x + tw + 22, y + 4, [cap]))
    write_neutral('fe-pages', D.svg(W, H, '\n'.join(b), 'Three front ends: rdrightnow.com with its R and D hero, the InVision U admissions portal, SHADE creative club site'))

def print_panel():
    """next episode: a ronin drawing his sword, Utagawa Kuniyoshi, 1847 (public domain), printed in ink and red"""
    W, H = 448, 300; D = Doc()
    src, (iw, ih) = jpeg_data(SHOTS / 'kuniyoshi-onodera-duotone.jpg', 896, q=84)
    d = f'M4 4 H{W - 4} V{H - 4} H4 Z'
    b = [f'<defs><clipPath id="pp"><path d="{d}"/></clipPath></defs>',
         f'<image href="{src}" x="4" y="4" width="{W - 8}" height="{H - 8}" clip-path="url(#pp)" preserveAspectRatio="xMidYMid slice"/>',
         ink_frame(d)]
    t, tw = kanji_tab(D, 16, 12, '忠臣')
    b.append(t)
    b.append(caption_box(D, W - 14, H - 42, ['UTAGAWA KUNIYOSHI · 1847'], 10.5, 'mono700', anchor='end'))
    write_neutral('print', D.svg(W, H, '\n'.join(b), 'Onodera Junai Hidetomo drawing his sword, from Seichu gishi den by Utagawa Kuniyoshi, 1847, printed in ink and red'))

if __name__ == '__main__':
    for T in (DARK, LIGHT):
        divider_saya(T)
        divider_draw(T)
        divider_daisho(T)
        auto_panel(T)
        ops_panel(T)
        client_grid(T)
        next_panel(T)
        lab_panel(T)
        chapter(T, '04', '第四話', 'AUTOMATION', 'BROWSERS  ·  MAIL AND AUTH  ·  BOTS  ·  TICKET MANAGER  ·  ACCOUNTS', 'Chapter 4: automation')
        chapter(T, '06', '第六話', 'FRONTEND', 'RDRIGHTNOW.COM  ·  INVISION U  ·  SHADE  ·  REACT  ·  VITE  ·  AZURE', 'Chapter 6: frontend')
        chapter(T, '05', '第五話', 'IN THE LAB', 'FOOTFALL  ·  FACETABEL  ·  SPREAD SCANNER  ·  SEPTEMBER 2026', 'Chapter 5: in the lab')
    fe_pages()
    print_panel()
