import math, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from water import spline_point, RIVER, CH_L, CH_R, POND_L, POND_R

OUT = os.path.join(os.path.dirname(HERE), 'blocks.html')
R = random.Random(5)
B = 32            # block size
P = B // 8        # texture pixel size
COLS, ROWS = 1600 // B, math.ceil(1000 / B)
HORIZON_ROW = 18  # y = 576

def hexmix(a, b, t):
    a = [int(a[i:i+2], 16) for i in (1, 3, 5)]; b = [int(b[i:i+2], 16) for i in (1, 3, 5)]
    return '#' + ''.join(f'{round(x + (y - x) * t):02x}' for x, y in zip(a, b))

# ---------- textures (8x8 pixel tiles) ----------
def texture(pid, palette, weights=None, holes=0.0, rows=None):
    rects = []
    for y in range(8):
        for x in range(8):
            if R.random() < holes:
                continue
            c = rows[y][x] if rows else R.choices(palette, weights=weights)[0]
            rects.append(f'<rect x="{x*P}" y="{y*P}" width="{P}" height="{P}" fill="{c}"/>')
    return f'<pattern id="{pid}" width="{B}" height="{B}" patternUnits="userSpaceOnUse">{"".join(rects)}</pattern>'

GRASS = ['#5d8f3e', '#4f7f34', '#6a9c47', '#45722e']
pats = []
for i in range(3):
    pats.append(texture(f'grass{i}', GRASS, [4, 3, 2, 2]))
pats.append(texture('dirt', ['#866043', '#79553a', '#966c4a', '#6b4a32'], [4, 3, 2, 2]))
pats.append(texture('sand', ['#d9c98f', '#cdbb80', '#e3d49e', '#c4b177'], [4, 3, 2, 1]))
pats.append(texture('water0', ['#3062b8', '#3a6fc6', '#2a56a6', '#4b82d6'], [5, 3, 3, 1]))
pats.append(texture('water1', ['#3062b8', '#3a6fc6', '#2a56a6', '#4b82d6'], [5, 3, 3, 1]))
pats.append(texture('leaves', ['#3d7a2a', '#336a22', '#4a8a34', '#2a5a1c'], [4, 3, 2, 2], holes=0.12))
pats.append(texture('log', None, rows=[[('#6b5030', '#5a4226', '#7a5c38')[(x + (y // 3)) % 3] for x in range(8)] for y in range(8)]))
lily_rows = []
for y in range(8):
    row = []
    for x in range(8):
        d = math.hypot(x - 3.5, y - 3.5)
        if d < 3.6 and not (x >= 4 and 2.5 < y < 4.5):
            row.append(R.choice(['#2f6a20', '#3a7a28', '#285a1a']))
        else:
            row.append('none')
    lily_rows.append(row)
pats.append('<pattern id="lily" width="32" height="32" patternUnits="userSpaceOnUse">' + ''.join(
    f'<rect x="{x*P}" y="{y*P}" width="{P}" height="{P}" fill="{lily_rows[y][x]}"/>' for y in range(8) for x in range(8) if lily_rows[y][x] != 'none') + '</pattern>')

# ---------- terrain classification ----------
def dense(ctrl, n=400):
    return [spline_point(ctrl, i / n) for i in range(n + 1)]
RIV, CL, CR = dense(RIVER), dense(CH_L, 120), dense(CH_R, 120)

def in_stream(pts, x, y, pad=0):
    return any((x - px) ** 2 + (y - py) ** 2 < (w / 2 + pad) ** 2 for px, py, w in pts)

def in_pond(p, x, y, pad=0):
    cx, cy, rx, ry = p
    return ((x - cx) / (rx + pad)) ** 2 + ((y - cy) / (ry + pad * 0.6)) ** 2 < 1

def is_water(x, y, pad=0):
    return in_stream(RIV, x, y, pad) or in_stream(CL, x, y, pad) or in_stream(CR, x, y, pad) or in_pond(POND_L, x, y, pad) or in_pond(POND_R, x, y, pad)

cells = []
lily_cells = []
for r in range(HORIZON_ROW, ROWS):
    for c in range(COLS):
        x, y = c * B + B / 2, r * B + B / 2
        if is_water(x, y):
            mat = f'water{R.randint(0, 1)}'
            if (in_pond(POND_L, x, y, -20) or in_pond(POND_R, x, y, -8)) and R.random() < 0.28:
                lily_cells.append((c, r))
        elif is_water(x, y, pad=B * 0.7):
            mat = 'sand' if R.random() < 0.7 else 'dirt'
        else:
            mat = f'grass{R.randint(0, 2)}'
        cells.append(f'<rect x="{c*B}" y="{r*B}" width="{B}" height="{B}" fill="url(#{mat})"/>')
lilies = ''.join(f'<rect x="{c*B}" y="{r*B}" width="{B}" height="{B}" fill="url(#lily)"/>' for c, r in lily_cells)

# Grid lines give the "placed block" look
grid = ''.join(f'<path d="M0 {r*B} H1600" />' for r in range(HORIZON_ROW, ROWS)) + ''.join(f'<path d="M{c*B} {HORIZON_ROW*B} V1000"/>' for c in range(COLS))

# ---------- sky ----------
SKY = ['#1b1d48', '#24245a', '#2f2b68', '#3d3274', '#4e397c', '#633f80', '#7a4680', '#924e7c', '#aa5876',
       '#c0646c', '#d27262', '#df8259', '#e89354', '#eea353', '#f2b257', '#f5bf5e', '#f7ca68', '#f8d273']
sky = ''.join(f'<rect x="0" y="{i*B}" width="1600" height="{B}" fill="{c}"/>' for i, c in enumerate(SKY))
stars = ''.join(f'<rect class="star" x="{R.randrange(0, 400)*4}" y="{R.randrange(0, 60)*4}" width="4" height="4" fill="#fff" style="animation-delay:-{R.uniform(0,6):.1f}s;opacity:{R.uniform(.4,.9):.2f}"/>' for _ in range(60))
clouds = []
for cx, cy, w in [(160, 192, 7), (420, 128, 5), (1180, 160, 8), (1430, 224, 5), (700, 256, 4)]:
    clouds.append(f'<rect x="{cx}" y="{cy}" width="{w*B}" height="{B}" fill="#f6b8a0" opacity="0.55"/>')
    clouds.append(f'<rect x="{cx + B}" y="{cy - B//2}" width="{(w-2)*B}" height="{B//2}" fill="#f6b8a0" opacity="0.55"/>')
sun = ''.join(f'<rect x="{870-s/2}" y="{528-s/2}" width="{s}" height="{s}" fill="#ffd27a" opacity="{o}"/>' for s, o in [(320, 0.08), (240, 0.12), (176, 0.2)])
sun += '<rect x="822" y="480" width="96" height="96" fill="#ffe6a6"/><rect x="838" y="496" width="64" height="64" fill="#fff2c8"/>'

# ---------- trees (16px grid silhouettes in the distance) ----------
def spruce(cx, base, h, fill, u=16):
    out = []
    widths = [1, 3, 3, 5, 3, 5, 7, 5, 7, 9]
    rows = widths[:h]
    for i, w in enumerate(rows):
        y = base - (h + 1 - i) * u
        out.append(f'<rect x="{cx - (w//2)*u}" y="{y}" width="{w*u}" height="{u}" fill="{fill}"/>')
    out.append(f'<rect x="{cx}" y="{base - u}" width="{u}" height="{u}" fill="{fill}"/>')
    return ''.join(out)

far = []
for cx in range(-16, 1616, 48):
    h = R.randint(5, 8)
    if 800 < cx < 1000:
        h = R.randint(2, 4)
    far.append(spruce(cx - cx % 16, 576, h, '#4b3d70'))
mid = []
for cx in list(range(-32, 720, 80)) + list(range(1080, 1650, 80)):
    mid.append(spruce(cx - cx % 16, 592, R.randint(7, 10), '#2f2a52', 16))

def oak(cx, base, trunk, leaf_w, leaf_h):
    """Blocky oak in textured blocks, cx/base on the 32px grid."""
    out = []
    for i in range(trunk):
        out.append(f'<rect x="{cx}" y="{base - (i+1)*B}" width="{B}" height="{B}" fill="url(#log)"/>')
    top = base - trunk * B
    for j in range(leaf_h):
        w = leaf_w if j < leaf_h - 1 else leaf_w - 2
        x0 = cx - (w // 2) * B
        out.append(f'<rect x="{x0}" y="{top - (j+1)*B + B}" width="{w*B}" height="{B}" fill="url(#leaves)"/>')
    out.append(f'<rect x="{cx - B}" y="{top - leaf_h*B + B - B}" width="{3*B}" height="{B}" fill="url(#leaves)"/>')
    return ''.join(out)

oaks = ''.join([oak(64, 640, 4, 5, 3), oak(288, 608, 3, 5, 2), oak(1248, 608, 3, 5, 2), oak(1472, 640, 4, 5, 3),
                oak(512, 640, 3, 3, 2), oak(1120, 640, 3, 3, 2)])
# Big framing trees at the edges
frame = oak(-32, 1024, 12, 7, 4) + oak(1600, 1024, 12, 7, 4)

# ---------- character (Minecraft-style, 12px pixels) ----------
CP = 12
C = {'H': '#c49359', 'h': '#9a6c3f', 'S': '#f2c6a8', 's': '#e0ad8d', 'W': '#ffffff', 'E': '#5f8f8a', 'F': '#c8876a',
     'M': '#a9554f', 'T': '#fbf6ee', 'G': '#4c4f54', 'g': '#3e4146', 'k': '#5a5d63', 'J': '#3f4d6c', 'j': '#334058',
     'O': '#cfc8ba', 'o': '#a9a396'}
head = ['HHHHHHHHHHHHHHHH',
        'HHLHHHHLHHHHLHHH',
        'HHHHLHHHHHLHHHHH',
        'HHhHHHHhHHHHHhHH',
        'HHHHHLHHHHHLHHHH',
        'hHHSHHHSHHHSHHHh',
        'hHSSSHSSSSHSSSHh',
        'hSSBBBSSSSBBBSSh',
        'hSWEPSSSSSSPEWSh',
        'SSWEESSSSSSEEWSS',
        'SFSFSSSNNSSSFSFS',
        'SCFCFSSNsSSFCFCS',
        'SSCSSSSSSSSSSCSS',
        'SSSSMTTTTTTMSSSS',
        'SSSSSMRRRRMSSSSS',
        'SSSSSSSSSSSSSSSS']
C.update({'L': '#dcae72', 'B': '#a87a4c', 'P': '#1d2a2a', 'N': '#e6b192', 'R': '#d98d86', 'C': '#f0b49c', 'F': '#d39474'})
body = ['kGGSSGGg'] + ['kGGGGGGg'] * 10 + ['gggggggg']
arm_l = ['kGGG'] * 4 + ['SSSs'] * 7 + ['sSSs']
arm_r = ['GGGg'] * 4 + ['SSSs'] * 7 + ['sSSs']
leg_l = ['JJJj'] * 10 + ['OOOo'] * 2
leg_r = ['JJjj'] * 10 + ['OOoo'] * 2

def sprite(rows, ox, oy, px, extra=''):
    out = []
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != '.':
                out.append(f'<rect x="{ox + x*px}" y="{oy + y*px}" width="{px}" height="{px}" fill="{C.get(ch, ch)}"{extra}/>')
    return ''.join(out)

bx, by = 680 - 8 * CP, 976 - 32 * CP   # top-left of the 16x32 figure
boy = ''.join([
    f'<rect x="{bx}" y="{976 - 6}" width="{16*CP}" height="10" fill="#000" opacity="0.35"/>',
    sprite(leg_l, bx + 4*CP, by + 20*CP, CP), sprite(leg_r, bx + 8*CP, by + 20*CP, CP),
    sprite(arm_l, bx, by + 8*CP, CP), sprite(arm_r, bx + 12*CP, by + 8*CP, CP),
    sprite(body, bx + 4*CP, by + 8*CP, CP),
    sprite(head, bx + 4*CP, by, CP // 2),
    # shading on the head's right side for a little depth
    f'<rect x="{bx + 11*CP}" y="{by + 3*CP}" width="{CP}" height="{5*CP}" fill="#000" opacity="0.06"/>',
])
# blinking eyes: skin-coloured lids over each eye
lids = (f'<g class="lids"><rect x="{bx + 4*CP + 2*6}" y="{by + 8*6}" width="18" height="12" fill="#f2c6a8"/>'
        f'<rect x="{bx + 4*CP + 11*6}" y="{by + 8*6}" width="18" height="12" fill="#f2c6a8"/></g>')

# ---------- frogs ----------
FROG = ['.......BB..',
        '......BWEB.',
        '..BBBBBBBBB',
        '.BBBBBBBBMM',
        'BBDBBBLLLL.',
        'BDDDBLLLL..',
        'DD.DD..FF..']
VARIANTS = [  # temperate (orange), cold (green), warm (cream)
    {'B': '#c9733f', 'D': '#9a5530', 'L': '#e8c290', 'W': '#f1e3b0', 'E': '#1a1a1a', 'M': '#6e3a20', 'F': '#9a5530'},
    {'B': '#5f8f45', 'D': '#44693a', 'L': '#a9c47a', 'W': '#e6edc0', 'E': '#1a1a1a', 'M': '#2f4a26', 'F': '#44693a'},
    {'B': '#e0d2b0', 'D': '#b39a70', 'L': '#f2ead2', 'W': '#fff6dc', 'E': '#1a1a1a', 'M': '#8a7450', 'F': '#b39a70'},
]
FP = 6
def frog(x, y, s=1.0, flip=False, v=0):
    pal = VARIANTS[v % 3]
    rects = []
    for ry, row in enumerate(FROG):
        for rx, ch in enumerate(row):
            if ch != '.':
                rects.append(f'<rect x="{rx*FP}" y="{(ry-7)*FP}" width="{FP}" height="{FP}" fill="{pal[ch]}"/>')
    sac = f'<rect class="sac" x="{8*FP}" y="{-3*FP}" width="{3*FP}" height="{2*FP}" fill="{pal["L"]}"/>'
    sx = -s if flip else s
    return (f'<g class="frog" data-x="{x}" data-s="{s}" transform="translate({x} {y}) scale({sx} {s}) translate({-5.5*FP} 0)">'
            f'<g class="hopper">{"".join(rects)}{sac}</g></g>')

# Frogs on lily pads, banks and the boy's head
pad_frogs = [lily_cells[i] for i in range(0, len(lily_cells), max(1, len(lily_cells) // 7))][:7]
frogs = [frog(c*B + 16, r*B + 26, 0.55, i % 2 == 1, i) for i, (c, r) in enumerate(pad_frogs)]
frogs += [frog(150, 960, 1.0, False, 0), frog(360, 975, 1.1, True, 1), frog(560, 968, 0.9, True, 2),
          frog(820, 975, 1.0, False, 1), frog(1000, 985, 1.15, True, 0), frog(1520, 975, 1.1, True, 2),
          frog(880, 800, 0.6, False, 2), frog(1240, 690, 0.45, False, 1)]
frogs.append(frog(680, by + 2, 0.7, False, 0))  # sitting on his head

# ---------- torches ----------
def torch(x, y):
    return (f'<rect x="{x-12}" y="{y-12}" width="24" height="24" fill="#ffcf6a" opacity="0.25" class="flicker"/>'
            f'<rect x="{x-4}" y="{y}" width="8" height="40" fill="#6b5030"/>'
            f'<rect x="{x-4}" y="{y-8}" width="8" height="8" fill="#ffd54a"/>'
            f'<rect x="{x-4}" y="{y-12}" width="4" height="4" fill="#ff8a2a" class="flicker"/>')
torches = torch(520, 900) + torch(860, 880)
glows = ''.join(f'<circle cx="{x}" cy="{y}" r="150" fill="url(#torchGlow)" class="flicker"/>' for x, y in [(520, 900), (860, 880)])

# Small flowers and grass tufts in pixels
tufts = []
for _ in range(70):
    x = R.randrange(0, 400) * 4; y = R.randrange(150, 250) * 4
    if is_water(x, y, 10) or (590 < x < 780 and y > 580):
        continue
    col = R.choice(['#3c6a2a', '#4a7a32', '#ff5a5a', '#ffd84a', '#5a8ae0'])
    if col.startswith('#3') or col.startswith('#4'):
        tufts.append(f'<rect x="{x}" y="{y-8}" width="4" height="8" fill="{col}"/><rect x="{x+4}" y="{y-12}" width="4" height="12" fill="{col}"/><rect x="{x+8}" y="{y-6}" width="4" height="6" fill="{col}"/>')
    else:
        tufts.append(f'<rect x="{x+4}" y="{y-8}" width="4" height="8" fill="#3c6a2a"/><rect x="{x}" y="{y-16}" width="12" height="8" fill="{col}"/><rect x="{x+4}" y="{y-12}" width="4" height="4" fill="#ffe9a0"/>')

sound_js = open(os.path.join(HERE, 'sound.js')).read()

html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Just a Boy and His Frogs</title>
<meta name="description" content="just a boy and his frogs">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Pixelify+Sans:wght@600&display=swap" rel="stylesheet">
<style>
  html, body {{ margin: 0; height: 100%; background: #1b1d48; overflow: hidden; }}
  svg {{ display: block; width: 100vw; height: 100vh; shape-rendering: crispEdges; }}
  h1 {{
    position: fixed; top: 8vh; left: 0; right: 0; margin: 0; padding: 0 16px; text-align: center;
    font-family: "Pixelify Sans", "Courier New", monospace; font-weight: 600;
    font-size: clamp(30px, 5.4vw, 80px); letter-spacing: 0.02em; color: #fff7d6;
    text-shadow: 4px 4px 0 #3b3355, 0 0 24px rgba(255, 210, 120, .35); pointer-events: none;
  }}
  .star {{ animation: twinkle 6s steps(2) infinite; }}
  @keyframes twinkle {{ 50% {{ opacity: 0.1; }} }}
  .flicker {{ animation: flicker 1.6s steps(3) infinite; }}
  @keyframes flicker {{ 50% {{ opacity: .55; }} }}
  .lids {{ opacity: 0; animation: lids 5s steps(1) infinite; }}
  @keyframes lids {{ 0%, 96% {{ opacity: 0; }} 97%, 100% {{ opacity: 1; }} }}
  .ff {{ animation: wander var(--t) steps(12) infinite alternate; }}
  .ff > g {{ animation: glow var(--b) steps(4) infinite; }}
  @keyframes wander {{ to {{ transform: translate(var(--dx), var(--dy)); }} }}
  @keyframes glow {{ 0%, 100% {{ opacity: 0.1; }} 40%, 60% {{ opacity: 1; }} }}
  .hopper.hop {{ animation: hop 0.7s steps(7); }}
  @keyframes hop {{ 0% {{ transform: none; }} 40% {{ transform: translate(6px, -36px); }} 80% {{ transform: translate(0, 0); }} 100% {{ transform: none; }} }}
  .sac {{ transform-box: fill-box; transform-origin: 0 50%; transform: scale(0); }}
  .sac.croak {{ animation: croak 0.9s steps(6); }}
  @keyframes croak {{ 0%,100% {{ transform: scale(0); }} 20%,35% {{ transform: scale(1); }} 50% {{ transform: scale(.4); }} 65%,80% {{ transform: scale(1.1); }} }}
  #versions, #sound {{
    position: fixed; bottom: 16px; z-index: 2; display: flex; align-items: center;
    font: 600 14px/1 "Pixelify Sans", "Courier New", monospace; color: #fff7d6;
    background: rgba(40, 36, 70, .8); border: 3px solid #12101e; box-shadow: inset -3px -3px 0 rgba(0,0,0,.35), inset 3px 3px 0 rgba(255,255,255,.15);
  }}
  #versions {{ left: 16px; gap: 2px; padding: 3px; }}
  #versions a {{ color: inherit; text-decoration: none; padding: 7px 10px; opacity: .75; }}
  #versions a:hover {{ opacity: 1; }}
  #versions a[aria-current] {{ background: rgba(255, 247, 214, .18); opacity: 1; }}
  #sound {{ right: 16px; gap: 8px; padding: 9px 14px; cursor: pointer; }}
  #sound:hover {{ background: rgba(60, 54, 100, .9); }}
  #versions a:focus-visible, #sound:focus-visible {{ outline: 3px solid #fff7d6; outline-offset: 2px; }}
  #sound svg {{ width: 16px; height: 16px; }}
  @media (prefers-reduced-motion: reduce) {{ .ff, .ff > g, .star, .flicker, .lids, .hopper.hop, .sac.croak {{ animation: none; }} }}
</style>
</head>
<body data-scene="blocks">
<h1>just a boy and his frogs</h1>
<nav id="versions" aria-label="Versions"><a href="index.html">pond</a><a href="jungle.html">jungle</a><a href="blocks.html" aria-current="page">blocks</a></nav>
<button id="sound" type="button" aria-pressed="false"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="square"><path d="M11 5 6 9H2v6h4l5 4z"/><path d="M15.5 8.5a5 5 0 0 1 0 7M19 5a10 10 0 0 1 0 14"/></svg><span>sound on</span></button>
<svg viewBox="0 0 1600 1000" preserveAspectRatio="xMidYMid slice" role="img" aria-label="A blocky, Minecraft-style scene: a boy with a frog on his head stands by a river and ponds at dusk, with frogs and fireflies around">
  <defs>
    {''.join(pats)}
    <linearGradient id="dusk" x1="0" y1="576" x2="0" y2="1000" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#2a2358" stop-opacity="0.6"/>
      <stop offset="1" stop-color="#1a1638" stop-opacity="0.38"/>
    </linearGradient>
    <radialGradient id="torchGlow">
      <stop offset="0" stop-color="#ffc864" stop-opacity="0.35"/>
      <stop offset="1" stop-color="#ffc864" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="vignette" cx="0.5" cy="0.45" r="0.75">
      <stop offset="0.55" stop-color="#0b0c1c" stop-opacity="0"/>
      <stop offset="1" stop-color="#0b0c1c" stop-opacity="0.6"/>
    </radialGradient>
    <filter id="ffblur" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="5"/></filter>
  </defs>

  {sky}
  {stars}
  {sun}
  {''.join(clouds)}
  {''.join(far)}
  {''.join(mid)}

  <!-- terrain -->
  {''.join(cells)}
  {lilies}
  <g stroke="#000" stroke-opacity="0.12" stroke-width="1">{grid}</g>
  <rect x="0" y="{HORIZON_ROW*B}" width="1600" height="6" fill="#000" opacity="0.18"/>
  {oaks}
  {''.join(tufts)}
  {torches}
  <rect x="0" y="{HORIZON_ROW*B}" width="1600" height="{1000 - HORIZON_ROW*B}" fill="url(#dusk)" style="mix-blend-mode:multiply"/>
  {glows}
  {boy}
  {lids}
  {''.join(frogs)}
  {frame}
  <rect width="1600" height="1000" fill="url(#vignette)" pointer-events="none"/>
  <g id="fireflies"></g>
</svg>
<script>
(function () {{
  var g = document.getElementById('fireflies'), NS = 'http://www.w3.org/2000/svg';
  function rnd(a, b) {{ return a + Math.random() * (b - a); }}
  function add(x, y, s) {{
    x = Math.round(x / 4) * 4; y = Math.round(y / 4) * 4;
    var outer = document.createElementNS(NS, 'g');
    outer.setAttribute('class', 'ff');
    outer.setAttribute('style', '--t:' + rnd(6, 14).toFixed(1) + 's;--dx:' + (Math.round(rnd(-15, 15)) * 4) + 'px;--dy:' + (Math.round(rnd(-12, 12)) * 4) + 'px;animation-delay:-' + rnd(0, 14).toFixed(1) + 's');
    var inner = document.createElementNS(NS, 'g');
    inner.setAttribute('style', '--b:' + rnd(2.5, 5).toFixed(1) + 's;animation-delay:-' + rnd(0, 5).toFixed(1) + 's');
    var sz = Math.round(4 * s), halo = document.createElementNS(NS, 'rect');
    halo.setAttribute('x', x - sz * 2); halo.setAttribute('y', y - sz * 2); halo.setAttribute('width', sz * 5); halo.setAttribute('height', sz * 5);
    halo.setAttribute('fill', '#d8f56a'); halo.setAttribute('opacity', '0.6'); halo.setAttribute('filter', 'url(#ffblur)');
    var core = document.createElementNS(NS, 'rect');
    core.setAttribute('x', x); core.setAttribute('y', y); core.setAttribute('width', sz); core.setAttribute('height', sz); core.setAttribute('fill', '#fffbd0');
    inner.appendChild(halo); inner.appendChild(core); outer.appendChild(inner); g.appendChild(outer);
  }}
  for (var i = 0; i < 70; i++) {{
    var y = rnd(330, 980), x = rnd(0, 1600);
    if (Math.abs(x - 680) < 70 && Math.abs(y - 640) < 70) continue;
    add(x, y, 1 + (y - 330) / 650);
  }}
  for (var j = 0; j < 14; j++) add(rnd(540, 840), rnd(720, 940), rnd(1.5, 2));
}})();
{sound_js}
</script>
</body>
</html>
'''
open(OUT, 'w').write(html)
print('written', len(html), 'lilies', len(lily_cells))
