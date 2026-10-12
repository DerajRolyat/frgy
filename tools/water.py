import math, random

R = random.Random(11)

def catmull(pts, closed):
    """Smooth path through points (Catmull-Rom -> cubic Bezier)."""
    n = len(pts)
    d = f'M{pts[0][0]:.1f} {pts[0][1]:.1f}'
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if closed else pts[max(i - 1, 0)]
        p1 = pts[i]
        p2 = pts[(i + 1) % n] if closed else pts[i + 1]
        p3 = pts[(i + 2) % n] if closed else pts[min(i + 2, n - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f' C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}'
    return d + (' Z' if closed else '')

def spline_point(ctrl, t):
    """Point and width on an open Catmull-Rom spline of (x, y, w), t in [0,1]."""
    n = len(ctrl) - 1
    f = t * n
    i = min(int(f), n - 1)
    u = f - i
    p0, p1, p2, p3 = ctrl[max(i - 1, 0)], ctrl[i], ctrl[i + 1], ctrl[min(i + 2, n)]
    def cr(a, b, c, d):
        return 0.5 * ((2 * b) + (-a + c) * u + (2 * a - 5 * b + 4 * c - d) * u * u + (-a + 3 * b - 3 * c + d) * u ** 3)
    return tuple(cr(p0[k], p1[k], p2[k], p3[k]) for k in range(3))

def stream(ctrl, samples, wobble, pad=0):
    """Closed outline of a winding stream with irregular banks."""
    L, Rt = [], []
    ph1, ph2 = R.uniform(0, 6), R.uniform(0, 6)
    for s in range(samples + 1):
        t = s / samples
        x, y, w = spline_point(ctrl, t)
        x2, y2, _ = spline_point(ctrl, min(t + 0.01, 1)) if t < 1 else spline_point(ctrl, t)
        xa, ya, _ = spline_point(ctrl, max(t - 0.01, 0))
        dx, dy = x2 - xa, y2 - ya
        ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln, dx / ln
        nl = 1 + wobble * (math.sin(t * 23 + ph1) * 0.6 + math.sin(t * 57 + ph2) * 0.4) + R.uniform(-wobble, wobble) * 0.5
        nr = 1 + wobble * (math.sin(t * 19 + ph2) * 0.6 + math.sin(t * 61 + ph1) * 0.4) + R.uniform(-wobble, wobble) * 0.5
        hw = w / 2
        L.append((x + nx * (hw * nl + pad), y + ny * (hw * nl + pad)))
        Rt.append((x - nx * (hw * nr + pad), y - ny * (hw * nr + pad)))
    return catmull(L + Rt[::-1], True)

def pond(cx, cy, rx, ry, pad=0, seed=0):
    rr = random.Random(seed)
    ph = [rr.uniform(0, 6) for _ in range(3)]
    pts = []
    for i in range(22):
        a = i / 22 * math.tau
        k = 1 + 0.07 * math.sin(3 * a + ph[0]) + 0.05 * math.sin(5 * a + ph[1]) + 0.03 * math.sin(8 * a + ph[2])
        pts.append((cx + math.cos(a) * (rx * k + pad), cy + math.sin(a) * (ry * k + pad * 0.6)))
    return catmull(pts, True)

# Main river: comes out of the forest, meanders, widens toward the viewer
RIVER = [(985, 598, 8), (955, 608, 14), (900, 622, 24), (850, 642, 32), (845, 668, 42),
         (905, 700, 56), (985, 735, 70), (1015, 785, 92), (1000, 845, 120), (1060, 905, 165),
         (1180, 965, 230), (1290, 1030, 300)]
CH_L = [(578, 806, 9), (650, 772, 11), (730, 745, 12), (800, 712, 13), (848, 680, 16)]
CH_R = [(1006, 758, 14), (1080, 742, 11), (1170, 728, 10), (1260, 716, 12)]
POND_L = (330, 848, 255, 80)
POND_R = (1395, 708, 165, 36)

def build():
    river = stream(RIVER, 70, 0.14)
    river_rim = stream(RIVER, 70, 0.14, pad=7)
    chl, chl_rim = stream(CH_L, 24, 0.22), stream(CH_L, 24, 0.22, pad=5)
    chr_, chr_rim = stream(CH_R, 20, 0.22), stream(CH_R, 20, 0.22, pad=5)
    pl, pl_rim = pond(*POND_L, seed=3), pond(*POND_L, pad=9, seed=3)
    pr, pr_rim = pond(*POND_R, seed=5), pond(*POND_R, pad=7, seed=5)
    waters = [river, chl, chr_, pl, pr]
    rims = [river_rim, chl_rim, chr_rim, pl_rim, pr_rim]

    out = ['<clipPath id="waterClip">' + ''.join(f'<path d="{d}"/>' for d in waters) + '</clipPath>']
    # Muddy banks, then a thin grassy lip
    out += [f'<path d="{d}" fill="#2a2a22"/>' for d in rims]
    out += [f'<path d="{d}" fill="url(#water)"/>' for d in waters]
    out.append('<g clip-path="url(#waterClip)">')
    # Shadow of the banks and trees falling on the water
    out += [f'<path d="{d}" fill="none" stroke="#0e1424" stroke-width="22" opacity="0.55" filter="url(#blur6)"/>' for d in waters]
    # Reflection of the dark treeline at the far end of the river
    out.append('<rect x="780" y="590" width="260" height="34" fill="#2b2a48" opacity="0.55" filter="url(#blur6)"/>')
    # Broken sunset reflection beneath the sun
    sun = []
    for i in range(26):
        y = 604 + i * 4.2 + R.uniform(-1, 1)
        hl = (10 + i * 0.9) * R.uniform(0.5, 1.2)
        x = 868 + R.uniform(-6, 6)
        sun.append(f'<path d="M{x-hl:.1f} {y:.1f} H{x+hl:.1f}" stroke="#ffd9a2" stroke-width="{1.2 + i*0.06:.1f}" opacity="{0.85 - i*0.028:.2f}"/>')
    out.append('<g class="shimmer" stroke-linecap="round">' + ''.join(sun) + '</g>')
    # Ripples: short horizontal glints scattered across the water
    rip = []
    for _ in range(170):
        t = R.uniform(0.15, 1)
        x, y, w = spline_point(RIVER, t)
        x += R.uniform(-0.45, 0.45) * w
        y += R.uniform(-6, 6)
        hl = w * R.uniform(0.04, 0.16)
        col = '#f3c9a2' if y < 760 else '#b9c3e8'
        rip.append(f'<path d="M{x-hl:.1f} {y:.1f} q{hl:.1f} {-hl*0.08:.1f} {hl*2:.1f} 0" stroke="{col}" stroke-width="{0.8 + (y-600)/400*1.6:.1f}" fill="none" opacity="{R.uniform(0.12, 0.38):.2f}"/>')
    for (cx, cy, rx, ry) in (POND_L, POND_R):
        for _ in range(26):
            x = cx + R.uniform(-0.8, 0.8) * rx; y = cy + R.uniform(-0.6, 0.6) * ry; hl = R.uniform(6, 22)
            rip.append(f'<path d="M{x-hl:.1f} {y:.1f} H{x+hl:.1f}" stroke="#c9c6ea" stroke-width="1" opacity="{R.uniform(0.1, 0.25):.2f}"/>')
    out.append('<g stroke-linecap="round">' + ''.join(rip) + '</g>')
    out.append('</g>')

    # Rocks along the banks and in the shallows
    rocks, frog_rocks = [], []
    def rock(x, y, s, sky=True):
        w = 22 * s; h = 13 * s
        rocks.append(f'<path d="M{x-w:.1f} {y:.1f} C{x-w:.1f} {y-h:.1f} {x-w*0.3:.1f} {y-h*1.3:.1f} {x+w*0.2:.1f} {y-h*1.15:.1f} C{x+w*0.8:.1f} {y-h:.1f} {x+w:.1f} {y-h*0.4:.1f} {x+w:.1f} {y:.1f} Z" fill="#1c2026"/>')
        if sky:
            rocks.append(f'<path d="M{x-w*0.75:.1f} {y-h*0.75:.1f} C{x-w*0.3:.1f} {y-h*1.15:.1f} {x+w*0.3:.1f} {y-h*1.1:.1f} {x+w*0.7:.1f} {y-h*0.7:.1f}" stroke="#d99a7c" stroke-width="{1+s*0.5:.1f}" fill="none" opacity="0.45"/>')
        rocks.append(f'<path d="M{x-w*1.1:.1f} {y+1:.1f} H{x+w*1.1:.1f}" stroke="#c9d0f0" stroke-width="1.2" opacity="0.3"/>')
    for t, off, s in [(0.62, 0.42, 0.7), (0.70, -0.46, 0.9), (0.80, 0.30, 1.0), (0.86, -0.5, 1.3), (0.93, 0.15, 1.6), (0.96, -0.35, 1.2), (0.5, 0.5, 0.5)]:
        x, y, w = spline_point(RIVER, t)
        x += off * w
        rock(x, y, s)
        frog_rocks.append((x, y - 13 * s * 1.05, s))
    rock(1045, 960, 0.9); rock(980, 900, 0.6); rock(640, 800, 0.5); rock(1235, 740, 0.45)
    out += rocks
    return '\n'.join(out), frog_rocks
