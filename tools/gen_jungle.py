import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
src = open(os.path.join(HERE, 'gen_pond.py')).read()

def rep(old, new, count=1):
    global src
    assert old in src, old[:80]
    src = src.replace(old, new, count)

rep("OUT = os.path.join(ROOT, 'index.html')", "OUT = os.path.join(ROOT, 'jungle.html')")

# Jungle layers instead of pines
rep("far = layer(", "from jungle_parts import build as _jb\nJ = _jb()\nfar = J['far']\n_far = layer(")
rep("mid = layer(", "mid = J['mid']\n_mid = layer(")
rep("near = layer(", "near = J['near']\n_near = layer(")
rep("frame = layer(", "frame = J['frame'] + J['vines']\n_frame = layer(")
rep("cattails = '\\n'.join([", "cattails = J['ferns']\n_cattails = '\\n'.join([")
rep("grass_front = blades(420, (-20, 1620), (960, 1010), (25, 70), ['#16211c', '#1b2922', '#22332a'])",
    "grass_front = blades(420, (-20, 1620), (960, 1010), (25, 70), ['#122319', '#173020', '#1d3826'])")

# Colourful rainforest frogs: red-eyed tree frogs and poison dart frogs
rep("""def frog(x, y, s, flip=False):
    sx = -s if flip else s
    return (f'<g class="frog" data-x="{x}" data-s="{s}" transform""",
"""KINDS = [
    '--fs:#5cbc3a;--fb:#eef0c0;--fl:#46a02c;--ff:#f08a2a;--fe:#e0302a;--fd:transparent',
    '--fs:#2f6fd8;--fb:#2a58b0;--fl:#2457b8;--ff:#1d4796;--fe:#141414;--fd:#0c1530',
    '--fs:#5cbc3a;--fb:#eef0c0;--fl:#46a02c;--ff:#f08a2a;--fe:#e0302a;--fd:transparent',
    '--fs:#f0c02c;--fb:#e8b828;--fl:#d9a51e;--ff:#c48f14;--fe:#141414;--fd:#151515',
    '--fs:#3cc27a;--fb:#2ea86a;--fl:#2b9e62;--ff:#21854f;--fe:#141414;--fd:#0f1a14',
]
_fc = [0]
def frog(x, y, s, flip=False):
    sx = -s if flip else s
    kind = KINDS[_fc[0] % len(KINDS)]; _fc[0] += 1
    return (f'<g class="frog" style="{kind}" data-x="{x}" data-s="{s}" transform""")

rep('fill="url(#frogSkin)"/>', 'style="fill:var(--fs,#5cbc3a)"/>')
rep('fill="#a9a56e" opacity="0.8"', 'style="fill:var(--fb,#eef0c0)" opacity="0.9"')
rep('<path d="M-34 -2 C-38 -14 -26 -22 -12 -18 C-2 -14 -2 -4 -10 -1 Z" fill="#4d6334"/>',
    '<path d="M-34 -2 C-38 -14 -26 -22 -12 -18 C-2 -14 -2 -4 -10 -1 Z" style="fill:var(--fl,#46a02c)"/>')
rep('<path d="M-14 -1 L4 -1 C10 -1 12 1 6 1.5 L-14 1.5 Z" fill="#3b4d2a"/>',
    '<path d="M-14 -1 L4 -1 C10 -1 12 1 6 1.5 L-14 1.5 Z" style="fill:var(--ff,#f08a2a)"/>')
rep('<path d="M17 -10 C19 -6 20 -3 22 0 L26 0 C24 -3 22 -7 21 -11 Z" fill="#4d6334"/>',
    '<path d="M17 -10 C19 -6 20 -3 22 0 L26 0 C24 -3 22 -7 21 -11 Z" style="fill:var(--ff,#f08a2a)"/>')
rep('<circle cx="17" cy="-29" r="6.5" fill="#556f36"/>', '<circle cx="17" cy="-29" r="6.5" style="fill:var(--fl,#46a02c)"/>')
rep('<circle cx="18" cy="-29.5" r="4.6" fill="#c99a32"/>', '<circle cx="18" cy="-29.5" r="5" style="fill:var(--fe,#e0302a)"/>')
rep('<rect x="15" y="-30.6" width="6.4" height="2.2" rx="1.1" fill="#120d06"/>',
    '<rect x="17" y="-33" width="2" height="7" rx="1" fill="#120d06"/>')
for old in ['<circle cx="26" cy="-23" r="2" fill="#2c3a1f" opacity="0.7"/>',
            '<ellipse cx="-8" cy="-24" rx="4" ry="2.6" fill="#2c3a1f" opacity="0.6"/>',
            '<ellipse cx="-18" cy="-14" rx="3.5" ry="2.2" fill="#2c3a1f" opacity="0.6"/>',
            '<ellipse cx="4" cy="-28" rx="3" ry="2" fill="#2c3a1f" opacity="0.55"/>']:
    rep(old, old.replace('fill="#2c3a1f"', 'style="fill:var(--fd,transparent)"').replace('rx="4" ry="2.6"', 'rx="6" ry="3.6"').replace('rx="3.5" ry="2.2"', 'rx="5" ry="3"'))

# Warmer, greener rainforest dusk
for a, b in [('#171a3d', '#152331'), ('#3b3470', '#2c4a58'), ('#8b5a88', '#7f7a6a'), ('#e3896a', '#e2955c'), ('#f7c389', '#f6cf86'),
             ('<stop offset="0" stop-color="#2f3a45"/>', '<stop offset="0" stop-color="#2c3f3c"/>'),
             ('<stop offset="0.4" stop-color="#263630"/>', '<stop offset="0.4" stop-color="#21392b"/>'),
             ('<stop offset="1" stop-color="#18241f"/>', '<stop offset="1" stop-color="#132218"/>'),
             ('<stop offset="0.18" stop-color="#9c7290"/>', '<stop offset="0.18" stop-color="#8d8a7a"/>'),
             ('<stop offset="0.45" stop-color="#4d5079"/>', '<stop offset="0.45" stop-color="#3d5a62"/>'),
             ('<stop offset="0.75" stop-color="#2a3a58"/>', '<stop offset="0.75" stop-color="#243e48"/>'),
             ('<stop offset="1" stop-color="#1a2638"/>', '<stop offset="1" stop-color="#162a30"/>')]:
    rep(a, b)

rep('    <filter id="blur6"', '''    <linearGradient id="falls" x1="0" y1="410" x2="0" y2="604" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#f4ead2"/><stop offset="0.5" stop-color="#cfe0e4"/><stop offset="1" stop-color="#a9c8d2"/>
    </linearGradient>
    <filter id="blur6\"''')
rep("  .star {{", "  .falls path {{ animation: falls 0.95s linear infinite; }}\n  @keyframes falls {{ to {{ stroke-dashoffset: -60; }} }}\n  .star {{")
rep(".star, .shimmer, .blink,", ".star, .shimmer, .falls path, .blink,")

rep("  {near}\n", "  {near}\n  {J['waterfall']}\n")
rep('''  <!-- bushes hiding where the river leaves the forest -->
  <g fill="#262840"><ellipse cx="1000" cy="598" rx="34" ry="12"/><ellipse cx="955" cy="600" rx="18" ry="7"/><ellipse cx="1030" cy="596" rx="22" ry="10"/></g>''',
    "  <!-- spray where the waterfall meets the river -->\n  {J['mist']}")
rep('  <rect width="1600" height="1000" fill="url(#vignette)"', "  {J['fg']}\n  <rect width=\"1600\" height=\"1000\" fill=\"url(#vignette)\"")
rep('aria-label="A boy standing by a forest river at dusk',
    'aria-label="A boy standing by a rainforest river below a waterfall at dusk')
rep("html = html.replace('SCENE', 'pond').replace('NAV_POND', 'aria-current=\"page\"').replace(' NAV_JUNGLE', '')",
    "html = html.replace('SCENE', 'jungle').replace('NAV_JUNGLE', 'aria-current=\"page\"').replace(' NAV_POND', '')")

exec(compile(src, 'gen_jungle', 'exec'))
