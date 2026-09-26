#!/usr/bin/env python3
"""Contribution turtle: a ninja turtle walks the contribution grid column by column and cuts every day
that has commits. An original turtle (red headband, two katanas on the shell), drawn for this profile.

Runs daily in GitHub Actions (.github/workflows/turtle.yml). Standard library only, no fonts needed.
usage: contrib_turtle.py --user overloooooord --out dist [--data calendar.json]
Writes dist/turtle.svg (GitHub light theme) and dist/turtle-dark.svg (dark theme).
The token comes from GITHUB_TOKEN (Actions) or GH_TOKEN.
"""
import argparse, json, os, urllib.request
from pathlib import Path

P = 15; S = 12                      # grid pitch and cell size, same as GitHub's own calendar
MX, MY = 30, 30                     # margins leave room for the turtle to walk past the edges
STEP = 0.085                        # seconds per cell
PAUSE = 2.6                         # rest at the end, then the grid grows back

THEMES = {
    'light': dict(cells=['#ebe4da', '#f2b3bc', '#e2717e', '#c8102e', '#6e0a18'], cut='#ebe4da', slash='#c8102e', flash='#0b0b0d'),
    'dark': dict(cells=['#1f1a1d', '#4a0d17', '#7a0a1a', '#c8102e', '#ff2a2a'], cut='#1f1a1d', slash='#ff2a2a', flash='#ffffff'),
}


def fetch(user, token):
    q = ('query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{'
         'weeks{contributionDays{date contributionCount weekday}}}}}}')
    req = urllib.request.Request('https://api.github.com/graphql', method='POST',
                                 data=json.dumps({'query': q, 'variables': {'login': user}}).encode(),
                                 headers={'Authorization': f'bearer {token}', 'Content-Type': 'application/json',
                                          'User-Agent': 'contribution-turtle'})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    weeks = data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
    return [[(d['weekday'], d['contributionCount'], d['date']) for d in w['contributionDays']] for w in weeks]


def levels(weeks):
    counts = sorted(c for w in weeks for _, c, _ in w if c > 0)
    if not counts:
        return lambda c: 0
    q = [counts[int(len(counts) * f)] for f in (0.25, 0.5, 0.75)]
    return lambda c: 0 if c == 0 else 1 if c <= q[0] else 2 if c <= q[1] else 3 if c <= q[2] else 4


def turtle_sprite(dark):
    """top-down turtle facing +x, about 30 px long, centred on the origin"""
    skin, skin_d = '#7f9b69', '#4f6a42'
    shell, scute, rim = '#2c3527', '#6f8a5c', '#1a2016'
    band = '#c8102e'
    legs = ''.join(
        f'<ellipse class="leg{"a" if i in (0, 3) else "b"}" cx="{x}" cy="{y}" rx="4.2" ry="2.6" fill="{skin}" stroke="{skin_d}" stroke-width=".8" transform="rotate({r} {x} {y})"/>'
        for i, (x, y, r) in enumerate(((6, -9, -35), (6, 9, 35), (-7, -8.5, 35), (-7, 8.5, -35))))
    scutes = ('<path d="M-4 -3.2 L1 -3.2 L3.6 0 L1 3.2 L-4 3.2 L-6.4 0 Z" fill="#35412e" stroke="{c}" stroke-width=".9"/>'
              '<path d="M1 -3.2 L3 -7 M1 3.2 L3 7 M-4 -3.2 L-6 -7 M-4 3.2 L-6 7 M3.6 0 L8.4 0 M-6.4 0 L-10 0" stroke="{c}" stroke-width=".9"/>').format(c=scute)
    # two katanas crossed on the back: black scabbards, red wraps sticking out past the head end
    swords = ('<g stroke-linecap="round">'
              '<path d="M-13 5.6 L7.4 -6.2" stroke="#5e0714" stroke-width="1.9"/><path d="M-13 -5.6 L7.4 6.2" stroke="#5e0714" stroke-width="1.9"/>'
              '<path d="M-13 5.6 L-11.4 4.7 M-13 -5.6 L-11.4 -4.7" stroke="#c9a961" stroke-width="2"/>'
              '<path d="M8.4 -6.8 L12.6 -9.2 M8.4 6.8 L12.6 9.2" stroke="#c8102e" stroke-width="2.3"/>'
              '<path d="M7.6 -8.2 L9 -5.4 M7.6 8.2 L9 5.4" stroke="#c9a961" stroke-width="1.5"/></g>')
    head = (f'<ellipse cx="14.5" cy="0" rx="5" ry="4.2" fill="{skin}" stroke="{skin_d}" stroke-width=".8"/>'
            f'<path d="M12.2 -4 Q14.6 -4.8 16.6 -3.8 L16.6 3.8 Q14.6 4.8 12.2 4 Z" fill="{band}"/>'
            f'<circle cx="15.6" cy="-1.9" r=".9" fill="#ffffff"/><circle cx="15.6" cy="1.9" r=".9" fill="#ffffff"/>'
            f'<g class="tails"><path d="M11.8 -1.4 C8 -3 6 -2 3.6 -4.6" stroke="{band}" stroke-width="1.6" fill="none" stroke-linecap="round"/>'
            f'<path d="M11.8 1.4 C8.4 3.4 6.4 3 4 5.4" stroke="{band}" stroke-width="1.6" fill="none" stroke-linecap="round"/></g>')
    tail = f'<path d="M-11.5 0 L-15.5 -1.2 L-15.5 1.2 Z" fill="{skin}" stroke="{skin_d}" stroke-width=".6"/>'
    body = (f'<ellipse cx="-1" cy="0" rx="11.6" ry="9.6" fill="{shell}" stroke="{rim}" stroke-width="1.4"/>' + scutes + swords
            + '<ellipse cx="-2" cy="-4" rx="6" ry="2.2" fill="#ffffff" opacity=".12"/>')
    outline = '<ellipse cx="-1" cy="0" rx="12.6" ry="10.6" fill="none" stroke="#f3ede4" stroke-width=".8" opacity=".35"/>' if dark else ''
    return legs + tail + body + head + outline


def build(weeks, theme):
    th = THEMES[theme]; dark = theme == 'dark'
    lvl = levels(weeks)
    ncol = len(weeks)
    W = MX * 2 + ncol * P - (P - S); H = MY * 2 + 7 * P - (P - S)
    steps = ncol * 7 - 1
    t_walk = steps * STEP; T = t_walk + PAUSE; wf = t_walk / T
    cx = lambda c: MX + c * P + S / 2
    cy = lambda r: MY + r * P + S / 2
    # boustrophedon path through every cell centre, and the time the turtle reaches each cell
    pts = []
    for c in range(ncol):
        rows = range(7) if c % 2 == 0 else range(6, -1, -1)
        for r in rows:
            pts.append((c, r))
    when = {cell: i * STEP for i, cell in enumerate(pts)}
    d = 'M' + ' L'.join(f'{cx(c):.1f} {cy(r):.1f}' for c, r in [pts[0]] + [p for i, p in enumerate(pts) if i and (pts[i - 1][0] != p[0] or p[1] in (0, 6))])
    css = [f'.legA{{animation:paddle .34s ease-in-out infinite alternate}}.legB{{animation:paddle .34s ease-in-out -.34s infinite alternate}}'
           f'.legA,.legB{{transform-box:fill-box;transform-origin:center}}'
           f'@keyframes paddle{{from{{transform:rotate(-18deg)}}to{{transform:rotate(18deg)}}}}'
           f'.tails{{transform-box:fill-box;transform-origin:100% 50%;animation:flap .3s ease-in-out infinite alternate}}'
           f'@keyframes flap{{from{{transform:rotate(-9deg)}}to{{transform:rotate(9deg)}}}}'
           ]
    cells, slashes = [], []
    for c, w in enumerate(weeks):
        for wd, cnt, date in w:
            L = lvl(cnt); x, y = MX + c * P, MY + wd * P
            if L == 0:
                cells.append(f'<rect x="{x}" y="{y}" width="{S}" height="{S}" rx="2" fill="{th["cells"][0]}"/>')
                continue
            p = when[(c, wd)] / T * 100
            name = f'c{c}_{wd}'
            cells.append(f'<rect class="{name}" x="{x}" y="{y}" width="{S}" height="{S}" rx="2" fill="{th["cells"][L]}"/>')
            css.append(f'@keyframes {name}{{0%,{p:.2f}%{{fill:{th["cells"][L]}}}{p + 0.35:.2f}%,93%{{fill:{th["cut"]}}}98%,100%{{fill:{th["cells"][L]}}}}}'
                       f'.{name}{{animation:{name} {T:.2f}s linear infinite}}')
            slashes.append(f'<path class="s{name}" d="M{x + 2} {y + S - 2} L{x + S - 2} {y + 2}" stroke-width="1.8" stroke-linecap="round" opacity="0"/>')
            css.append(f'@keyframes s{name}{{0%,{p:.2f}%{{opacity:0;stroke:{th["flash"]}}}{p + 0.2:.2f}%{{opacity:1;stroke:{th["flash"]}}}{p + 1.2:.2f}%,92%{{opacity:1;stroke:{th["slash"]}}}96%,100%{{opacity:0;stroke:{th["slash"]}}}}}'
                       f'.s{name}{{animation:s{name} {T:.2f}s linear infinite}}')
    motion = (f'<animateMotion dur="{T:.2f}s" repeatCount="indefinite" rotate="auto" keyPoints="0;1;1" keyTimes="0;{wf:.4f};1" calcMode="linear" path="{d}"/>')
    # fade in at the start and out after the last column, on the same SMIL clock as the walk
    fade = (f'<animate attributeName="opacity" dur="{T:.2f}s" repeatCount="indefinite" values="0;1;1;0;0" '
            f'keyTimes="0;0.015;{min(wf + 0.02, 0.97):.4f};{min(wf + 0.05, 0.99):.4f};1" calcMode="linear"/>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
           f'aria-label="A ninja turtle with a red headband walks the contribution calendar and cuts every day with commits">'
           f'<style>{"".join(css)}</style>'
           f'<g>{"".join(cells)}</g><g fill="none">{"".join(slashes)}</g>'
           f'<g opacity="1">{fade}<g>{turtle_sprite(dark)}{motion}</g></g></svg>')
    return svg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--user', default='overloooooord'); ap.add_argument('--out', default='dist'); ap.add_argument('--data')
    a = ap.parse_args()
    if a.data:
        weeks = json.loads(Path(a.data).read_text())
    else:
        token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
        if not token:
            raise SystemExit('set GITHUB_TOKEN or GH_TOKEN')
        weeks = fetch(a.user, token)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    (out / 'turtle.svg').write_text(build(weeks, 'light'))
    (out / 'turtle-dark.svg').write_text(build(weeks, 'dark'))
    lit = sum(1 for w in weeks for _, c, _ in w if c)
    print(f'turtle: {len(weeks)} weeks, {lit} active days -> {out}/turtle.svg, {out}/turtle-dark.svg')


if __name__ == '__main__':
    main()
