#!/usr/bin/env python3
"""Genera una sola vez los PNG del sitio (imagen social y apple-touch-icon).

Requiere macOS (qlmanage para rasterizar el SVG) y Pillow. El resultado se
versiona en src/, así que sólo hay que volver a ejecutarlo si cambia el logo.
"""
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SRC = Path(__file__).resolve().parent
DARK = (28, 28, 30)
ACCENT = (201, 168, 130)
LIGHT = (250, 250, 248)
SERIF = "/System/Library/Fonts/Supplemental/Times New Roman.ttf"
SERIF_IT = "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"
SANS = "/System/Library/Fonts/Supplemental/Arial.ttf"


def logo_mask(size):
    """Rasteriza logo-accent.svg y devuelve su máscara (L) sin el fondo blanco de QuickLook."""
    with tempfile.TemporaryDirectory() as tmp:
        svg = Path(tmp) / "logo.svg"
        svg.write_bytes((SRC / "assets" / "logo-accent.svg").read_bytes())
        subprocess.run(["qlmanage", "-t", "-s", str(size), "-o", tmp, str(svg)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        im = Image.open(Path(tmp) / "logo.svg.png").convert("RGB")
    blue = im.getchannel("B")  # acento B=130 sobre blanco B=255
    return blue.point(lambda v: max(0, min(255, round((255 - v) * 255 / (255 - ACCENT[2])))))


def paste_logo(canvas, box_xy, size):
    mask = logo_mask(size)
    canvas.paste(Image.new("RGB", (size, size), ACCENT), box_xy, mask)


def spaced(draw, xy, text, font, fill, spacing):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + spacing
    return x


def og_image():
    w, h = 1200, 630
    im = Image.new("RGB", (w, h), DARK)
    d = ImageDraw.Draw(im)
    paste_logo(im, (90, 150), 330)
    x = 500
    spaced(d, (x, 175), "ZIROTTI", ImageFont.truetype(SERIF, 84), LIGHT, 12)
    spaced(d, (x + 4, 280), "STRATEGIC ADVISORY", ImageFont.truetype(SANS, 24), ACCENT, 7)
    d.line([(x + 4, 340), (x + 120, 340)], fill=ACCENT, width=2)
    d.text((x, 370), "…libera todo tu potencial.", font=ImageFont.truetype(SERIF_IT, 50), fill=LIGHT)
    spaced(d, (x + 4, 470), "MADRID · ESPAÑA · SANTIAGO · CHILE", ImageFont.truetype(SANS, 20), (156, 156, 158), 4)
    im.save(SRC / "assets" / "og-image.png", optimize=True)


def apple_icon():
    s = 180
    im = Image.new("RGB", (s, s), DARK)
    paste_logo(im, (34, 34), 112)
    im.save(SRC / "root" / "apple-touch-icon.png", optimize=True)


if __name__ == "__main__":
    (SRC / "root").mkdir(exist_ok=True)
    og_image()
    apple_icon()
    print("OK")
