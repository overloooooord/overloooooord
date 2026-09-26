"""Three katana dividers, each a different sword and a different moment: at rest, being drawn, on the stand."""
import math
from build_assets import write, AKA, PAPER, INK
from katana import Katana, GOLD
from typeset import Doc


def _rules(W, y, x_left, x_right, T):
    """thin rules that run out from the sword to both edges, ending in a small red lozenge"""
    return (f'<line x1="0" y1="{y}" x2="{x_left}" y2="{y}" stroke="{AKA}" stroke-opacity=".35"/>'
            f'<line x1="{x_right}" y1="{y}" x2="{W}" y2="{y}" stroke="{AKA}" stroke-opacity=".35"/>'
            f'<path d="M{x_left - 8} {y} l4 -4 l4 4 l-4 4 z" fill="{AKA}"/><path d="M{x_right} {y} l4 -4 l4 4 l-4 4 z" fill="{AKA}"/>')


def divider_saya(T):
    """a katana at rest in black lacquer, cream ito, gold fittings, the sageo tied and hanging"""
    W, H = 900, 78; dark = T['name'] == 'dark'
    k = Katana(700, 'da', ito='cream', hamon='gunome', rim_light=PAPER if dark else None)
    kd, kb = k.svg(saya=dict(color='#141013', style='gloss', sageo=('#e6dcc7', '#9c8f76'), hang=13, gloss_class='dgl'))
    x0 = 100; y0 = 30
    style = '@keyframes dgl{0%,55%{transform:translateX(0)}100%{transform:translateX(640px)}}.dgl{animation:dgl 6s cubic-bezier(.4,0,.2,1) 1s infinite}'
    body = (f'<defs>{kd}</defs>' + _rules(W, y0, x0 - 18, x0 + 718, T)
            + f'<g transform="translate({x0} {y0}) rotate({k.level(k.L):.2f})">{kb}</g>')
    write('divider-saya', T, Doc().svg(W, H, body, 'A katana at rest in a black lacquer scabbard, cream silk wrap, gold fittings', style))


def divider_draw(T):
    """nukitsuke: the blade a third out of a red ribbed scabbard, a glint running along the steel"""
    W, H = 900, 74; dark = T['name'] == 'dark'
    k = Katana(640, 'dd', ito='black', hamon='notare', hi=True, rim_light=PAPER if dark else None)
    kd, kb = k.svg(saya=dict(color='#b0102a', style='ribbed', sageo=('#1a1517', '#000000'), drawn=.3, hang=12), glint_class='ddg')
    x0 = 52; y0 = 30
    style = '@keyframes ddg{0%{transform:translateX(-40px)}30%,100%{transform:translateX(190px)}}.ddg{animation:ddg 4.2s cubic-bezier(.3,0,.2,1) .8s infinite}'
    body = (f'<defs>{kd}</defs>' + _rules(W, y0, x0 - 16, x0 + 808, T)
            + f'<g transform="translate({x0} {y0}) rotate({k.level(k.L * 1.23):.2f})">{kb}</g>')
    write('divider-draw', T, Doc().svg(W, H, body, 'A katana drawn a third of the way out of a red ribbed scabbard', style))


def _world(k, x0, y0, xl):
    """world position of the scabbard centre line at local x for a sword placed at (x0, y0) and levelled"""
    a = math.radians(k.level(k.L)); yl = k.yc(xl) - 0.03 * k.wb
    return x0 + xl * math.cos(a) - yl * math.sin(a), y0 + xl * math.sin(a) + yl * math.cos(a)


def divider_daisho(T):
    """daisho, katana over wakizashi, resting in the cradles of a black lacquer katana-kake with gold maki-e"""
    W, H = 900, 136; dark = T['name'] == 'dark'
    rim = PAPER if dark else None
    ka = Katana(560, 'dk', ito='black', hamon='notare', rim_light=rim)
    wa = Katana(410, 'dw', ito='black', hamon='suguha', rim_light=rim)
    kd1, kb1 = ka.svg(saya=dict(color='#141013', style='gloss', sageo=None, gloss_class='dkg'))
    kd2, kb2 = wa.svg(saya=dict(color='#141013', style='gloss', sageo=None))
    cx = 450; kx0, ky0 = cx - 300, 34; wx0, wy0 = cx - 222, 80
    lac = '#161113'; edge = PAPER if dark else INK
    stand, lips = [], []
    for ux in (cx - 70, cx + 150):
        d = f'M{ux - 9} 122 L{ux - 9} 26 Q{ux - 9} 14 {ux} 12 Q{ux + 9} 14 {ux + 9} 26 L{ux + 9} 122 Z'
        stand.append(f'<path d="{d}" fill="{lac}" stroke="{INK}" stroke-width="1"/>')
        if dark: stand.append(f'<path d="{d}" fill="none" stroke="{edge}" stroke-width=".7" opacity=".35"/>')
        for yy in (24, 64, 104, 112):
            stand.append(f'<circle cx="{ux + (3 if yy % 16 else -3)}" cy="{yy}" r="1.3" fill="{GOLD}" opacity=".85"/>')
        stand.append(f'<path d="M{ux - 4} 62 q6 -6 8 2 q-4 5 -8 -2" fill="none" stroke="{GOLD}" stroke-width=".9" opacity=".8"/>')
        for k_, x0_, y0_ in ((ka, kx0, ky0), (wa, wx0, wy0)):
            lo, hi = 0.0, k_.L * 1.3            # the local x whose world x is this upright
            for _ in range(40):
                mid = (lo + hi) / 2
                if _world(k_, x0_, y0_, mid)[0] < ux: lo = mid
                else: hi = mid
            wy = _world(k_, x0_, y0_, lo)[1]; half = k_.wb * 0.69
            lips.append(f'<path d="M{ux - 10} {wy + half - 3:.1f} q10 9 20 0 l0 6 q-10 9 -20 0 z" fill="{lac}" stroke="{INK}" stroke-width=".9"/>')
            if dark: lips.append(f'<path d="M{ux - 10} {wy + half + 3:.1f} q10 9 20 0" fill="none" stroke="{edge}" stroke-width=".6" opacity=".4"/>')
    base = f'M{cx - 150} 120 L{cx + 230} 120 Q{cx + 242} 120 {cx + 244} 130 L{cx - 164} 130 Q{cx - 162} 120 {cx - 150} 120 Z'
    stand.append(f'<path d="{base}" fill="{lac}" stroke="{INK}" stroke-width="1"/>')
    if dark: stand.append(f'<path d="{base}" fill="none" stroke="{edge}" stroke-width=".7" opacity=".35"/>')
    stand.append(f'<path d="M{cx - 140} 125 H{cx + 222}" stroke="{GOLD}" stroke-width=".8" stroke-dasharray="2 5" opacity=".8"/>')
    style = '@keyframes dkg{0%,60%{transform:translateX(0)}100%{transform:translateX(500px)}}.dkg{animation:dkg 7s cubic-bezier(.4,0,.2,1) 2s infinite}'
    body = (f'<defs>{kd1}{kd2}</defs>' + _rules(W, 125, cx - 176, cx + 252, T) + ''.join(stand)
            + f'<g transform="translate({wx0} {wy0}) rotate({wa.level(wa.L):.2f})">{kb2}</g>'
            + f'<g transform="translate({kx0} {ky0}) rotate({ka.level(ka.L):.2f})">{kb1}</g>' + ''.join(lips))
    write('divider-daisho', T, Doc().svg(W, H, body, 'Daisho: a katana over a wakizashi resting on a black lacquer sword stand with gold maki-e', style))
