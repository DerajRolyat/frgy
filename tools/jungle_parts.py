import math, random

R = random.Random(21)

def crown(x, y, r, fill):
    out = [f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.0f}"/>']
    for _ in range(4):
        a = R.uniform(math.pi, 2 * math.pi)
        d = r * R.uniform(0.45, 0.8)
        out.append(f'<circle cx="{x + math.cos(a) * d:.0f}" cy="{y + math.sin(a) * d * 0.7:.0f}" r="{r * R.uniform(0.5, 0.75):.0f}"/>')
    return f'<g fill="{fill}">' + ''.join(out) + '</g>'

def canopy(x0, x1, step, y_rng, r_rng, fill, skip=None):
    out = []
    for x in range(x0, x1, step):
        r = R.uniform(*r_rng)
        if skip and skip[0] < x < skip[1]:
            r *= skip[2]
        y = R.uniform(*y_rng)
        out.append(crown(x + R.uniform(-8, 8), y, r, fill))
        out.append(f'<rect x="{x - r*0.08:.0f}" y="{y:.0f}" width="{r*0.16:.0f}" height="{r*1.4:.0f}" fill="{fill}"/>')
    return '\n'.join(out)

def emergent(x, base, h, fill):
    top = base - h
    out = [f'<path d="M{x-4} {base} C{x-2} {base-h*0.5} {x+6} {top+30} {x+2} {top}" stroke="{fill}" stroke-width="7" fill="none"/>']
    for dx, dy, rx, ry in [(0, 0, 70, 18), (-40, 8, 40, 14), (42, 6, 44, 14), (0, -12, 44, 14)]:
        out.append(f'<ellipse cx="{x+dx}" cy="{top+dy}" rx="{rx}" ry="{ry}" fill="{fill}"/>')
    return ''.join(out)

def frond(x, y, ang, length, droop, width, fill, comb=True):
    a = math.radians(ang)
    ex, ey = x + math.cos(a) * length, y + math.sin(a) * length + droop
    cx, cy = x + math.cos(a) * length * 0.55, y + math.sin(a) * length * 0.55 - droop * 0.35
    d = f'M{x:.1f} {y:.1f} Q{cx:.1f} {cy:.1f} {ex:.1f} {ey:.1f}'
    s = ''
    if comb:
        s += f'<path d="{d}" stroke="{fill}" stroke-width="{width:.1f}" stroke-dasharray="2.2 2.6" fill="none"/>'
    s += f'<path d="{d}" stroke="{fill}" stroke-width="{max(1.5, width*0.14):.1f}" fill="none" stroke-linecap="round"/>'
    return s

def palm(x, base, h, fill, lean=0.0):
    tx, ty = x + lean * h, base - h
    out = [f'<path d="M{x} {base} Q{x + lean*h*0.2:.0f} {base - h*0.6:.0f} {tx:.0f} {ty:.0f}" stroke="{fill}" stroke-width="{h*0.035:.1f}" fill="none"/>']
    for ang in [-170, -145, -120, -60, -35, -10, 15, 165, -90]:
        out.append(frond(tx, ty, ang, h * R.uniform(0.32, 0.42), h * R.uniform(0.12, 0.25), h * 0.11, fill))
    return ''.join(out)

def fern(x, y, s, fill='#16291f'):
    out = []
    for ang in [-160, -130, -105, -80, -55, -25]:
        out.append(frond(x, y, ang, 70 * s * R.uniform(0.8, 1.1), 30 * s, 12 * s, fill))
    return f'<g>{"".join(out)}</g>'

def leaf(x, y, length, width, ang, fill, vein='#24402f', split=False):
    parts = [f'<path d="M0 0 Q{length*0.45:.0f} {-width:.0f} {length:.0f} 0 Q{length*0.45:.0f} {width:.0f} 0 0 Z" fill="{fill}"/>',
             f'<path d="M0 0 Q{length*0.5:.0f} {-width*0.08:.0f} {length*0.97:.0f} 0" stroke="{vein}" stroke-width="2" fill="none"/>']
    for i in range(1, 9):
        px = length * i / 10
        for side in (-1, 1):
            vy = width * 0.85 * math.sin(math.pi * px / length) * side
            parts.append(f'<path d="M{px:.0f} 0 Q{px+length*0.04:.0f} {vy*0.5:.0f} {px+length*0.09:.0f} {vy:.0f}" stroke="{vein}" stroke-width="1.2" fill="none"/>')
    if split:
        for i in (3, 6):
            px = length * i / 10
            vy = width * 0.95 * math.sin(math.pi * px / length)
            parts.append(f'<path d="M{px+length*0.09:.0f} {vy:.0f} L{px+length*0.03:.0f} {vy*0.35:.0f}" stroke="#0b130f" stroke-width="2"/>')
    return f'<g transform="translate({x} {y}) rotate({ang})">{"".join(parts)}</g>'

def vine(x, y_end, fill='#0f1a16'):
    pts = []
    sway = R.uniform(10, 26)
    d = f'M{x} -10'
    for i in range(1, 7):
        y = -10 + (y_end + 10) * i / 6
        d += f' Q{x + (sway if i % 2 else -sway):.0f} {y - (y_end/12):.0f} {x + R.uniform(-4, 4):.0f} {y:.0f}'
    out = [f'<path d="{d}" stroke="{fill}" stroke-width="2.5" fill="none"/>']
    for i in range(10):
        yy = R.uniform(20, y_end)
        side = R.choice((-1, 1))
        out.append(f'<ellipse cx="{x + side*7:.0f}" cy="{yy:.0f}" rx="8" ry="3.5" transform="rotate({side*35} {x + side*7:.0f} {yy:.0f})" fill="{fill}"/>')
    return ''.join(out)

def build():
    far = canopy(-40, 1660, 24, (522, 548), (24, 40), '#55666a', skip=(900, 1100, 0.55))
    far += ''.join(emergent(x, 560, R.uniform(110, 150), '#55666a') for x in (180, 520, 1230, 1460))
    mid = canopy(-40, 1660, 36, (555, 585), (38, 64), '#36494b', skip=(760, 1100, 0.0))
    mid += ''.join(palm(x, 600, R.uniform(170, 230), '#36494b', R.uniform(-0.15, 0.15)) for x in (300, 640, 1150, 1380))
    near = canopy(-40, 640, 56, (590, 640), (70, 105), '#243739') + canopy(1120, 1700, 56, (590, 640), (70, 105), '#243739')
    near += palm(560, 640, 300, '#243739', 0.12) + palm(1200, 640, 280, '#243739', -0.1)
    # Tall canopy trees crowding in from both sides
    tall = []
    for x, top in [(40, 260), (170, 300), (300, 250), (430, 330), (1180, 330), (1300, 270), (1430, 300), (1560, 240)]:
        tall.append(f'<path d="M{x-10} 700 C{x-6} 560 {x+4} 450 {x} {top+40} L{x+14} {top+40} C{x+18} 450 {x+20} 560 {x+16} 700 Z" fill="#1d2e2d"/>')
        tall.append(crown(x, top + 40, R.uniform(80, 110), '#1d2e2d'))
        tall.append(crown(x + R.uniform(-30, 30), top + 110, R.uniform(60, 85), '#223434'))
    near = ''.join(tall) + near

    # Framing: trunks, corner canopy, and vines from above
    frame = [
        '<g fill="#0f1915">',
        '<path d="M-20 1000 L-10 0 L70 0 L60 1000 Z"/>',
        '<path d="M1545 1000 C1550 600 1560 300 1555 0 L1640 0 L1640 1000 Z"/>',
        '</g>',
        canopy(-80, 380, 60, (-30, 40), (70, 110), '#0f1915'),
        canopy(1240, 1700, 60, (-30, 40), (70, 110), '#0f1915'),
        palm(110, 760, 520, '#121e19', 0.18),
        palm(1490, 760, 500, '#121e19', -0.2),
    ]
    vines = ''.join(vine(x, R.uniform(160, 420)) for x in list(range(20, 360, 34)) + list(range(1260, 1600, 34)))

    ferns = '\n'.join([fern(80, 860, 1.3), fern(600, 832, 0.8), fern(1230, 740, 0.6), fern(1560, 728, 0.9),
                       fern(880, 905, 0.7), fern(1540, 990, 1.4)])

    fg = '\n'.join([
        leaf(-30, 1010, 330, 70, -40, '#12241a', split=True),
        leaf(-40, 900, 260, 52, -12, '#16291e'),
        leaf(30, 1030, 230, 46, -75, '#0f1f16'),
        leaf(1640, 1010, 320, 68, -140, '#12241a', split=True),
        leaf(1650, 880, 250, 50, -170, '#16291e'),
        leaf(1560, 1040, 220, 44, -110, '#0f1f16'),
        leaf(440, 1040, 160, 34, -65, '#13251b'),
        leaf(1060, 1040, 150, 32, -115, '#13251b'),
    ])

    waterfall = '''
  <!-- Waterfall feeding the river -->
  <path d="M890 606 L902 470 C914 418 958 396 998 398 C1046 400 1084 424 1096 470 L1116 606 Z" fill="#2a3236"/>
  <path d="M902 470 C914 418 958 396 998 398 C1046 400 1084 424 1096 470 C1080 440 1044 424 1000 424 C956 424 920 440 902 470 Z" fill="#2f4a35"/>
  <g fill="#2f4a35"><circle cx="925" cy="430" r="26"/><circle cx="1072" cy="432" r="28"/><circle cx="960" cy="408" r="22"/><circle cx="1040" cy="406" r="24"/></g>
  <path d="M912 520 C930 506 952 508 962 520 M1020 500 C1040 492 1064 500 1076 516 M906 570 C924 560 944 564 954 576 M1030 560 C1050 552 1076 560 1090 574" stroke="#1d2427" stroke-width="3" fill="none"/>
  <path d="M972 412 C982 409 996 409 1004 412 L1016 604 L958 604 Z" fill="url(#falls)"/>
  <g class="falls" stroke="#ffffff" stroke-linecap="round" fill="none" opacity="0.6">
    <path d="M978 416 L968 604" stroke-width="2" stroke-dasharray="22 14"/>
    <path d="M987 414 L986 604" stroke-width="2.5" stroke-dasharray="30 12" style="animation-duration:1.1s"/>
    <path d="M996 415 L1004 604" stroke-width="2" stroke-dasharray="18 18" style="animation-duration:0.8s"/>
    <path d="M1001 416 L1012 604" stroke-width="1.5" stroke-dasharray="12 20" style="animation-duration:1.3s"/>
  </g>
  <path d="M974 412 C984 407 996 407 1004 412" stroke="#f3e6c8" stroke-width="3" fill="none" opacity="0.7"/>
'''
    mist = '''
  <g filter="url(#blur20)" fill="#e9f1f0">
    <ellipse cx="986" cy="600" rx="70" ry="22" opacity="0.55"/>
    <ellipse cx="986" cy="585" rx="40" ry="26" opacity="0.4"/>
  </g>
'''
    return dict(far=far, mid=mid, near=near, frame='\n'.join(frame), vines=vines, ferns=ferns, fg=fg,
                waterfall=waterfall, mist=mist)
