"""Genera assets/header.svg, el banner del perfil.

Uso:
    python3 scripts/banner.py

No necesita dependencias ni red: escribe el SVG directamente. El dibujo es una
terminal donde se tipea el comando CMD y despues aparece una salida estilo
neofetch: el cactus de CACTUS a la izquierda y los datos de INFO a la derecha.

Que tocar:
    CMD, USER, HOST       lo que se tipea y el prompt
    CACTUS                arte ASCII, una fila por linea de la salida
    INFO                  pares (etiqueta, valor) al lado del cactus
    PALETA                bloques de color del final, como en neofetch
    T_INICIO, T_LINEA     ritmo de la animacion, en segundos
    scripts/fontpaths.py  tipografia y tamano: regenera glyphs.json

La animacion corre una sola vez. Cada elemento esta visible por defecto y un
<set> lo oculta hasta su turno, asi un visor sin animaciones muestra el cuadro
final completo en vez de una terminal vacia.
"""

import json
import os

# Contornos de la tipografia, generados por fontpaths.py.
# Van como path y no como <text> porque GitHub sanea los SVG: la fuente
# no llegaria al visitante y el texto caeria al fallback del sistema.
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "glyphs.json")) as fh:
    GLIFOS = json.load(fh)

USER, HOST, CMD = "maurolando", "desierto", "maurolando"

CACTUS = [
    "      .--.     ",
    "      |  |   _ ",
    "  _   |  |  | |",
    " | |  |  |__| |",
    " | |__|  .----'",
    " '----.  |     ",
    "      |  |     ",
    "      |  |     ",
    "      |  |     ",
    " ~~~~~'~~'~~~~~",
]

INFO = [
    ("Rol", "Analista de Sistemas"),
    ("Título", "Lic. en Análisis de Sistemas"),
    ("Backend", "Java · Spring · GraphQL"),
    ("Frontend", "Angular · TypeScript · Ionic"),
    ("Datos", "PostgreSQL · MySQL · Supabase"),
    ("Fuera", "playlists largas y Steam"),
]

PALETA = ["#0a3a2d", "#1f5a45", "#2f9e6b", "#7be39b", "#4f9cf9", "#8aa3a0", "#cfe8dc", "#f2fbf6"]

W = 1000
BARRA = 40                      # alto de la barra de titulo de la ventana
ADV = GLIFOS["avance"]          # ancho de celda
LH = 25                         # alto de linea
X0, Y0 = 34, BARRA + 38         # linea base de la primera fila
COL_INFO = len(CACTUS[0]) + 4   # columna donde arrancan los datos
NFILAS = 1 + len(CACTUS) + 1    # comando + salida + prompt final
H = Y0 + (NFILAS - 1) * LH + 26

T_INICIO = 0.9                  # espera antes de empezar a tipear
T_LINEA = 0.07                  # separacion entre lineas de la salida

BLANCO, CLARO, VERDE, AZUL, GRIS, TEXTO = "#f2fbf6", "#7be39b", "#2f9e6b", "#4f9cf9", "#8aa3a0", "#cfe8dc"

def lerp(a, b, t): return a + (b - a) * t
def hex2rgb(h): return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))
def rgb2hex(c): return "#%02x%02x%02x" % tuple(max(0, min(255, round(v))) for v in c)
def cx(col): return round(X0 + col * ADV, 2)
def cy(fila): return Y0 + fila * LH

usados = set()

def gid(ch, bold):
    usados.add((ch, bold))
    return f"{'b' if bold else 'r'}{ord(ch):x}"

def oculto(hasta):
    return f'<set attributeName="opacity" to="0" begin="0s" dur="{hasta:.2f}s"/>'

def texto(s, col, fila, color, bold=False):
    """Un tramo de texto de un color, alineado a la grilla de celdas."""
    usos = "".join(f'<use href="#{gid(ch, bold)}" x="{cx(col + i)}"/>'
                   for i, ch in enumerate(s) if ch != " ")
    return f'<g fill="{color}" transform="translate(0 {cy(fila)})">{usos}</g>'

def prompt(fila):
    partes, col = [], 0
    for s, color, bold in [(f"{USER}@{HOST}", CLARO, True), (":", BLANCO, False),
                           ("~", AZUL, True), ("$", BLANCO, False)]:
        partes.append(texto(s, col, fila, color, bold))
        col += len(s)
    return "".join(partes), col + 1

# --- linea 0: el comando, tipeado caracter por caracter --------------------
prompt0, col_cmd = prompt(0)
tiempos, t = [], T_INICIO
for i in range(len(CMD)):
    tiempos.append(t)
    t += 0.09 + ((i * 7) % 5) * 0.03      # ritmo irregular, como una mano
t_enter = tiempos[-1] + 0.5

tipeo = "".join(
    f'<use href="#{gid(ch, False)}" x="{cx(col_cmd + i)}" y="{cy(0)}">{oculto(tiempos[i])}</use>'
    for i, ch in enumerate(CMD))

# cursor que avanza con el tipeo; desaparece al dar enter
xs = [cx(col_cmd + i) for i in range(len(CMD) + 1)]
kt = [0] + [round(v / t_enter, 4) for v in tiempos]
cursor_tipeo = (
    f'<rect x="{xs[0]}" y="{cy(0) - 18}" width="{ADV - 1.5}" height="23" fill="{CLARO}" opacity="0">'
    f'<set attributeName="opacity" to="0.9" begin="0s" dur="{t_enter:.2f}s"/>'
    f'<animate attributeName="x" calcMode="discrete" values="{";".join(map(str, xs))}" '
    f'keyTimes="{";".join(map(str, kt))}" dur="{t_enter:.2f}s" fill="freeze"/></rect>')

# --- salida: cactus a la izquierda, datos a la derecha ---------------------
datos = [[(f"{USER}@{HOST}", CLARO, True)],
         [("-" * len(f"{USER}@{HOST}"), GRIS, False)]]
datos += [[(f"{k}:", CLARO, True), (f" {v}", TEXTO, False)] for k, v in INFO]

C_ARRIBA, C_ABAJO = hex2rgb(CLARO), hex2rgb(VERDE)
salida = []
for i, linea in enumerate(CACTUS):
    fila = 1 + i
    piso = i == len(CACTUS) - 1
    color = GRIS if piso else rgb2hex(
        [lerp(C_ARRIBA[c], C_ABAJO[c], i / (len(CACTUS) - 2)) for c in range(3)])
    partes = [texto(linea, 0, fila, color, bold=not piso)]
    if piso:  # el cactus atraviesa la linea del suelo
        partes.append(texto("".join(ch if ch == "'" else " " for ch in linea),
                            0, fila, rgb2hex(C_ABAJO), True))
    col = COL_INFO
    for s, c, bold in (datos[i] if i < len(datos) else []):
        partes.append(texto(s, col, fila, c, bold))
        col += len(s)
    if piso:
        partes += [f'<rect x="{cx(COL_INFO + 3 * j)}" y="{cy(fila) - 17}" width="{ADV * 3:.2f}" '
                   f'height="21" fill="{c}"/>' for j, c in enumerate(PALETA)]
    salida.append(f'    <g>{oculto(t_enter + 0.15 + i * T_LINEA)}{"".join(partes)}</g>')

# --- prompt final, con el cursor parpadeando -------------------------------
t_fin = t_enter + 0.15 + len(CACTUS) * T_LINEA + 0.15
fila_fin = NFILAS - 1
prompt1, col_fin = prompt(fila_fin)
final = (
    f'<g>{oculto(t_fin)}{prompt1}'
    f'<rect x="{cx(col_fin)}" y="{cy(fila_fin) - 18}" width="{ADV - 1.5}" height="23" fill="{CLARO}" opacity="0.9">'
    f'<animate attributeName="opacity" calcMode="discrete" values="0.9;0" keyTimes="0;0.5" '
    f'dur="1.1s" begin="{t_fin:.2f}s" repeatCount="indefinite"/></rect></g>')

# titulo de la ventana: mismo glifo, mas chico y centrado
titulo = f"{USER}@{HOST}: ~"
K_TIT = 0.72
titulo_svg = (
    f'<g fill="{GRIS}" transform="translate({W / 2 - len(titulo) * ADV * K_TIT / 2:.1f} {BARRA / 2 + 5}) scale({K_TIT})">'
    + "".join(f'<use href="#{gid(ch, False)}" x="{round(i * ADV, 2)}"/>'
              for i, ch in enumerate(titulo) if ch != " ") + "</g>")

botones = "".join(f'<circle cx="{24 + i * 20}" cy="{BARRA / 2}" r="6" fill="{c}"/>'
                  for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]))

defs = "\n".join(
    f'    <path id="{gid(ch, bold)}" d="{GLIFOS["bold" if bold else "regular"][ch]}"/>'
    for ch, bold in sorted(usados))

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{USER}">
  <title>{USER}</title>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0.35" y2="1">
      <stop offset="0%" stop-color="#040d1c"/>
      <stop offset="52%" stop-color="#08243c"/>
      <stop offset="100%" stop-color="#0a3a2d"/>
    </linearGradient>
    <radialGradient id="halo" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0%" stop-color="#2f9e6b" stop-opacity="0.30"/>
      <stop offset="100%" stop-color="#2f9e6b" stop-opacity="0"/>
    </radialGradient>
    <clipPath id="card"><rect x="0" y="0" width="{W}" height="{H}" rx="14"/></clipPath>
{defs}
  </defs>

  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>
    <ellipse cx="{cx(len(CACTUS[0]) / 2)}" cy="{cy(len(CACTUS) / 2)}" rx="230" ry="190" fill="url(#halo)"/>

    <rect width="{W}" height="{BARRA}" fill="#020810" opacity="0.55"/>
    <rect y="{BARRA}" width="{W}" height="1" fill="{CLARO}" opacity="0.18"/>
    {botones}
    {titulo_svg}

    {prompt0}
    <g fill="{BLANCO}">{tipeo}</g>
    {cursor_tipeo}

{chr(10).join(salida)}

    {final}

    <rect x="0.75" y="0.75" width="{W-1.5}" height="{H-1.5}" rx="14" fill="none" stroke="{VERDE}" stroke-width="1.5" opacity="0.40"/>
  </g>
</svg>
'''
destino = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "assets", "header.svg")
with open(destino, "w") as fh:
    fh.write(svg)
print("glifos:", len(usados), "| alto:", H, "| bytes:", len(svg), "->", destino)
