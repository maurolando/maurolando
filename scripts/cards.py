"""Genera las cards de "Fuera del codigo": assets/card-spotify.png y card-steam.png.

Uso:
    python3 scripts/cards.py

Necesita Pillow y el binario `magick` (ImageMagick): el contorno del logo lo
rasteriza magick y la composicion la hace Pillow. No necesita red, los paths
de los iconos van embebidos en ICONS.

Las cards van como PNG y no como HTML porque GitHub sanea el README: no hay
CSS ni background posible, el verde tiene que venir pintado en la imagen.
Son monocromaticas a proposito: el logo se pinta en FG pero con OPACITY, asi
se funde con el fondo en vez de recortarse encima y la card se lee como un
bloque verde entero.

El lienzo es 2x (se muestra a W/2 en el README) para que no se vea borroso en
pantallas densas.

Que tocar:
    BG / FG / OPACITY   color del fondo, color del logo y cuanto se funde
    W, H, RADIUS        tamano del lienzo y radio de las esquinas
    LOGO_H              alto del logo como fraccion de H
"""

import os
import subprocess
import tempfile

from PIL import Image, ImageDraw

BG = "#0b3b2e"      # verde petroleo, el mismo de los badges del stack
FG = "#7be39b"      # menta, el acento del resto del perfil
OPACITY = 0.5       # cuanto del logo se deja ver sobre el fondo

W, H = 860, 580     # 2x: en el README se muestran a 430
RADIUS = 34
LOGO_H = 0.82       # el logo ocupa casi todo el alto: es la mitad de la card
SS = 4              # supersampling del glifo, por el antialiasing de magick

# viewBox 0 0 24 24, tal como los publica simple-icons.
ICONS = {
    "spotify": "M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z",
    "steam": "M11.979 0C5.678 0 .511 4.86.022 11.037l6.432 2.658c.545-.371 1.203-.59 1.912-.59.063 0 .125.004.188.006l2.861-4.142V8.91c0-2.495 2.028-4.524 4.524-4.524 2.494 0 4.524 2.031 4.524 4.527s-2.03 4.525-4.524 4.525h-.105l-4.076 2.911c0 .052.004.105.004.159 0 1.875-1.515 3.396-3.39 3.396-1.635 0-3.016-1.173-3.331-2.727L.436 15.27C1.862 20.307 6.486 24 11.979 24c6.627 0 11.999-5.373 11.999-12S18.605 0 11.979 0zM7.54 18.21l-1.473-.61c.262.543.714.999 1.314 1.25 1.297.539 2.793-.076 3.332-1.375.263-.63.264-1.319.005-1.949s-.75-1.121-1.377-1.383c-.624-.26-1.29-.249-1.878-.03l1.523.63c.956.4 1.409 1.5 1.009 2.455-.397.957-1.497 1.41-2.454 1.012H7.54zm11.415-9.303c0-1.662-1.353-3.015-3.015-3.015-1.665 0-3.015 1.353-3.015 3.015 0 1.665 1.35 3.015 3.015 3.015 1.663 0 3.015-1.35 3.015-3.015zm-5.273-.005c0-1.252 1.013-2.266 2.265-2.266 1.249 0 2.266 1.014 2.266 2.266 0 1.251-1.017 2.265-2.266 2.265-1.253 0-2.265-1.014-2.265-2.265z",
}

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def glyph(path, height):
    """Rasteriza un path de 24x24 a un RGBA de alto height, con transparencia.

    El tamano va en el propio SVG y no en un -resize posterior: magick
    rasteriza al tamano del viewBox (24x24) y escalar despues deja el borde
    lavado. Se pide SS veces el alto final y baja con Pillow, que da un
    antialiasing mas limpio que el de magick.
    """
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
           'viewBox="0 0 24 24"><path d="%s" fill="#000"/></svg>'
           % (height * SS, height * SS, path))
    with tempfile.TemporaryDirectory() as tmp:
        src, out = os.path.join(tmp, "i.svg"), os.path.join(tmp, "i.png")
        with open(src, "w") as fh:
            fh.write(svg)
        subprocess.run(["magick", "-background", "none", src,
                        "PNG32:" + out], check=True)
        big = Image.open(out).convert("RGBA")
    ancho = round(big.width * height / big.height)
    return big.resize((ancho, height), Image.LANCZOS)


def card(name, path):
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(base).rounded_rectangle([0, 0, W - 1, H - 1], RADIUS, fill=BG)

    logo = glyph(path, round(H * LOGO_H))
    # El logo entra como mascara: se pinta plano en FG y es el alfa, atenuado
    # por OPACITY, el que lo mezcla con el fondo.
    tinta = Image.new("RGBA", logo.size, FG)
    tinta.putalpha(logo.getchannel("A").point(lambda a: round(a * OPACITY)))
    base.alpha_composite(tinta, ((W - logo.width) // 2, (H - logo.height) // 2))

    dest = os.path.join(ROOT, "assets", "card-%s.png" % name)
    base.save(dest)
    print("%s  %dx%d" % (dest, W, H))


for nombre, d in ICONS.items():
    card(nombre, d)
