"""Katana illustrations for the Akai profile, drawn from the real anatomy of a Japanese sword.

Local frame: the sword lies along +x, pommel (kashira) at x=0, tip (kissaki) at x=L, cutting edge (ha) facing +y.
Proportions follow a standard katana: tsuka ~26 % of the length, blade ~72 %, blade width ~3.2 % at the base
tapering to ~2.2 % at the yokote, chu-kissaki ~3.6 %, sori (curve depth) ~1.9 %.
Every part is its own shape: kashira, ito wrap over same (rayskin) with diamond windows and menuki, fuchi,
seppa, tsuba, habaki, blade with shinogi, hamon, yokote and boshi, optional saya with koiguchi, kurigata, sageo, kojiri.
Callers wrap the returned SVG fragment in their own transform. Ids are prefixed per instance.
"""
import math

INK = '#0d1117'; PAPER = '#f3ede4'; AKA = '#c8102e'; WINE = '#7a0a1a'
GOLD = '#c9a961'; GOLD_D = '#8a6d3b'; GOLD_L = '#f1e2b4'
STEEL = dict(mune='#5f5a57', shinogiji='#8c8680', ji='#b7b0a7', ji_lo='#cfc8be', hamon='#f6f1e8', edge='#ffffff')

ITO = {  # base, dark edge, light twist highlight
    'red': ('#b3122c', '#5e0714', '#ef5a6c'),
    'black': ('#1a1517', '#000000', '#5b5157'),
    'cream': ('#e6dcc7', '#9c8f76', '#fffaf0'),
}


def f(v):
    s = f'{v:.1f}'
    return '0' if s in ('-0.0', '0.0') else (s[:-2] if s.endswith('.0') else s)


class Katana:
    def __init__(self, L, pid, ito='red', same='#efe6d6', tsuba='#1b1618', rim=GOLD, metal=GOLD,
                 hamon='notare', hi=False, red_glow=0.0, rim_light=None, sukashi='moon', seed=3):
        self.L = L; self.p = pid; self.ito = ITO[ito]; self.same = same; self.tsuba_c = tsuba
        self.rim = rim; self.metal = metal; self.hamon_kind = hamon; self.hi = hi; self.red_glow = red_glow
        self.rim_light = rim_light; self.sukashi = sukashi; self.seed = seed
        self.S = 0.062                                   # tip rise over the whole length -> sori ~1.6 %
        self.k_len = 0.030 * L; self.f_len = 0.018 * L
        self.tsuka_len = 0.262 * L; self.tb = max(3.0, 0.011 * L)
        self.hb_len = 0.034 * L
        self.x_t = self.tsuka_len; self.x_b0 = self.x_t + self.tb
        self.wt = 0.034 * L; self.wb = 0.032 * L; self.wy = 0.0225 * L
        self.kl = 0.038 * L; self.x_y = L - self.kl
        self.defs = []

    # ------------------------------------------------------------------ geometry
    def yc(self, x):
        return -self.S * x * x / self.L

    def w(self, x):
        t = (x - self.x_b0) / (self.x_y - self.x_b0)
        return self.wb + (self.wy - self.wb) * min(max(t, 0), 1)

    def mune(self, x):
        return self.yc(x) - self.w(x) * 0.5

    def edge(self, x):
        return self.yc(x) + self.w(x) * 0.5

    def shinogi(self, x):
        return self.mune(x) + self.w(x) * 0.34

    def tip(self):
        return self.L, self.mune(self.L) + 0.16 * self.wy

    def xs(self, a, b, n=28):
        return [a + (b - a) * i / n for i in range(n + 1)]

    def poly(self, pts):
        return ' '.join(f'{f(x)} {f(y)}' for x, y in pts)

    def hamon_y(self, x):
        w = self.w(x); k = self.hamon_kind; lam = 2.6 * self.wb
        if k == 'suguha':
            v = 0.24
        elif k == 'gunome':
            ph = (x - self.x_b0) / lam
            v = 0.22 + 0.13 * abs(math.sin(math.pi * ph)) ** 0.55
        else:  # notare: long gentle swells with a second harmonic
            ph = (x - self.x_b0) / (lam * 1.7)
            v = 0.26 + 0.09 * math.sin(2 * math.pi * ph) + 0.035 * math.sin(4.3 * math.pi * ph + 1.1)
        return self.edge(x) - w * v

    # ------------------------------------------------------------------ blade
    def blade_outline(self):
        tx, ty = self.tip(); xy = self.x_y
        top = [(x, self.mune(x)) for x in self.xs(self.x_b0, self.L, 40)]
        ey = self.edge(xy)
        d = 'M' + self.poly(top) + f' L{f(tx)} {f(ty)}'
        d += (f' C{f(tx - 0.12 * self.kl)} {f(ty + 0.42 * self.wy)} {f(xy + 0.5 * self.kl)} {f(ey + 0.02 * self.wy)} {f(xy)} {f(ey)}')
        bot = [(x, self.edge(x)) for x in self.xs(xy, self.x_b0, 40)]
        d += ' L' + self.poly(bot) + ' Z'
        return d

    def blade(self, glint_class=''):
        p = self.p; tx, ty = self.tip(); xy = self.x_y
        outline = self.blade_outline()
        self.defs.append(f'<clipPath id="{p}b"><path d="{outline}"/></clipPath>')
        g = [f'<path d="{outline}" fill="{STEEL["ji"]}"/>']
        # shinogi-ji: the burnished band between the back and the ridge, runs out through the ko-shinogi to the tip
        sj = [(x, self.mune(x) - 2) for x in self.xs(self.x_b0, self.L, 40)]
        sj += [(tx + 2, ty - 1), (xy + 0.62 * self.kl, self.shinogi(xy) + 0.30 * (ty - self.shinogi(xy)))]
        sj += [(x, self.shinogi(x)) for x in self.xs(xy, self.x_b0, 40)]
        g.append(f'<path d="M{self.poly(sj)} Z" fill="{STEEL["shinogiji"]}"/>')
        # hamon: the frosty tempered edge, notare / gunome / suguha, turning into the boshi inside the kissaki
        hm = [(x, self.hamon_y(x)) for x in self.xs(self.x_b0 + self.hb_len * 0.8, xy, 90)]
        hy = self.hamon_y(xy)
        boshi = [(xy + 0.35 * self.kl, hy - 0.10 * self.wy), (xy + 0.72 * self.kl, ty + 0.38 * self.wy), (tx - 0.10 * self.kl, ty + 0.14 * self.wy)]
        low = [(tx + 4, ty + 30), (self.x_b0, self.edge(self.x_b0) + 30)]
        hpath = 'M' + self.poly(hm + boshi + low) + ' Z'
        g.append(f'<path d="{hpath}" fill="{STEEL["hamon"]}"/>')
        # nioi: a soft bright line on the hamon boundary
        g.append(f'<path d="M{self.poly(hm)}" fill="none" stroke="#ffffff" stroke-width="{f(max(0.8, self.wb * 0.07))}" opacity=".85" filter="url(#{p}soft)"/>')
        self.defs.append(f'<filter id="{p}soft" x="-5%" y="-50%" width="110%" height="200%"><feGaussianBlur stdDeviation="{f(max(0.4, self.wb * 0.05))}"/></filter>')
        # polish: a long light streak just under the shinogi, and a darker line on the ridge itself
        streak = [(x, self.shinogi(x) + self.w(x) * 0.07) for x in self.xs(self.x_b0 + self.hb_len, xy - 4, 30)]
        streak += [(x, self.shinogi(x) + self.w(x) * 0.17) for x in self.xs(xy - 4, self.x_b0 + self.hb_len, 30)]
        g.append(f'<path d="M{self.poly(streak)} Z" fill="#ffffff" opacity=".38"/>')
        g.append(f'<path d="M{self.poly([(x, self.shinogi(x)) for x in self.xs(self.x_b0, xy, 40)])}" fill="none" stroke="#4a4542" stroke-width="{f(max(0.6, self.wb * 0.045))}" opacity=".7"/>')
        if self.hi:  # bo-hi: a groove in the shinogi-ji
            hi_pts = [(x, self.mune(x) + self.w(x) * 0.15) for x in self.xs(self.x_b0 + self.hb_len * 1.2, xy - 0.9 * self.kl, 30)]
            g.append(f'<path d="M{self.poly(hi_pts)}" fill="none" stroke="#3d3936" stroke-width="{f(self.wb * 0.11)}" stroke-linecap="round"/>')
            g.append(f'<path d="M{self.poly([(x, y + self.wb * 0.05) for x, y in hi_pts])}" fill="none" stroke="#d8d2c9" stroke-width="{f(self.wb * 0.035)}" stroke-linecap="round" opacity=".8"/>')
        if self.red_glow:
            rg = [(x, self.shinogi(x) + self.w(x) * 0.2) for x in self.xs(self.x_b0, xy, 30)] + [(x, self.hamon_y(x) - self.w(x) * 0.04) for x in self.xs(xy, self.x_b0, 30)]
            g.append(f'<path d="M{self.poly(rg)} Z" fill="{AKA}" opacity="{self.red_glow}"/>')
        # yokote and the edge line
        g.append(f'<path d="M{f(xy)} {f(self.shinogi(xy))} L{f(xy + 0.03 * self.kl)} {f(self.edge(xy))}" stroke="#4a4542" stroke-width="{f(max(0.6, self.wb * 0.05))}"/>')
        g.append(f'<path d="M{self.poly([(x, self.edge(x) - 0.5) for x in self.xs(self.x_b0, xy, 40)])}" fill="none" stroke="{STEEL["edge"]}" stroke-width="{f(max(0.6, self.wb * 0.05))}" opacity=".9"/>')
        if glint_class:
            gw = self.wb * 2.4
            g.append(f'<g class="{glint_class}"><rect x="{f(self.x_b0)}" y="{f(self.mune(self.x_b0) - 40)}" width="{f(gw)}" height="{f(self.wb + 80)}" fill="url(#{p}gl)" transform="skewX(-28)"/></g>')
            self.defs.append(f'<linearGradient id="{p}gl" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".95"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')
        body = f'<g clip-path="url(#{p}b)">{"".join(g)}</g>'
        return body + f'<path d="{outline}" fill="none" stroke="{INK}" stroke-width="{f(max(0.9, self.wb * 0.075))}" stroke-linejoin="round"/>'

    # ------------------------------------------------------------------ fittings
    def tsuka_w(self, x):
        t = (x - self.k_len) / (self.x_t - self.f_len - self.k_len)
        return self.wt * (1 - 0.075 * math.sin(math.pi * min(max(t, 0), 1)))

    def tsuka_outline(self, a, b):
        top = [(x, self.yc(x) - self.tsuka_w(x) / 2) for x in self.xs(a, b, 24)]
        bot = [(x, self.yc(x) + self.tsuka_w(x) / 2) for x in self.xs(b, a, 24)]
        return 'M' + self.poly(top + bot) + ' Z'

    def tsuka(self):
        p = self.p; a, b = self.k_len, self.x_t - self.f_len
        base, dark, light = self.ito
        out = self.tsuka_outline(a, b)
        self.defs.append(f'<clipPath id="{p}t"><path d="{out}"/></clipPath>')
        g = [f'<path d="{out}" fill="{self.same}"/>']
        # same: the rayskin nodules that show through the diamond windows
        nod = []
        step = max(1.6, self.wt * 0.11)
        for j, y in enumerate([self.yc(a) - self.wt / 2 + step * (k + 0.5) for k in range(int(self.wt / step) + 2)]):
            for i, x in enumerate(self.xs(a, b, max(4, int((b - a) / step)))):
                xx = x + (step / 2 if j % 2 else 0)
                g.append(f'<circle cx="{f(xx)}" cy="{f(y + self.yc(xx) - self.yc(a))}" r="{f(step * 0.32)}"/>')
        g = [g[0], f'<g fill="#d7ccbb">{"".join(g[1:])}</g>']
        n = max(5, round((b - a) / (self.wt * 0.98)))
        s = (b - a) / n; bw = s * 0.56
        # menuki: a gold ornament under the wrap, seen through the middle windows
        mx = a + s * (n // 2 + 0.05)
        g.append(f'<ellipse cx="{f(mx)}" cy="{f(self.yc(mx))}" rx="{f(s * 0.95)}" ry="{f(self.wt * 0.2)}" fill="{GOLD}" stroke="{GOLD_D}" stroke-width="{f(max(0.4, self.wt * 0.03))}"/>')
        g.append(f'<path d="M{f(mx - s * 0.6)} {f(self.yc(mx))} q{f(s * 0.3)} {f(-self.wt * 0.12)} {f(s * 0.6)} 0 t{f(s * 0.6)} 0" fill="none" stroke="{GOLD_D}" stroke-width="{f(max(0.4, self.wt * 0.03))}"/>')
        # mekugi: the bamboo peg, in the window next to the fuchi
        kx = b - s * 0.5
        g.append(f'<circle cx="{f(kx)}" cy="{f(self.yc(kx))}" r="{f(self.wt * 0.1)}" fill="#8f7c5a" stroke="{GOLD_D}" stroke-width="{f(max(0.3, self.wt * 0.02))}"/>')
        bands = []
        for i in range(n + 1):
            xi = a + i * s
            yt = lambda x: self.yc(x) - self.tsuka_w(x) / 2 - 1
            yb = lambda x: self.yc(x) + self.tsuka_w(x) / 2 + 1
            A = [(xi - s / 2 - bw / 2, yt(xi - s / 2)), (xi - s / 2 + bw / 2, yt(xi - s / 2)), (xi + s / 2 + bw / 2, yb(xi + s / 2)), (xi + s / 2 - bw / 2, yb(xi + s / 2))]
            B = [(xi + s / 2 - bw / 2, yt(xi + s / 2)), (xi + s / 2 + bw / 2, yt(xi + s / 2)), (xi - s / 2 + bw / 2, yb(xi - s / 2)), (xi - s / 2 - bw / 2, yb(xi - s / 2))]
            order = (B, A) if i % 2 else (A, B)
            for qi, q in enumerate(order):
                bands.append(f'<path d="M{self.poly(q)} Z" fill="{base}" stroke="{dark}" stroke-width="{f(max(0.4, s * 0.05))}"/>')
                if qi == 0:   # the strand that runs under the crossing sits in shadow
                    bands.append(f'<path d="M{self.poly(q)} Z" fill="{dark}" opacity=".28"/>')
                (x1, y1), (x2, y2) = ((q[0][0] + q[1][0]) / 2, q[0][1]), ((q[2][0] + q[3][0]) / 2, q[2][1])
                bands.append(f'<path d="M{f(x1 + (x2 - x1) * .12)} {f(y1 + (y2 - y1) * .12)} L{f(x1 + (x2 - x1) * .88)} {f(y1 + (y2 - y1) * .88)}" stroke="{light}" stroke-width="{f(max(0.4, bw * 0.16))}" opacity=".55" stroke-linecap="round"/>')
            # the twist at the crossing
            cy = self.yc(xi); r = s * 0.2
            bands.append(f'<path d="M{f(xi - r)} {f(cy)} L{f(xi)} {f(cy - r * 0.9)} L{f(xi + r)} {f(cy)} L{f(xi)} {f(cy + r * 0.9)} Z" fill="{dark}" opacity=".55"/>')
        g.append(''.join(bands))
        body = f'<g clip-path="url(#{p}t)">{"".join(g)}</g>'
        return body + f'<path d="{out}" fill="none" stroke="{INK}" stroke-width="{f(max(0.8, self.wt * 0.05))}"/>'

    def kashira(self):
        a = self.k_len; y0 = self.yc(0); h = self.tsuka_w(a)
        d = (f'M{f(a)} {f(self.yc(a) - h / 2)} L{f(a * 0.35)} {f(y0 - h * 0.5)} Q{f(-a * 0.25)} {f(y0 - h * 0.46)} {f(-a * 0.25)} {f(y0)} '
             f'Q{f(-a * 0.25)} {f(y0 + h * 0.46)} {f(a * 0.35)} {f(y0 + h * 0.5)} L{f(a)} {f(self.yc(a) + h / 2)} Z')
        base, dark, light = self.ito
        g = [f'<path d="{d}" fill="{self.tsuba_c}" stroke="{INK}" stroke-width="{f(max(0.8, h * 0.05))}"/>',
             f'<path d="M{f(a - 0.6)} {f(self.yc(a) - h / 2 + 0.8)} L{f(a - 0.6)} {f(self.yc(a) + h / 2 - 0.8)}" stroke="{self.metal}" stroke-width="{f(max(0.8, h * 0.06))}"/>',
             # the ito crosses over the kashira and is tied
             f'<path d="M{f(a * 0.95)} {f(y0 - h * 0.44)} L{f(a * 0.15)} {f(y0 + h * 0.18)} M{f(a * 0.95)} {f(y0 + h * 0.44)} L{f(a * 0.15)} {f(y0 - h * 0.18)}" stroke="{base}" stroke-width="{f(h * 0.2)}" stroke-linecap="round"/>',
             f'<circle cx="{f(a * 0.22)}" cy="{f(y0)}" r="{f(h * 0.14)}" fill="{base}" stroke="{dark}" stroke-width="{f(max(0.4, h * 0.03))}"/>']
        if self.rim_light:
            g.append(f'<path d="{d}" fill="none" stroke="{self.rim_light}" stroke-width=".6" opacity=".22"/>')
        return ''.join(g)

    def fuchi(self):
        a, b = self.x_t - self.f_len, self.x_t
        h0, h1 = self.tsuka_w(a), self.tsuka_w(a) * 1.04
        d = f'M{f(a)} {f(self.yc(a) - h0 / 2)} L{f(b)} {f(self.yc(b) - h1 / 2)} L{f(b)} {f(self.yc(b) + h1 / 2)} L{f(a)} {f(self.yc(a) + h0 / 2)} Z'
        g = [f'<path d="{d}" fill="{self.tsuba_c}" stroke="{INK}" stroke-width="{f(max(0.8, h0 * 0.05))}"/>',
             f'<path d="M{f(a + 0.8)} {f(self.yc(a) - h0 / 2 + 0.6)} L{f(a + 0.8)} {f(self.yc(a) + h0 / 2 - 0.6)}" stroke="{self.metal}" stroke-width="{f(max(0.7, h0 * 0.05))}"/>',
             f'<path d="M{f(a + 1.5)} {f(self.yc(a) - h0 * 0.3)} L{f(b - 1)} {f(self.yc(b) - h1 * 0.3)}" stroke="{PAPER}" stroke-width="{f(max(0.5, h0 * 0.05))}" opacity=".35"/>']
        return ''.join(g)

    def tsuba_seppa(self):
        x0 = self.x_t; tb = self.tb; cx = x0 + tb / 2; cy = self.yc(cx)
        ry = 0.043 * self.L; rx = max(2.6, 0.0125 * self.L)
        sep_h = self.wt * 1.18
        g = []
        for sx in (x0 - 0.9, x0 + tb - 0.2):
            g.append(f'<rect x="{f(sx)}" y="{f(self.yc(sx) - sep_h / 2)}" width="{f(1.1)}" height="{f(sep_h)}" fill="{self.metal}" stroke="{GOLD_D}" stroke-width=".4"/>')
        # thickness: a back rim offset toward the handle, then the face
        g.append(f'<ellipse cx="{f(cx - rx * 0.45)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}" fill="#050405" stroke="{INK}" stroke-width="{f(max(0.8, rx * 0.2))}"/>')
        g.append(f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}" fill="{self.tsuba_c}" stroke="{self.rim}" stroke-width="{f(max(0.8, rx * 0.26))}"/>')
        if self.sukashi == 'moon' and ry > 12:     # gold inlay (zogan): a crescent moon and a star, seen at a steep angle
            g.append(f'<path d="M{f(cx - rx * 0.1)} {f(cy - ry * 0.74)} q{f(rx * 0.95)} {f(ry * 0.2)} 0 {f(ry * 0.42)} q{f(rx * 0.42)} {f(-ry * 0.21)} 0 {f(-ry * 0.42)} Z" fill="{GOLD}"/>')
            g.append(f'<ellipse cx="{f(cx + rx * 0.1)}" cy="{f(cy + ry * 0.6)}" rx="{f(rx * 0.26)}" ry="{f(ry * 0.07)}" fill="{GOLD}"/>')
        g.append(f'<path d="M{f(cx - rx * 0.5)} {f(cy - ry * 0.86)} Q{f(cx + rx * 0.2)} {f(cy - ry * 1.02)} {f(cx + rx * 0.7)} {f(cy - ry * 0.55)}" fill="none" stroke="{PAPER}" stroke-width="{f(max(0.6, rx * 0.14))}" opacity=".5" stroke-linecap="round"/>')
        if self.rim_light:
            g.append(f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx + 0.8)}" ry="{f(ry + 0.8)}" fill="none" stroke="{self.rim_light}" stroke-width=".7" opacity=".35"/>')
        return ''.join(g)

    def habaki(self):
        a = self.x_b0; b = a + self.hb_len; e = 0.26 * self.hb_len
        up, dn = self.mune(a) - 1.4, self.edge(a) + 1.4
        d = f'M{f(a)} {f(up)} L{f(b)} {f(self.mune(b) - 1.1)} L{f(b - e)} {f(self.edge(b - e) + 1.1)} L{f(a)} {f(dn)} Z'
        g = [f'<path d="{d}" fill="{self.metal}" stroke="{GOLD_D}" stroke-width="{f(max(0.6, self.wb * 0.05))}"/>',
             f'<path d="M{f(a + 0.6)} {f(up + (dn - up) * 0.62)} L{f(b - e * 0.62)} {f(self.edge(b) - (dn - up) * 0.36)} L{f(b - e * 0.62)} {f(self.edge(b - e) + 0.8)} L{f(a + 0.6)} {f(dn - 0.4)} Z" fill="{GOLD_D}" opacity=".55"/>',
             f'<path d="M{f(a + 0.8)} {f(up + (dn - up) * 0.2)} L{f(b - 0.8)} {f(self.mune(b) + (dn - up) * 0.18)}" stroke="{GOLD_L}" stroke-width="{f(max(0.6, self.wb * 0.09))}" opacity=".9"/>']
        for k in range(3):  # neko-gaki: diagonal file marks
            xx = a + self.hb_len * (0.32 + 0.16 * k)
            g.append(f'<path d="M{f(xx)} {f(up + 1.4)} l{f(-self.hb_len * 0.1)} {f((dn - up) * 0.42)}" stroke="{GOLD_D}" stroke-width=".5" opacity=".7"/>')
        return ''.join(g)

    # ------------------------------------------------------------------ scabbard
    def saya(self, color='#141013', style='gloss', sageo=('#e6dcc7', '#9c8f76'), drawn=0.0, hang=16, gloss_class=''):
        """Scabbard over the blade. drawn: how much of the blade (0..1) is out of the koiguchi."""
        p = self.p
        x0 = self.x_b0 + drawn * (self.L - self.x_b0); x1 = x0 + (self.L - self.x_b0) * 1.01
        ws0, ws1 = self.wb * 1.34, self.wy * 1.42
        ww = lambda x: ws0 + (ws1 - ws0) * (x - x0) / (x1 - x0)
        cyf = lambda x: self.yc(x) - 0.03 * self.wb
        top = [(x, cyf(x) - ww(x) / 2) for x in self.xs(x0, x1 - ws1 * 0.5, 36)]
        bot = [(x, cyf(x) + ww(x) / 2) for x in self.xs(x1 - ws1 * 0.5, x0, 36)]
        ex = x1 - ws1 * 0.5; ey = cyf(ex)
        d = 'M' + self.poly(top) + f' Q{f(x1 + ws1 * 0.25)} {f(ey - ws1 / 2)} {f(x1 + ws1 * 0.25)} {f(ey)} Q{f(x1 + ws1 * 0.25)} {f(ey + ws1 / 2)} {f(ex)} {f(ey + ws1 / 2)} L' + self.poly(bot) + ' Z'
        self.defs.append(f'<clipPath id="{p}s"><path d="{d}"/></clipPath>')
        g = [f'<path d="{d}" fill="{color}"/>']
        if style == 'ribbed':    # kizami-zaya: a lacquered rib every few pixels
            ribs = []
            for x in self.xs(x0 + 3, x1, int((x1 - x0) / max(3.4, self.wb * 0.42))):
                ribs.append(f'M{f(x)} {f(cyf(x) - ww(x) / 2)} q{f(-self.wb * 0.18)} {f(ww(x) / 2)} 0 {f(ww(x))}')
            g.append(f'<path d="{" ".join(ribs)}" fill="none" stroke="#5e0714" stroke-width="{f(max(0.6, self.wb * 0.06))}" opacity=".7"/>')
        shade = [(x, cyf(x) + ww(x) * 0.22) for x in self.xs(x0, x1, 30)] + [(x, cyf(x) + ww(x) * 0.6) for x in self.xs(x1, x0, 30)]
        g.append(f'<path d="M{self.poly(shade)} Z" fill="#000" opacity="{0.35 if style == "ribbed" else 0.3}"/>')
        # gloss: one long reflection along the upper third, a thin one along the lower edge
        gl = [(x, cyf(x) - ww(x) * 0.30) for x in self.xs(x0 + 4, x1 - 6, 30)] + [(x, cyf(x) - ww(x) * 0.18) for x in self.xs(x1 - 6, x0 + 4, 30)]
        self.defs.append(f'<filter id="{p}gb" x="-2%" y="-60%" width="104%" height="220%"><feGaussianBlur stdDeviation="{f(max(0.5, ws0 * 0.07))}"/></filter>')
        g.append(f'<path d="M{self.poly(gl)} Z" fill="{PAPER}" opacity="{0.42 if style != "ribbed" else 0.3}" filter="url(#{p}gb)"/>')
        g.append(f'<path d="M{self.poly([(x, cyf(x) + ww(x) * 0.34) for x in self.xs(x0 + 6, x1 - 8, 30)])}" fill="none" stroke="{AKA if style != "ribbed" else PAPER}" stroke-width="{f(max(0.8, self.wb * 0.09))}" opacity=".5" filter="url(#{p}gb)"/>')
        if gloss_class:   # a travelling reflection across the lacquer
            self.defs.append(f'<linearGradient id="{p}gg" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')
            g.append(f'<g class="{gloss_class}"><rect x="{f(x0 - 70)}" y="{f(cyf(x0) - ws0 * 3)}" width="{f(ws0 * 2.2)}" height="{f(ws0 * 6)}" fill="url(#{p}gg)" transform="skewX(-32)"/></g>')
        body = f'<g clip-path="url(#{p}s)">{"".join(g)}</g><path d="{d}" fill="none" stroke="{INK}" stroke-width="{f(max(0.9, self.wb * 0.07))}"/>'
        if self.rim_light:
            body += f'<path d="{d}" fill="none" stroke="{self.rim_light}" stroke-width=".7" opacity=".35"/>'
        # koiguchi (horn mouth) and kojiri (end cap)
        kl = self.L * 0.022
        body += (f'<path d="M{f(x0)} {f(cyf(x0) - ww(x0) / 2)} L{f(x0 + kl)} {f(cyf(x0 + kl) - ww(x0 + kl) / 2)} L{f(x0 + kl)} {f(cyf(x0 + kl) + ww(x0 + kl) / 2)} L{f(x0)} {f(cyf(x0) + ww(x0) / 2)} Z" fill="#241c20" stroke="{INK}" stroke-width=".8"/>'
                 f'<path d="M{f(x0 + 1)} {f(cyf(x0) - ww(x0) * 0.3)} L{f(x0 + kl - 1)} {f(cyf(x0 + kl) - ww(x0 + kl) * 0.3)}" stroke="{PAPER}" stroke-width=".8" opacity=".45"/>')
        cap = x1 - ws1 * 0.55
        body += (f'<path d="M{f(cap)} {f(cyf(cap) - ww(cap) / 2)} L{f(ex)} {f(ey - ws1 / 2)} Q{f(x1 + ws1 * 0.25)} {f(ey - ws1 / 2)} {f(x1 + ws1 * 0.25)} {f(ey)} Q{f(x1 + ws1 * 0.25)} {f(ey + ws1 / 2)} {f(ex)} {f(ey + ws1 / 2)} L{f(cap)} {f(cyf(cap) + ww(cap) / 2)} Z" fill="{self.metal}" stroke="{GOLD_D}" stroke-width=".7"/>')
        # kurigata and the sageo: wound twice over the saya, a loop hanging below, two tails with tassels
        if sageo:
            sc, sd = sageo; kx = x0 + (x1 - x0) * 0.12
            cw = max(1.6, self.wb * 0.30)
            ky = cyf(kx) + ww(kx) / 2
            body += f'<path d="M{f(kx - cw * 1.1)} {f(ky - 0.4)} q{f(cw * 1.1)} {f(cw * 1.6)} {f(cw * 2.2)} 0 Z" fill="{color}" stroke="{INK}" stroke-width=".7"/>'
            wraps = []
            for dx in (cw * 1.6, cw * 4.2):
                xa = kx + dx
                wraps.append(f'M{f(xa - cw * 0.9)} {f(cyf(xa) + ww(xa) / 2 + 0.4)} L{f(xa + cw * 0.9)} {f(cyf(xa) - ww(xa) / 2 - 0.4)}')
            xa, xb = kx + cw * 0.2, kx + cw * 6.4
            ya, yb = cyf(xa) + ww(xa) / 2, cyf(xb) + ww(xb) / 2
            loop = f'M{f(xa)} {f(ya)} C{f(xa - cw)} {f(ya + hang * 1.25)} {f(xb + cw * 2)} {f(yb + hang * 1.25)} {f(xb)} {f(yb)}'
            kx2, ky2 = xb + cw * 0.6, yb + cw * 0.5
            tail = f'M{f(kx2)} {f(ky2)} c{f(hang * 0.6)} {f(hang * 0.35)} {f(hang * 1.5)} {f(hang * 0.45)} {f(hang * 2.3)} {f(hang * 0.7)}'
            for dpath, wdt, clip in ((loop, cw * 0.8, False), (tail, cw * 0.8, False), (' '.join(wraps), cw, True)):
                seg = (f'<path d="{dpath}" fill="none" stroke="{sd}" stroke-width="{f(wdt + 1.1)}" stroke-linecap="{"butt" if clip else "round"}"/>'
                       f'<path d="{dpath}" fill="none" stroke="{sc}" stroke-width="{f(wdt)}" stroke-linecap="{"butt" if clip else "round"}"/>'
                       f'<path d="{dpath}" fill="none" stroke="{sd}" stroke-width="{f(wdt * 0.4)}" stroke-dasharray="{f(wdt * 0.8)} {f(wdt * 0.8)}" opacity=".5"/>')
                body += f'<g clip-path="url(#{p}s)">{seg}</g>' if clip else seg
            body += f'<ellipse cx="{f(kx2)}" cy="{f(ky2)}" rx="{f(cw * 0.95)}" ry="{f(cw * 0.75)}" fill="{sc}" stroke="{sd}" stroke-width=".7"/>'
            tx_, ty_ = kx2 + hang * 2.3, ky2 + hang * 0.7
            body += f'<path d="M{f(tx_ - cw * 0.3)} {f(ty_ - cw * 0.4)} l{f(cw * 2.2)} {f(cw * 0.7)} l{f(-cw * 0.4)} {f(cw * 0.9)} Z" fill="{sc}" stroke="{sd}" stroke-width=".6"/>'
        return body

    def level(self, end=None):
        """degrees to rotate so the chord from the pommel to the tip (or to x=end) is horizontal"""
        x = end if end is not None else self.L
        return -math.degrees(math.atan2(self.yc(x), x))

    # ------------------------------------------------------------------ assembly
    def svg(self, saya=None, glint_class=''):
        """saya: None for a bare blade, or kwargs for saya(). Returns (defs, body)."""
        parts = []
        if saya is None or saya.get('drawn', 0) > 0:
            parts.append(self.blade(glint_class))
            parts.append(self.habaki())
        parts.append(self.tsuka())
        parts.append(self.kashira())
        parts.append(self.fuchi())
        parts.append(self.tsuba_seppa())
        if saya is not None:
            parts.append(self.saya(**saya))
        return ''.join(self.defs), ''.join(parts)
