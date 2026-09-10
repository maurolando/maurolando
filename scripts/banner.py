"""Genera assets/header.svg, el banner del perfil.

Uso:
    python3 scripts/banner.py

No necesita dependencias ni red: escribe el SVG directamente. El dibujo es un
espectro de NBARS barras cuyo perfil de alturas sale de una suma de senos
(profile()), con el color interpolado a lo largo del eje X por color_at().

Que tocar:
    GREEN / LIGHT / BLUE  colores del degradado, de izquierda a derecha
    NBARS, BW             cantidad y ancho de las barras
    W, H, BASE            tamano del lienzo y linea de piso del espectro
    el bloque <text>      nombre y subtitulo, al final del archivo
"""

import math

W, H = 1000, 260
BASE = 214          # linea del suelo del espectro
NBARS = 58
BW = 9              # ancho de barra
pitch = W / NBARS

def lerp(a, b, t): return a + (b - a) * t
def hex2rgb(h): return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))
def rgb2hex(c): return "#%02x%02x%02x" % tuple(max(0, min(255, round(v))) for v in c)

GREEN, LIGHT, BLUE = hex2rgb("#2f9e6b"), hex2rgb("#7be39b"), hex2rgb("#4f9cf9")

def color_at(t):
    # verde cactus -> verde claro -> azul, a lo largo del eje X
    if t < 0.55:
        u = t / 0.55
        return rgb2hex([lerp(GREEN[i], LIGHT[i], u) for i in range(3)])
    u = (t - 0.55) / 0.45
    return rgb2hex([lerp(LIGHT[i], BLUE[i], u) for i in range(3)])

def profile(i):
    """Perfil de espectro: suma de senos -> se lee como audio real, no como ruido."""
    x = i / NBARS
    v = (0.55 * math.sin(x * math.pi * 2.1 + 0.4)
         + 0.30 * math.sin(x * math.pi * 5.3 + 1.1)
         + 0.18 * math.sin(x * math.pi * 11.7 + 2.3)
         + 0.10 * math.sin(x * math.pi * 19.1))
    v = (v + 1.13) / 2.26                      # normalizar a 0..1
    v *= 0.45 + 0.55 * math.sin(x * math.pi)   # atenuar en los bordes
    return max(0.10, min(1.0, v))

bars = []
for i in range(NBARS):
    cx = pitch * (i + 0.5)
    t = i / (NBARS - 1)
    h = 14 + profile(i) * 74
    col = color_at(t)
    dur = 1.05 + (i % 7) * 0.19 + (i % 3) * 0.11
    begin = -((i * 0.13) % dur)
    k = [round(0.30 + 0.70 * abs(math.sin(i * 1.7 + s * 1.9)), 3) for s in range(4)]
    vals = ";".join(str(v) for v in k + [k[0]])
    bars.append(f'''    <g transform="translate({cx:.1f} {BASE})">
      <rect x="{-BW/2}" y="{-h:.1f}" width="{BW}" height="{h:.1f}" rx="{BW/2}" fill="{col}">
        <animateTransform attributeName="transform" type="scale" values="1 {vals.replace(';',';1 ')}" dur="{dur:.2f}s" begin="{begin:.2f}s" repeatCount="indefinite" additive="sum" calcMode="spline" keySplines="{';'.join(['0.4 0 0.2 1']*4)}"/>
      </rect>
      <rect x="{-BW/2}" y="4" width="{BW}" height="{h*0.30:.1f}" rx="{BW/2}" fill="{col}" opacity="0.16"/>
    </g>''')

grid = "".join(
    f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="#7be39b" stroke-width="1" opacity="0.04"/>'
    for x in range(0, W + 1, 50))

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="maurolando">
  <title>maurolando</title>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0.35" y2="1">
      <stop offset="0%" stop-color="#040d1c"/>
      <stop offset="52%" stop-color="#08243c"/>
      <stop offset="100%" stop-color="#0a3a2d"/>
    </linearGradient>
    <radialGradient id="halo" cx="0.5" cy="1" r="0.75">
      <stop offset="0%" stop-color="#2f9e6b" stop-opacity="0.34"/>
      <stop offset="100%" stop-color="#2f9e6b" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="rule" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#2f9e6b" stop-opacity="0"/>
      <stop offset="22%" stop-color="#7be39b" stop-opacity="0.85"/>
      <stop offset="70%" stop-color="#4f9cf9" stop-opacity="0.7"/>
      <stop offset="100%" stop-color="#4f9cf9" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="card"><rect x="0" y="0" width="{W}" height="{H}" rx="14"/></clipPath>
  </defs>

  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>
    {grid}
    <ellipse cx="{W/2}" cy="{BASE}" rx="{W*0.55}" ry="150" fill="url(#halo)"/>

    <g font-family="Verdana, 'DejaVu Sans', Geneva, sans-serif">
      <text x="54" y="96" font-size="50" font-weight="bold" fill="#f2fbf6" letter-spacing="0.5">maurolando</text>
      <text x="56" y="126" font-size="14" fill="#7be39b" letter-spacing="4.2">ANALISTA DE SISTEMAS &#183; PARAGUAY</text>
    </g>

    <rect x="54" y="146" width="300" height="2" rx="1" fill="url(#rule)"/>

{chr(10).join(bars)}

    <rect x="0" y="{BASE}" width="{W}" height="1.2" fill="#7be39b" opacity="0.30"/>
    <rect x="0.75" y="0.75" width="{W-1.5}" height="{H-1.5}" rx="14" fill="none" stroke="#2f9e6b" stroke-width="1.5" opacity="0.40"/>
  </g>
</svg>
'''
open('/home/franco/maurolando-readme/assets/header.svg', 'w').write(svg)
print("barras:", NBARS, "| bytes:", len(svg))
