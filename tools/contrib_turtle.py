#!/usr/bin/env python3
"""Contribution log: one panel with the live numbers on top and the contribution calendar under them, where a ninja
turtle walks the grid column by column and cuts every day that has commits. The turtle (red headband, two katanas on
the shell) is original, drawn for this profile.

Runs daily in GitHub Actions (.github/workflows/turtle.yml). Standard library only: the text is set from glyph
outlines baked into data/log-kit.json by log_kit.py, so the runner needs no fonts.
usage: contrib_turtle.py --user overloooooord --out dist [--data calendar.json]
Writes dist/log.svg (GitHub light theme) and dist/log-dark.svg (dark theme).
The token comes from GITHUB_TOKEN (Actions) or GH_TOKEN.
"""
import argparse, datetime as dt, json, os, urllib.request
from pathlib import Path

KIT = json.loads((Path(__file__).resolve().parent / 'data' / 'log-kit.json').read_text())
W, H = 900, 344
P = 15; S = 12                      # grid pitch and cell size, same as GitHub's own calendar
X0, Y0 = 54, 170                    # top left cell of the calendar
STEP = 0.085                        # seconds per cell
PAUSE = 2.6                         # rest at the end, then the grid grows back
DECENTRATHON = '2026-04-05'         # the April spike: Decentrathon 5.0, AI inDrive track
MONTHS = 'JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC'.split()


def fetch(user, token):
    q = ('query($login:String!){user(login:$login){repositories(privacy:PUBLIC,ownerAffiliations:OWNER){totalCount}'
         'contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount weekday}}}}}}')
    req = urllib.request.Request('https://api.github.com/graphql', method='POST',
                                 data=json.dumps({'query': q, 'variables': {'login': user}}).encode(),
                                 headers={'Authorization': f'bearer {token}', 'Content-Type': 'application/json',
                                          'User-Agent': 'contribution-turtle'})
    with urllib.request.urlopen(req, timeout=30) as r:
        user = json.load(r)['data']['user']
    cal = user['contributionsCollection']['contributionCalendar']
    weeks = [[(d['weekday'], d['contributionCount'], d['date']) for d in w['contributionDays']] for w in cal['weeks']]
    return {'weeks': weeks, 'total': cal['totalContributions'], 'repos': user['repositories']['totalCount']}


class Glyphs:
    """sets text from the baked outlines: one path def per glyph and a <use> per occurrence, like typeset.Doc"""
    def __init__(self):
        self.ids = {}; self.defs = []

    def _gid(self, style, ch):
        if (style, ch) not in self.ids:
            i = f'g{len(self.ids):x}'; self.ids[(style, ch)] = i
            self.defs.append(f'<path id="{i}" d="{KIT["styles"][style]["glyphs"][ch][1]}"/>')
        return self.ids[(style, ch)]

    def measure(self, s, size, style, ls=0):
        st = KIT['styles'][style]
        return sum(st['glyphs'][c][0] for c in s) * size / st['upm'] + ls * max(0, len(s) - 1)

    def text(self, s, x, y, size, style, fill, ls=0, anchor='start', opacity=None, skew=0):
        st = KIT['styles'][style]; k = size / st['upm']
        w = self.measure(s, size, style, ls)
        x -= w / 2 if anchor == 'middle' else w if anchor == 'end' else 0
        cur = 0.0; uses = []
        for c in s:
            adv, d = st['glyphs'][c]
            if d: uses.append(f'<use href="#{self._gid(style, c)}" x="{int(round(cur))}"/>')
            cur += adv + ls / k
        op = f' opacity="{opacity}"' if opacity is not None else ''
        sk = f' skewX({skew})' if skew else ''
        return f'<g transform="translate({x:.2f} {y:.2f}){sk} scale({k:.5f})" fill="{fill}"{op}>{"".join(uses)}</g>'


def levels(weeks):
    counts = sorted(c for w in weeks for _, c, _ in w if c > 0)
    if not counts:
        return lambda c: 0
    q = [counts[int(len(counts) * f)] for f in (0.25, 0.5, 0.75)]
    return lambda c: 0 if c == 0 else 1 if c <= q[0] else 2 if c <= q[1] else 3 if c <= q[2] else 4


def longest_streak(weeks):
    """(length, first day, last day) of the longest run of days with commits; the latest run wins a tie"""
    best, run, start = (0, None, None), 0, None
    for _, c, d in sorted((x for w in weeks for x in w), key=lambda t: t[2]):
        if c:
            start = d if run == 0 else start; run += 1
            if run >= best[0]: best = (run, start, d)
        else:
            run = 0
    return best


def day_label(iso):
    d = dt.date.fromisoformat(iso); return f'{MONTHS[d.month - 1]} {d.day}'


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


def calendar(weeks, th, dark):
    """the grid, the cut animation and the walking turtle; returns (css, svg)"""
    lvl = levels(weeks); ncol = len(weeks)
    steps = ncol * 7 - 1
    t_walk = steps * STEP; T = t_walk + PAUSE; wf = t_walk / T
    cx = lambda c: X0 + c * P + S / 2
    cy = lambda r: Y0 + r * P + S / 2
    # boustrophedon path through every cell centre, and the time the turtle reaches each cell
    pts = []
    for c in range(ncol):
        for r in (range(7) if c % 2 == 0 else range(6, -1, -1)):
            pts.append((c, r))
    when = {cell: i * STEP for i, cell in enumerate(pts)}
    d = 'M' + ' L'.join(f'{cx(c):.1f} {cy(r):.1f}' for c, r in [pts[0]] + [p for i, p in enumerate(pts) if i and (pts[i - 1][0] != p[0] or p[1] in (0, 6))])
    css = ['.legA{animation:paddle .34s ease-in-out infinite alternate}.legB{animation:paddle .34s ease-in-out -.34s infinite alternate}'
           '.legA,.legB{transform-box:fill-box;transform-origin:center}'
           '@keyframes paddle{from{transform:rotate(-18deg)}to{transform:rotate(18deg)}}'
           '.tails{transform-box:fill-box;transform-origin:100% 50%;animation:flap .3s ease-in-out infinite alternate}'
           '@keyframes flap{from{transform:rotate(-9deg)}to{transform:rotate(9deg)}}']
    empty = th['bg'] if dark else th['cell'][0]      # on the dark panel GitHub's empty grey vanishes: sink them to the page colour
    cut, slash = empty, th['hot']
    cells, slashes = [], []
    for c, w in enumerate(weeks):
        for wd, cnt, date in w:
            L = lvl(cnt); x, y = X0 + c * P, Y0 + wd * P
            if L == 0:
                cells.append(f'<rect x="{x}" y="{y}" width="{S}" height="{S}" rx="2" fill="{empty}"/>')
                continue
            p = when[(c, wd)] / T * 100; name = f'c{c}_{wd}'
            cells.append(f'<rect class="{name}" x="{x}" y="{y}" width="{S}" height="{S}" rx="2" fill="{th["cell"][L]}"/>')
            css.append(f'@keyframes {name}{{0%,{p:.2f}%{{fill:{th["cell"][L]}}}{p + 0.35:.2f}%,93%{{fill:{cut}}}98%,100%{{fill:{th["cell"][L]}}}}}'
                       f'.{name}{{animation:{name} {T:.2f}s linear infinite}}')
            slashes.append(f'<path class="s{name}" d="M{x + 2} {y + S - 2} L{x + S - 2} {y + 2}" stroke-width="1.8" stroke-linecap="round" opacity="0"/>')
            css.append(f'@keyframes s{name}{{0%,{p:.2f}%{{opacity:0;stroke:{th["flash"]}}}{p + 0.2:.2f}%{{opacity:1;stroke:{th["flash"]}}}{p + 1.2:.2f}%,92%{{opacity:1;stroke:{slash}}}96%,100%{{opacity:0;stroke:{slash}}}}}'
                       f'.s{name}{{animation:s{name} {T:.2f}s linear infinite}}')
    motion = f'<animateMotion dur="{T:.2f}s" repeatCount="indefinite" rotate="auto" keyPoints="0;1;1" keyTimes="0;{wf:.4f};1" calcMode="linear" path="{d}"/>'
    # fade in at the start and out after the last column, on the same SMIL clock as the walk
    fade = (f'<animate attributeName="opacity" dur="{T:.2f}s" repeatCount="indefinite" values="0;1;1;0;0" '
            f'keyTimes="0;0.015;{min(wf + 0.02, 0.97):.4f};{min(wf + 0.05, 0.99):.4f};1" calcMode="linear"/>')
    svg = (f'<g>{"".join(cells)}</g><g fill="none">{"".join(slashes)}</g>'
           f'<g class="turtle">{fade}<g>{turtle_sprite(dark)}{motion}</g></g>')
    return css, svg


def panel(data, theme, today):
    th = KIT['themes'][theme]; dark = theme == 'dark'; G = Glyphs(); weeks = data['weeks']
    run, first, last = longest_streak(weeks)
    css = ['@keyframes rv{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}'
           + ''.join(f'.r{i}{{animation:rv .6s cubic-bezier(.16,1,.3,1) {0.1 + i * .08:.2f}s both}}' for i in range(4))
           + '@keyframes run{0%{transform:translateX(0)}100%{transform:translateX(var(--run))}}.run{animation:run 2.6s ease-in-out infinite alternate}']
    b = [f'<rect width="{W}" height="{H}" fill="{th["panel"]}"/>',
         f'<g fill="{th["tone"]}" opacity="{th["dots_op"]}">' + ''.join(f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in th['dots'] if y <= H) + '</g>']
    # header and the three numbers
    b.append(G.text('TRAINING LOG', 28, 34, 11.5, 'mono700', th['akatext'], ls=4)
             + G.text('修行', 28 + G.measure('TRAINING LOG', 11.5, 'mono700', 4) + 10, 35, 12, 'cjk700', th['muted']))
    n = str(run); nw = G.measure(n, 64, 'num900')
    b.append('<g class="r0">' + G.text(n, 33, 127, 64, 'num900', KIT['aka'], skew=-10) + G.text(n, 28, 122, 64, 'num900', th['text'], skew=-10)
             + G.text('DAY COMBO', 28 + nw + 22, 92, 13, 'mono700', th['akatext'], ls=4)
             + G.text('連続', 28 + nw + 22 + G.measure('DAY COMBO', 13, 'mono700', 4) + 10, 93, 15, 'cjk900', th['text'])
             + (G.text(f'{day_label(first)} TO {day_label(last)}', 28 + nw + 23, 114, 11, 'mono500', th['muted'], ls=1) if run else '') + '</g>')
    for i, (x, num, label) in enumerate(((452, f'{data["total"]:,}', 'CONTRIBUTIONS, LAST YEAR'), (690, str(data['repos']), 'PUBLIC REPOSITORIES'))):
        b.append(f'<line x1="{x - 26}" y1="60" x2="{x - 26}" y2="126" stroke="{th["line"]}" stroke-width="1.5"/>')
        b.append(f'<g class="r{i + 1}">' + G.text(num, x, 104, 34, 'num900', th['text']) + G.text(label, x + 1, 124, 10.5, 'mono500', th['muted'], ls=1.5) + '</g>')
    # month labels: the first column whose Sunday falls in a new month, skipping a cramped first label
    labels, prev = [], None
    for c, w in enumerate(weeks):
        m = dt.date.fromisoformat(w[0][2]).month
        if m != prev and (c > 0 or dt.date.fromisoformat(w[0][2]).day <= 7):
            if not labels or c - labels[-1][0] >= 3: labels.append((c, m))
        prev = m
    b.append('<g class="r3">' + ''.join(G.text(MONTHS[m - 1], X0 + c * P, Y0 - 10, 11, 'mono500', th['muted'], ls=1) for c, m in labels) + '</g>')
    cal_css, cal_svg = calendar(weeks, th, dark); css += cal_css
    # annotations under the grid: the longest streak and the Decentrathon spike
    ybot = Y0 + 7 * P - (P - S); yb = ybot + 9
    ann, spans = [], []
    where = {date: (c, wd) for c, w in enumerate(weeks) for wd, _, date in w}
    if run >= 7 and first in where and last in where:
        sx0 = X0 + where[first][0] * P; sx1 = X0 + where[last][0] * P + S
        ann.append(f'<path d="M{sx0} {yb - 5} V{yb} H{sx1} V{yb - 5}" fill="none" stroke="{th["hot"]}" stroke-width="2"/>'
                   f'<rect class="run" style="--run:{max(0, sx1 - sx0 - 14)}px" x="{sx0}" y="{yb - 1.5}" width="14" height="3" fill="{th["text"]}"/>')
        spans.append((sx1 - G.measure('連続', 12, 'cjk900'), sx1))
        ann.append(G.text('連続', sx1, yb + 19, 12, 'cjk900', th['akatext'], anchor='end'))
    if DECENTRATHON in where:
        c, wd = where[DECENTRATHON]; ax, ay = X0 + c * P + S / 2, Y0 + wd * P + S / 2
        t = 'DECENTRATHON 5.0'; tx = ax - 5; tw = G.measure(t, 11, 'mono700', 1.2)
        if not any(tx < b1 + 10 and tx + tw > a1 - 10 for a1, b1 in spans):
            ann.append(f'<circle cx="{ax}" cy="{ay}" r="10" fill="none" stroke="{th["hot"]}" stroke-width="1.5"/>'
                       f'<path d="M{ax} {ay + 10} V{yb + 6}" stroke="{th["hot"]}" stroke-width="1.5" stroke-dasharray="2 3"/>'
                       + G.text(t, tx, yb + 19, 11, 'mono700', th['akatext'], ls=1.2))
    # legend and the date of this drawing
    ly = H - 30
    leg = G.text('LESS', W - 28 - 5 * 15 - 44 - G.measure('MORE', 11, 'mono500', 1), ly + 9.5, 11, 'mono500', th['muted'], ls=1)
    lx = W - 28 - 5 * 15 - G.measure('MORE', 11, 'mono500', 1) - 6
    leg += ''.join(f'<rect x="{lx + i * 15}" y="{ly}" width="{S}" height="{S}" rx="2" fill="{th["bg"] if dark and i == 0 else th["cell"][i]}"/>' for i in range(5))
    leg += G.text('MORE', W - 28, ly + 9.5, 11, 'mono500', th['muted'], ls=1, anchor='end')
    b.append(cal_svg.replace('<g class="turtle">', ''.join(ann) + '<g class="turtle">', 1))
    b.append(leg + G.text(f'UPDATED DAILY · {today:%Y.%m.%d}', 28, ly + 9.5, 11, 'mono500', th['dim'], ls=1.5))
    b.append(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" fill="none" stroke="{th["frame"]}" stroke-opacity="{th["frame_op"]}" stroke-width="2"/>')
    css.append('@media (prefers-reduced-motion: reduce){*{animation:none!important}.turtle{display:none}}')
    alt = (f'Contribution log, updated {today:%B %-d, %Y}: {data["total"]:,} contributions in the last year, a longest streak of {run} days'
           + (f' from {day_label(first).title()} to {day_label(last).title()}' if run else '') + f', {data["repos"]} public repositories. '
           'A ninja turtle with a red headband walks the calendar and cuts every day with commits.')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{alt}">'
            f'<title>{alt}</title><style>{"".join(css)}</style><defs>{"".join(G.defs)}</defs>{"".join(b)}</svg>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--user', default='overloooooord'); ap.add_argument('--out', default='dist'); ap.add_argument('--data')
    a = ap.parse_args()
    if a.data:
        data = json.loads(Path(a.data).read_text())
    else:
        token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
        if not token:
            raise SystemExit('set GITHUB_TOKEN or GH_TOKEN')
        data = fetch(a.user, token)
    today = dt.datetime.now(dt.timezone.utc).date()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    (out / 'log.svg').write_text(panel(data, 'light', today))
    (out / 'log-dark.svg').write_text(panel(data, 'dark', today))
    lit = sum(1 for w in data['weeks'] for _, c, _ in w if c)
    print(f'log: {len(data["weeks"])} weeks, {lit} active days, {data["total"]} contributions -> {out}/log.svg, {out}/log-dark.svg')


if __name__ == '__main__':
    main()
