#!/usr/bin/env python3
"""Chapter 3, the workshop: automation and lab builds as one tile grid (echoing the arsenal), the frontend page of
screenshots, and the Kuniyoshi print for the next episode. Also runs the katana dividers."""
from build_assets import *
from katana import Katana
from dividers import divider_saya, divider_draw, divider_daisho

# (title, tag, kanji watermark, one line, tech)
WORKSHOP = [
    ('01', '忍', 'AUTOMATION', [
        ('Ticket Manager', 'PRIVATE REPO', '券', 'Support desk for an account fleet. 9k lines.', 'FASTAPI · WEBSOCKET'),
        ('Account automation', '4 PLATFORMS', '運', 'Onboarding for Cloudflare, YouTube, Instagram, TikTok.', 'CAMOUFOX · CURL_CFFI'),
        ('Mail and bots', 'PIPELINES', '電', 'OTP over IMAP, OAuth chains, aiogram control bots.', 'IMAP · OAUTH · AIOGRAM')]),
    ('02', '験', 'IN THE LAB', [
        ('Footfall', 'PEOPLE COUNTER', '人', 'People counter on cameras a shop already has.', 'OPENCV · YOLOX · RTSP'),
        ('FaceTabel', 'STAFF CHECK-IN', '顔', 'Consent-only face check-in for staff.', 'YUNET · SFACE · OPENCV'),
        ('Spread Scanner', 'CRYPTO ARBITRAGE', '差', 'Spot and funding spreads across seven exchanges.', 'ASYNCIO · 7 EXCHANGES')]),
]

def workshop(T):
    W = 900; D = Doc(); dark = T['name'] == 'dark'
    top, TH, RG = 22, 122, 14; GX0, GX1 = 214, 880; TG = 12; TW = (GX1 - GX0 - 2 * TG) / 3
    H = top + 2 * TH + RG + 50
    tile_bg = INK if dark else '#ffffff'
    style = ('@keyframes rv{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}'
             + ''.join(f'.t{i}{{animation:rv .5s cubic-bezier(.16,1,.3,1) {0.15 + i*0.06:.2f}s both}}' for i in range(8))
             + '@keyframes gl{0%{transform:translateX(0)}40%,100%{transform:translateX(900px)}}.gl{animation:gl 6s cubic-bezier(.4,0,.2,1) 2.4s infinite}'
             + '@keyframes hot{0%,100%{opacity:1}50%{opacity:.3}}.hot{animation:hot 2.4s ease-in-out infinite}')
    b = [f'<rect width="{W}" height="{H}" fill="{T["panel"]}"/>', dots(halftone_x(W - 160, W, 0, H, 7, 1.4), T['tone'], .2 if dark else .12)]
    clips, k = [], 0
    for r, (num, kanji, cat, items) in enumerate(WORKSHOP):
        ry = top + r * (TH + RG)
        b.append(f'<g class="t{k}">' + tab(20, ry + 4, 38, 22, AKA) + D.text(num, 39, ry + 19.5, 11, 'mono700', PAPER, ls=1, anchor='middle')
                 + D.text(kanji, 86, ry + 25, 22, 'sans900', T['akatext'])
                 + D.text(cat, 21, ry + 50, 11.5, 'mono700', T['text'], ls=3)
                 + f'<rect x="20" y="{ry + 60}" width="{GX0 - 36}" height="1.5" fill="{T["line"]}"/>' + '</g>')
        k += 1
        for c, (title, tag, wm, line, tech) in enumerate(items):
            x = GX0 + c * (TW + TG); y = ry; inner = TW - 28
            clips.append(f'<rect x="{x:.1f}" y="{y}" width="{TW:.1f}" height="{TH}" rx="3"/>')
            fs = 17
            while D.measure(title, fs, 'sans900') > inner: fs -= .5
            lines = D.wrap(line, 12.5, 'sans400', inner)
            assert len(lines) <= 2, (title, lines)
            assert D.measure(tech, 10, 'mono500', 1) <= inner and D.measure(tag, 10, 'mono700', 2) <= inner, (tag, tech)
            g = [f'<clipPath id="k{r}{c}"><rect x="{x:.1f}" y="{y}" width="{TW:.1f}" height="{TH}" rx="3"/></clipPath>',
                 f'<rect x="{x:.1f}" y="{y}" width="{TW:.1f}" height="{TH}" rx="3" fill="{tile_bg}" stroke="{T["line"]}" stroke-width="1.2"/>',
                 f'<g clip-path="url(#k{r}{c})">' + D.text(wm, x + TW - 6, y + TH + 8, 78, 'sans900', T['wine'], anchor='end', opacity=T['wine_op'] * .75) + '</g>',
                 D.text(tag, x + 14, y + 23, 10, 'mono700', T['akatext'], ls=2),
                 D.text(title, x + 14, y + 50, fs, 'sans900', T['text'])]
            ly = y + 72
            for ln in lines:
                g.append(D.text(ln, x + 14, ly, 12.5, 'sans400', T['text'], opacity=.84)); ly += 17
            g.append(D.text(tech, x + 14, y + TH - 13, 10, 'mono500', T['muted'], ls=1))
            b.append(f'<g class="t{k}">' + ''.join(g) + '</g>'); k += 1
    b.append(f'<defs><clipPath id="tc">{"".join(clips)}</clipPath><linearGradient id="glg" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
             f'<stop offset=".5" stop-color="#fff" stop-opacity="{.1 if dark else .45}"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>')
    b.append(f'<g clip-path="url(#tc)"><g class="gl"><rect x="-120" y="0" width="80" height="{H}" fill="url(#glg)" transform="skewX(-20)"/></g></g>')
    fy = H - 20
    b.append(f'<circle class="hot" cx="{GX0 + 5}" cy="{fy - 4}" r="4" fill="{T["hot"]}"/>'
             + D.text('IN PROGRESS', GX0 + 18, fy, 10.5, 'mono700', T['muted'], ls=2.5)
             + D.text('工房', GX1, fy + 1, 12, 'sans700', T['akatext'], anchor='end')
             + D.text('PRIVATE REPOS', GX1 - D.measure('工房', 12, 'sans700') - 12, fy, 10.5, 'mono700', T['muted'], ls=2.5, anchor='end'))
    b.append(frame(W, H, T))
    alt = 'Workshop. ' + ' '.join(f'{cat.title()}: ' + '; '.join(f'{t}, {l[0].lower() + l[1:].rstrip(".")}' for t, _, _, l, _ in items) + '.' for _, _, cat, items in WORKSHOP)
    write('workshop', T, D.svg(W, H, '\n'.join(b), alt, style))

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
        workshop(T)
        next_panel(T)
    fe_pages()
    print_panel()
