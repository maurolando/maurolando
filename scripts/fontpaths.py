"""Convierte los textos del header a paths SVG y los deja en textpaths.json.

Solo hay que correrlo si cambia el texto o la tipografia del header.
banner.py lee el JSON y no necesita estas dependencias.

    python3 -m venv venv && ./venv/bin/pip install fonttools uharfbuzz
    ./venv/bin/python scripts/fontpaths.py

Los .otf no estan en el repo: son de uso personal y no se redistribuyen.
Para regenerar hay que bajarlos a assets/fonts/ (ver .gitignore):

    Highrise (Bold, demo)  https://www.dafont.com/es/highrise.font
    First Encounter        https://www.dafont.com/es/first-encounter.font

El header ya renderiza sin ellos: los contornos viajan dentro del SVG.

GitHub sanea los SVG: un font-family externo hace fallback y un @font-face
remoto lo bloquea. Por eso el texto va como contorno, no como <text>.
"""
import json
import os

import uharfbuzz as hb
from fontTools.misc.transform import Transform
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "assets", "fonts")

# (clave, archivo, texto, tamano)
PIEZAS = [
    ("titulo", "HighriseFont-Bold-Demo.otf", "MAUROLANDO", 72),
    ("subtitulo", "FirstEncounter_PERSONAL_USE_ONLY.otf", "Analista de Sistemas", 27),
]


def shape(ruta, texto):
    """Devuelve [(nombre_glifo, x, y), ...] ya posicionados, y el avance total."""
    with open(ruta, "rb") as fh:
        face = hb.Face(fh.read())
    font = hb.Font(face)
    font.scale = (face.upem, face.upem)

    buf = hb.Buffer()
    buf.add_str(texto)
    buf.guess_segment_properties()
    hb.shape(font, buf)          # liga/calt: la cursiva tiene que conectar

    orden = TTFont(ruta, fontNumber=0).getGlyphOrder()
    salida, x, y = [], 0.0, 0.0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        salida.append((orden[info.codepoint], x + pos.x_offset, y - pos.y_offset))
        x += pos.x_advance
        y += pos.y_advance
    return salida, x, face.upem


def texto_a_path(ruta, texto, size):
    glifos, avance, upem = shape(ruta, texto)
    tt = TTFont(ruta, fontNumber=0)
    gs = tt.getGlyphSet()
    k = size / upem

    def dibujar(pen):
        for nombre, gx, gy in glifos:
            # escala Y negativa: el SVG crece hacia abajo, la fuente hacia arriba
            gs[nombre].draw(TransformPen(pen, Transform(k, 0, 0, -k, gx * k, -gy * k)))

    trazo = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}")
    dibujar(trazo)
    caja = BoundsPen(gs)
    dibujar(caja)

    return {
        "texto": texto,
        "fuente": os.path.basename(ruta),
        "size": size,
        "avance": round(avance * k, 2),
        "bounds": [round(v, 2) for v in caja.bounds],
        "d": trazo.getCommands(),
    }


def main():
    datos = {}
    for clave, archivo, texto, size in PIEZAS:
        datos[clave] = texto_a_path(os.path.join(FONTS, archivo), texto, size)
        x0, y0, x1, y1 = datos[clave]["bounds"]
        print(f"{clave:10} {texto!r:24} size={size} "
              f"ancho={x1 - x0:.1f} alto={y1 - y0:.1f} d={len(datos[clave]['d'])} chars")

    destino = os.path.join(os.path.dirname(os.path.abspath(__file__)), "textpaths.json")
    with open(destino, "w") as fh:
        json.dump(datos, fh, indent=1)
    print("->", destino)


if __name__ == "__main__":
    main()
