"""Convierte la tipografia de la terminal a paths SVG y los deja en glyphs.json.

Solo hay que correrlo si cambia la tipografia, su tamano o hace falta un
caracter que no este en CHARS. banner.py lee el JSON y no necesita estas
dependencias.

    python3 -m venv venv && ./venv/bin/pip install fonttools
    ./venv/bin/python scripts/fontpaths.py

Los .ttf no estan en el repo (ver .gitignore). Para regenerar hay que bajar
JetBrains Mono (licencia OFL) y dejar Regular y Bold en assets/fonts/:

    https://github.com/JetBrains/JetBrainsMono/releases

El header ya renderiza sin ellos: los contornos viajan dentro del SVG.

GitHub sanea los SVG: un font-family externo hace fallback y un @font-face
remoto lo bloquea. Por eso el texto va como contorno, no como <text>; con la
fuente del sistema el arte ASCII se desalinearia.
"""
import json
import os

from fontTools.misc.transform import Transform
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "assets", "fonts")

SIZE = 20
PESOS = {"regular": "JetBrainsMono-Regular.ttf", "bold": "JetBrainsMono-Bold.ttf"}
CHARS = "".join(chr(c) for c in range(33, 127)) + "áéíóúüñÁÉÍÓÚÜÑ¿¡·"


def glifos(ruta):
    """Devuelve {caracter: d} a SIZE px, con la linea base en y=0, y el avance."""
    tt = TTFont(ruta)
    gs, cmap = tt.getGlyphSet(), tt.getBestCmap()
    k = SIZE / tt["head"].unitsPerEm
    salida = {}
    for ch in CHARS:
        pen = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
        # escala Y negativa: el SVG crece hacia abajo, la fuente hacia arriba
        gs[cmap[ord(ch)]].draw(TransformPen(pen, Transform(k, 0, 0, -k, 0, 0)))
        salida[ch] = pen.getCommands()
    return salida, round(tt["hmtx"][cmap[ord("M")]][0] * k, 3)


def main():
    datos = {"fuente": "JetBrains Mono", "size": SIZE}
    for peso, archivo in PESOS.items():
        datos[peso], datos["avance"] = glifos(os.path.join(FONTS, archivo))
        print(f"{peso:8} {archivo:28} glifos={len(datos[peso])} avance={datos['avance']}")

    destino = os.path.join(os.path.dirname(os.path.abspath(__file__)), "glyphs.json")
    with open(destino, "w") as fh:
        json.dump(datos, fh, indent=1, ensure_ascii=False)
    print("->", destino)


if __name__ == "__main__":
    main()
