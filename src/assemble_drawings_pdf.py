#!/usr/bin/env python3
"""Assemble the 11 component shop-drawing SVGs into one multi-page PDF.

Renders each SVG to a high-res PNG via headless Firefox (wrapped in an
<img> scaled to 254 dpi so the vector is rasterized full-size, not the
default 96 dpi), then combines the pages with Pillow.

Deps: firefox, Pillow.  Run:  python3 src/assemble_drawings_pdf.py
Output: build/ReadingLadder_drawings.pdf  (A4 landscape, 254 dpi)
"""
import os
import shutil
import subprocess
import tempfile
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SVG_DIR = os.path.join(HERE, "..", "build", "drawings")
OUT_PDF = os.path.join(HERE, "..", "build", "ReadingLadder_drawings.pdf")
SVG_DIR = os.path.abspath(SVG_DIR)
OUT_PDF = os.path.abspath(OUT_PDF)

# A4 landscape at 254 dpi (10 px/mm): 297x210mm -> 2970x2100 px
PX_W, PX_H, DPI = 2970, 2100, 254.0
ID_ORDER = "ABCDEFGHJKL"   # cut-list order (no I)


def ordered_svgs():
    files = [f for f in os.listdir(SVG_DIR) if f.endswith(".svg")]
    files.sort(key=lambda f: ID_ORDER.index(f[0]) if f and f[0] in ID_ORDER else 99)
    return [os.path.join(SVG_DIR, f) for f in files]


def render_png(firefox, svg_path, tmp):
    """Wrap the SVG in an <img> scaled to full page px, screenshot to PNG."""
    base = os.path.splitext(os.path.basename(svg_path))[0]
    html = os.path.join(tmp, base + ".html")
    png = os.path.join(tmp, base + ".png")
    with open(html, "w") as f:
        f.write('<!doctype html><html><head><meta charset="utf-8">'
                '<style>html,body{margin:0;padding:0}'
                'img{display:block;width:%dpx;height:%dpx}</style></head>'
                '<body><img src="file://%s"></body></html>'
                % (PX_W, PX_H, svg_path))
    subprocess.run([firefox, "--headless", "--screenshot", png,
                    "file://" + html, "--window-size=%d,%d" % (PX_W, PX_H)],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                   timeout=90)
    return png if os.path.exists(png) and os.path.getsize(png) > 0 else None


def main():
    firefox = shutil.which("firefox")
    if not firefox:
        raise SystemExit("firefox not found")
    svgs = ordered_svgs()
    print("Assembling %d drawings -> %s" % (len(svgs), OUT_PDF))

    tmp = tempfile.mkdtemp(prefix="rl_pdf_")
    pages = []
    try:
        for svg in svgs:
            png = render_png(firefox, svg, tmp)
            if png:
                pages.append(png)
                print("  rendered", os.path.basename(svg))
            else:
                print("  FAILED  ", os.path.basename(svg))
        if not pages:
            raise SystemExit("no pages rendered")
        imgs = [Image.open(p).convert("RGB") for p in pages]
        imgs[0].save(OUT_PDF, "PDF", resolution=DPI, save_all=True,
                     append_images=imgs[1:])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("Wrote %s (%d pages, %d bytes)"
          % (OUT_PDF, len(pages), os.path.getsize(OUT_PDF)))


if __name__ == "__main__":
    main()
