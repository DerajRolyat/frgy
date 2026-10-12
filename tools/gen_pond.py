import os, sys, random, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
random.seed(7)
OUT = os.path.join(ROOT, 'index.html')

def pine(x, base, h, fill, w=0.24):
    tiers = 8
    top = base - h
    L, R = [], []
    for i in range(tiers + 1):
        t = i / tiers
        y = top + h * 0.88 * t
        wid = h * w * (0.12 + t) * random.uniform(0.85, 1.1)
        if i == 0:
            continue
        L.append((x - wid, y + h * 0.02)); L.append((x - wid * 0.55, y - h * 0.035))
        R.append((x + wid, y + h * 0.02)); R.append((x + wid * 0.55, y - h * 0.035))
    pts = [(x, top)] + R + [(x + h * 0.03, base)] + [(x - h * 0.03, base)] + L[::-1]
    d = 'M' + ' L'.join(f'{a:.1f} {b:.1f}' for a, b in pts) + ' Z'
    return f'<path d="{d}" fill="{fill}"/>'

def layer(xs, base_rng, h_rng, fill, skip=None, w=0.24):
    out = []
    for x in xs:
        h = random.uniform(*h_rng)
        if skip and skip[0] < x < skip[1]:
            h *= skip[2]
        out.append(pine(x + random.uniform(-8, 8), random.uniform(*base_rng), h, fill, w))
    return '\n'.join(out)

far = layer(range(-40, 1660, 16), (548, 560), (50, 100), '#5e4b78', skip=(800, 960, 0.45))
mid = layer(range(-40, 1660, 30), (570, 590), (100, 190), '#3c3660', skip=(720, 1020, 0.0))
near = layer(list(range(-40, 660, 48)) + list(range(1080, 1680, 48)), (600, 640), (190, 320), '#262840')
frame = layer([-40, 60, 170, 1430, 1540, 1640], (720, 760), (480, 640), '#151a28', w=0.22)

def blades(n, x_rng, y_rng, h_rng, colors):
    out = []
    for _ in range(n):
        x = random.uniform(*x_rng); y = random.uniform(*y_rng); h = random.uniform(*h_rng)
        lean = random.uniform(-0.35, 0.35) * h
        c = random.choice(colors)
        out.append(f'<path d="M{x:.1f} {y:.1f} Q{x+lean*0.3:.1f} {y-h*0.6:.1f} {x+lean:.1f} {y-h:.1f}" stroke="{c}" stroke-width="{random.uniform(1.5,3):.1f}" fill="none" stroke-linecap="round"/>')
    return '\n'.join(out)

grass_front = blades(420, (-20, 1620), (960, 1010), (25, 70), ['#16211c', '#1b2922', '#22332a'])
grass_mid = blades(160, (560, 930), (880, 905), (15, 40), ['#1e2c25', '#26382e'])
reeds_l = blades(70, (60, 200), (815, 840), (60, 140), ['#141d18', '#1a261f'])
reeds_r = blades(50, (1500, 1580), (700, 725), (50, 110), ['#141d18', '#1a261f'])

stars = '\n'.join(
    f'<circle class="star" cx="{random.uniform(0,1600):.0f}" cy="{random.uniform(0,300)*random.random()+5:.0f}" r="{random.uniform(0.6,1.8):.1f}" fill="#fff" style="animation-delay:-{random.uniform(0,6):.1f}s;opacity:{random.uniform(0.4,0.9):.2f}"/>'
    for _ in range(70))

def cattail(x, y, s):
    return (f'<g transform="translate({x} {y}) scale({s})" fill="#141c18" stroke="#141c18">'
            f'<path d="M0 0 Q-3 -70 2 -150" fill="none" stroke-width="3"/>'
            f'<rect x="-4" y="-145" width="10" height="38" rx="5" stroke="none" fill="#2a1e17"/>'
            f'<path d="M0 0 Q-25 -60 -30 -110" fill="none" stroke-width="3"/>'
            f'<path d="M0 0 Q20 -50 28 -95" fill="none" stroke-width="3"/></g>')

cattails = '\n'.join([cattail(70, 850, 1.1), cattail(110, 860, 0.85), cattail(585, 830, 0.8),
                      cattail(1530, 715, 0.8), cattail(1560, 720, 0.65), cattail(1240, 730, 0.6)])

def frog(x, y, s, flip=False):
    sx = -s if flip else s
    return (f'<g class="frog" data-x="{x}" data-s="{s}" transform="translate({x} {y}) scale({sx} {s})"><g class="hopper">'
            f'<ellipse class="sac" cx="25" cy="-9" rx="8" ry="6" fill="#d9cf9c"/><use href="#frog"/></g></g>')

from water import build
water, frog_rocks = build()

frog_list = [
    frog(230, 850, 0.9), frog(405, 816, 0.75, True), frog(470, 876, 0.85),
    frog(120, 940, 1.1), frog(330, 958, 1.3, True), frog(560, 965, 1.15, True),
    frog(790, 975, 1.0), frog(985, 990, 1.25, True), frog(880, 812, 0.7),
    frog(1340, 710, 0.6), frog(1440, 716, 0.65, True), frog(1500, 965, 1.2, True),
    frog(905, 692, 0.5, True), frog(600, 806, 0.55),
]
for i, (x, y, s) in enumerate(frog_rocks[1:5]):
    frog_list.append(frog(round(x), round(y), round(0.55 * s + 0.25, 2), i % 2 == 1))
frogs = '\n'.join(frog_list)

boy = open(os.path.join(HERE, 'boy.svg')).read()

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
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@1,400&display=swap" rel="stylesheet">
<style>
  html, body {{ margin: 0; height: 100%; background: #1b1f45; overflow: hidden; }}
  svg {{ display: block; width: 100vw; height: 100vh; }}
  h1 {{
    position: fixed; top: 9vh; left: 0; right: 0; margin: 0; padding: 0 16px;
    text-align: center; font-family: "Cormorant Garamond", Georgia, serif; font-style: italic; font-weight: 400;
    font-size: clamp(34px, 6.2vw, 92px); letter-spacing: 0.02em; color: #f8e9cf;
    text-shadow: 0 0 18px rgba(255, 214, 140, 0.45), 0 2px 10px rgba(20, 15, 40, 0.6);
    pointer-events: none;
  }}
  .blink {{ animation: blink 6s infinite; transform-box: fill-box; transform-origin: center; }}
  @keyframes blink {{ 0%, 95%, 100% {{ transform: scaleY(1); }} 97% {{ transform: scaleY(0.1); }} }}
  .star {{ animation: twinkle 6s ease-in-out infinite; }}
  @keyframes twinkle {{ 50% {{ opacity: 0.15; }} }}
  .ff {{ animation: wander var(--t) ease-in-out infinite alternate; }}
  .ff > g {{ animation: glow var(--b) ease-in-out infinite; }}
  @keyframes wander {{ to {{ transform: translate(var(--dx), var(--dy)); }} }}
  @keyframes glow {{ 0%, 100% {{ opacity: 0.1; }} 40%, 60% {{ opacity: 1; }} }}
  .shimmer {{ animation: shimmer 5s ease-in-out infinite; }}
  @keyframes shimmer {{ 50% {{ opacity: 0.35; }} }}
  .hopper.hop {{ animation: hop 0.75s cubic-bezier(.3,.7,.4,1); }}
  @keyframes hop {{ 0% {{ transform: none; }} 15% {{ transform: translate(0,2px) scale(1.04,.94); }} 45% {{ transform: translate(8px,-34px) rotate(-10deg); }} 78% {{ transform: translate(0,0) scale(1.05,.95); }} 100% {{ transform: none; }} }}
  .sac {{ transform-box: fill-box; transform-origin: 20% 30%; transform: scale(0); }}
  .sac.croak {{ animation: croak 0.9s ease-in-out; }}
  @keyframes croak {{ 0%,100% {{ transform: scale(0); }} 20%,35% {{ transform: scale(1); }} 50% {{ transform: scale(.3); }} 65%,80% {{ transform: scale(1.1); }} }}
  #versions {{
    position: fixed; left: 16px; bottom: 16px; z-index: 2; display: flex; gap: 2px;
    font: 500 13px/1 system-ui, -apple-system, sans-serif; letter-spacing: .02em;
    background: rgba(20, 22, 45, .55); border: 1px solid rgba(248, 233, 207, .3); border-radius: 999px;
    padding: 4px; backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px);
  }}
  #versions a {{ color: #f8e9cf; text-decoration: none; padding: 7px 12px; border-radius: 999px; opacity: .75; }}
  #versions a:hover {{ opacity: 1; }}
  #versions a[aria-current] {{ background: rgba(248, 233, 207, .18); opacity: 1; }}
  #versions a:focus-visible {{ outline: 2px solid #f8e9cf; outline-offset: 1px; }}
  #sound {{
    position: fixed; right: 16px; bottom: 16px; z-index: 2; display: flex; align-items: center; gap: 8px;
    font: 500 14px/1 system-ui, -apple-system, sans-serif; letter-spacing: .02em; color: #f8e9cf;
    background: rgba(20, 22, 45, .55); border: 1px solid rgba(248, 233, 207, .3); border-radius: 999px;
    padding: 10px 16px; cursor: pointer; backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px);
  }}
  #sound:hover {{ background: rgba(20, 22, 45, .75); }}
  #sound:focus-visible {{ outline: 2px solid #f8e9cf; outline-offset: 2px; }}
  #sound svg {{ width: 16px; height: 16px; }}
  @media (prefers-reduced-motion: reduce) {{ .ff, .ff > g, .star, .shimmer, .blink, .hopper.hop, .sac.croak {{ animation: none; }} }}
</style>
</head>
<body data-scene="SCENE">
<h1>just a boy and his frogs</h1>
<nav id="versions" aria-label="Versions"><a href="index.html" NAV_POND>pond</a><a href="jungle.html" NAV_JUNGLE>jungle</a><a href="blocks.html" NAV_BLOCKS>blocks</a></nav>
<button id="sound" type="button" aria-pressed="false"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 5 6 9H2v6h4l5 4z"/><path d="M15.5 8.5a5 5 0 0 1 0 7M19 5a10 10 0 0 1 0 14"/></svg><span>sound on</span></button>
<svg viewBox="0 0 1600 1000" preserveAspectRatio="xMidYMid slice" role="img" aria-label="A boy standing by a forest river at dusk, smiling, with frogs around the ponds and fireflies glowing">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="600" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#171a3d"/>
      <stop offset="0.38" stop-color="#3b3470"/>
      <stop offset="0.65" stop-color="#8b5a88"/>
      <stop offset="0.85" stop-color="#e3896a"/>
      <stop offset="1" stop-color="#f7c389"/>
    </linearGradient>
    <radialGradient id="sunGlow" cx="870" cy="560" r="520" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#ffd59a" stop-opacity="0.9"/>
      <stop offset="0.3" stop-color="#ff9e6e" stop-opacity="0.35"/>
      <stop offset="1" stop-color="#ff9e6e" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="ground" x1="0" y1="580" x2="0" y2="1000" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#2f3a45"/>
      <stop offset="0.4" stop-color="#263630"/>
      <stop offset="1" stop-color="#18241f"/>
    </linearGradient>
    <linearGradient id="water" x1="0" y1="590" x2="0" y2="1000" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#e7a983"/>
      <stop offset="0.18" stop-color="#9c7290"/>
      <stop offset="0.45" stop-color="#4d5079"/>
      <stop offset="0.75" stop-color="#2a3a58"/>
      <stop offset="1" stop-color="#1a2638"/>
    </linearGradient>
    <linearGradient id="river" x1="0" y1="590" x2="0" y2="1000" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#f6bd86"/>
      <stop offset="0.25" stop-color="#b9788e"/>
      <stop offset="0.6" stop-color="#5a4d7c"/>
      <stop offset="1" stop-color="#262c52"/>
    </linearGradient>
    <linearGradient id="pond" x1="0" y1="660" x2="0" y2="920" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#9b6d8e"/>
      <stop offset="0.5" stop-color="#4c4775"/>
      <stop offset="1" stop-color="#252b4d"/>
    </linearGradient>
    <radialGradient id="vignette" cx="0.5" cy="0.45" r="0.75">
      <stop offset="0.55" stop-color="#0b0c1c" stop-opacity="0"/>
      <stop offset="1" stop-color="#0b0c1c" stop-opacity="0.65"/>
    </radialGradient>
    <radialGradient id="ffGlow">
      <stop offset="0" stop-color="#fffbd1" stop-opacity="1"/>
      <stop offset="0.25" stop-color="#e9f78a" stop-opacity="0.75"/>
      <stop offset="1" stop-color="#c7f05a" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="warmLight" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#ffd27a" stop-opacity="0.22"/>
      <stop offset="1" stop-color="#ffd27a" stop-opacity="0"/>
    </radialGradient>
    <filter id="blur6" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>
    <filter id="blur20" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="20"/></filter>

    <linearGradient id="frogSkin" x1="0" y1="-34" x2="0" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#6f8a45"/>
      <stop offset="1" stop-color="#3b4d2a"/>
    </linearGradient>
    <!-- Sitting frog, side view facing right; feet at y=0, ~70 long -->
    <g id="frog">
      <ellipse cx="0" cy="1" rx="34" ry="4" fill="#0c120f" opacity="0.45"/>
      <path d="M-30 -2 C-36 -14 -26 -30 -4 -33 C10 -35 22 -31 30 -22 C36 -15 36 -8 31 -6 C26 -4 20 -2 14 -1 L-22 -1 Z" fill="url(#frogSkin)"/>
      <path d="M-4 -6 C6 -4 18 -4 30 -7 C26 -2 18 0 8 0 L-6 0 Z" fill="#a9a56e" opacity="0.8"/>
      <path d="M-34 -2 C-38 -14 -26 -22 -12 -18 C-2 -14 -2 -4 -10 -1 Z" fill="#4d6334"/>
      <path d="M-14 -1 L4 -1 C10 -1 12 1 6 1.5 L-14 1.5 Z" fill="#3b4d2a"/>
      <path d="M17 -10 C19 -6 20 -3 22 0 L26 0 C24 -3 22 -7 21 -11 Z" fill="#4d6334"/>
      <circle cx="17" cy="-29" r="6.5" fill="#556f36"/>
      <circle cx="18" cy="-29.5" r="4.6" fill="#c99a32"/>
      <rect x="15" y="-30.6" width="6.4" height="2.2" rx="1.1" fill="#120d06"/>
      <circle cx="19.6" cy="-31.2" r="1" fill="#fff4d0" opacity="0.9"/>
      <path d="M33 -15 C26 -14 18 -15 12 -17" stroke="#24301a" stroke-width="1.4" fill="none" stroke-linecap="round"/>
      <circle cx="26" cy="-23" r="2" fill="#2c3a1f" opacity="0.7"/>
      <ellipse cx="-8" cy="-24" rx="4" ry="2.6" fill="#2c3a1f" opacity="0.6"/>
      <ellipse cx="-18" cy="-14" rx="3.5" ry="2.2" fill="#2c3a1f" opacity="0.6"/>
      <ellipse cx="4" cy="-28" rx="3" ry="2" fill="#2c3a1f" opacity="0.55"/>
      <path d="M-24 -26 C-10 -32 6 -34 18 -34" stroke="#f6b884" stroke-width="1.6" fill="none" opacity="0.45" stroke-linecap="round"/>
    </g>
    <g id="pad">
      <path d="M0 0 L38 -5 A40 13 0 1 1 34 -9 Z" fill="#2c4636"/>
      <path d="M0 0 L38 -5 A40 13 0 1 1 34 -9 Z" fill="none" stroke="#3d5d45" stroke-width="1.5"/>
    </g>
  </defs>

  <!-- Sky -->
  <rect width="1600" height="620" fill="url(#sky)"/>
  {stars}
  <rect width="1600" height="1000" fill="url(#sunGlow)"/>
  <circle cx="870" cy="548" r="42" fill="#ffe2a8"/>
  <circle cx="870" cy="548" r="70" fill="#ffd38c" opacity="0.35" filter="url(#blur20)"/>

  <!-- Forest layers -->
  {far}
  <rect x="0" y="540" width="1600" height="40" fill="#e9a07a" opacity="0.18" filter="url(#blur20)"/>
  {mid}
  {near}

  <!-- Ground -->
  <path d="M-10 600 C300 590 600 605 860 592 C1100 585 1400 600 1610 595 V1010 H-10 Z" fill="url(#ground)"/>
  {frame}

  <!-- River, side channels and ponds -->
  {water}
  <!-- bushes hiding where the river leaves the forest -->
  <g fill="#262840"><ellipse cx="1000" cy="598" rx="34" ry="12"/><ellipse cx="955" cy="600" rx="18" ry="7"/><ellipse cx="1030" cy="596" rx="22" ry="10"/></g>

  <!-- Lily pads & flowers -->
  <use href="#pad" transform="translate(230 852) scale(1)"/>
  <use href="#pad" transform="translate(405 818) scale(0.8)"/>
  <use href="#pad" transform="translate(470 878) scale(1)"/>
  <use href="#pad" transform="translate(160 822) scale(0.7)"/>
  <use href="#pad" transform="translate(320 880) scale(0.6)"/>
  <use href="#pad" transform="translate(1340 712) scale(0.6)"/>
  <use href="#pad" transform="translate(1440 718) scale(0.65)"/>
  <use href="#pad" transform="translate(1495 702) scale(0.45)"/>
  <g fill="#f3d6e2"><ellipse cx="180" cy="818" rx="7" ry="4"/><ellipse cx="320" cy="876" rx="6" ry="3.5"/><ellipse cx="1500" cy="698" rx="5" ry="3"/></g>
  <g fill="#ffd27a"><circle cx="180" cy="816" r="2"/><circle cx="320" cy="874" r="1.8"/></g>

  <!-- Mist -->
  <g filter="url(#blur20)" fill="#e7d9f0">
    <ellipse cx="900" cy="700" rx="260" ry="22" opacity="0.14"/>
    <ellipse cx="380" cy="790" rx="300" ry="20" opacity="0.12"/>
    <ellipse cx="1380" cy="690" rx="220" ry="16" opacity="0.12"/>
  </g>

  {reeds_l}
  {reeds_r}
  {cattails}
  {grass_mid}

  <!-- Warm pool of firefly light around the boy -->
  <ellipse cx="680" cy="720" rx="280" ry="300" fill="url(#warmLight)"/>

  {boy}

  {frogs}
  {grass_front}

  <rect width="1600" height="1000" fill="url(#vignette)" pointer-events="none"/>
  <g id="fireflies"></g>
</svg>
<script>
(function () {{
  var g = document.getElementById('fireflies'), NS = 'http://www.w3.org/2000/svg';
  function rnd(a, b) {{ return a + Math.random() * (b - a); }}
  function add(x, y, s) {{
    var outer = document.createElementNS(NS, 'g');
    outer.setAttribute('class', 'ff');
    outer.setAttribute('style', '--t:' + rnd(6, 14).toFixed(1) + 's;--dx:' + rnd(-60, 60).toFixed(0) + 'px;--dy:' + rnd(-45, 45).toFixed(0) + 'px;animation-delay:-' + rnd(0, 14).toFixed(1) + 's');
    var inner = document.createElementNS(NS, 'g');
    inner.setAttribute('style', '--b:' + rnd(2.5, 5).toFixed(1) + 's;animation-delay:-' + rnd(0, 5).toFixed(1) + 's');
    var halo = document.createElementNS(NS, 'circle');
    halo.setAttribute('cx', x); halo.setAttribute('cy', y); halo.setAttribute('r', 14 * s); halo.setAttribute('fill', 'url(#ffGlow)');
    var core = document.createElementNS(NS, 'circle');
    core.setAttribute('cx', x); core.setAttribute('cy', y); core.setAttribute('r', 1.8 * s); core.setAttribute('fill', '#fffde6');
    inner.appendChild(halo); inner.appendChild(core); outer.appendChild(inner); g.appendChild(outer);
  }}
  for (var i = 0; i < 70; i++) {{
    var y = rnd(330, 980);
    var x = rnd(0, 1600);
    if (Math.abs(x - 680) < 80 && Math.abs(y - 540) < 80) continue;
    add(x, y, 0.5 + (y - 330) / 650 * 0.9);
  }}
  for (var j = 0; j < 16; j++) add(rnd(560, 820), rnd(640, 900), rnd(0.9, 1.4));
  for (var k = 0; k < 4; k++) add(rnd(540, 590), rnd(440, 560), rnd(0.9, 1.2));
  for (var m = 0; m < 4; m++) add(rnd(770, 830), rnd(440, 560), rnd(0.9, 1.2));
}})();
{sound_js}
</script>
</body>
</html>
'''
html = html.replace('SCENE', 'pond').replace('NAV_POND', 'aria-current="page"').replace(' NAV_JUNGLE', '').replace(' NAV_BLOCKS', '')
open(OUT, 'w').write(html)
print('written', len(html))
