#!/usr/bin/env python3
"""Generate dimensioned shop-drawing SVGs for ReadingLadder components.

Pure Python (no FreeCAD) -> deterministic, printable A4 pages with the part
outline to scale, overall + feature dimensions, a titleblock, and notes.
Nominal spec, inches. Output: build/drawings/<ID>.svg

Run:  python3 src/gen_drawings_svg.py
"""
import os

OUT = os.path.join(os.path.dirname(__file__), "..", "build", "drawings")
OUT = os.path.abspath(OUT)

# A4 landscape, mm. Drawing window sits above the titleblock.
PAGE_W, PAGE_H = 297.0, 210.0
MARGIN = 8.0
TB_H = 34.0                       # titleblock height
AREA = (MARGIN, MARGIN, PAGE_W - MARGIN, PAGE_H - MARGIN - TB_H)  # x0,y0,x1,y1


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fmt(v):
    """Tidy inch label: 42 -> 42", 12.649 -> 12.65"."""
    return ("%.2f" % v).rstrip("0").rstrip(".") + '"'


class Drawing:
    """SVG builder in page mm coords (y-down). Model->page mapping set per part."""

    def __init__(self):
        self.body = []
        self.sx = self.sy = 1.0
        self.ox = self.oy = 0.0
        self.ymax_in = 0.0

    # ----- model(inch) -> page(mm) -----
    def fit(self, w_in, h_in):
        aw = (AREA[2] - AREA[0])
        ah = (AREA[3] - AREA[1])
        # leave room for dimension lines/labels around the part
        pad = 22.0
        s = min((aw - 2 * pad) / w_in, (ah - 2 * pad) / h_in)
        self.scale = s
        # center the part in the area
        cx = (AREA[0] + AREA[2]) / 2.0
        cy = (AREA[1] + AREA[3]) / 2.0
        self.ox = cx - (w_in * s) / 2.0
        self.oy = cy + (h_in * s) / 2.0   # page y grows down; model y grows up
        return s

    def pt(self, x_in, y_in):
        return (self.ox + x_in * self.scale, self.oy - y_in * self.scale)

    # ----- primitives -----
    def line(self, p1, p2, w=0.3, color="#222", dash=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        self.body.append(
            '<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" '
            'stroke-width="%.2f"%s/>' % (p1[0], p1[1], p2[0], p2[1], color, w, d))

    def poly(self, pts_in, w=0.6, color="#111", fill="none"):
        d = " ".join("%.2f,%.2f" % self.pt(x, y) for x, y in pts_in)
        self.body.append('<polygon points="%s" fill="%s" stroke="%s" '
                         'stroke-width="%.2f"/>' % (d, fill, color, w))

    def text(self, x, y, s, size=3.2, anchor="middle", color="#111", bold=False):
        b = ' font-weight="bold"' if bold else ""
        self.body.append(
            '<text x="%.2f" y="%.2f" font-family="sans-serif" font-size="%.2f" '
            'text-anchor="%s" fill="%s"%s>%s</text>'
            % (x, y, size, anchor, color, b, esc(s)))

    # ----- dimensions (model inches) -----
    def _tick(self, p, ang_deg=45, ln=1.4):
        import math
        a = math.radians(ang_deg)
        dx, dy = ln * math.cos(a), ln * math.sin(a)
        self.line((p[0] - dx, p[1] - dy), (p[0] + dx, p[1] + dy), w=0.4)

    def dim_h(self, x1_in, x2_in, y_in, label, off_mm=12.0, below=True):
        """Horizontal dimension between two x's at model y_in."""
        sgn = 1 if below else -1
        a = self.pt(x1_in, y_in); b = self.pt(x2_in, y_in)
        yl = (a[1] if below else a[1]) + sgn * off_mm
        pa = (a[0], yl); pb = (b[0], yl)
        # extension lines
        self.line(a, (a[0], yl + sgn * 1.5), w=0.25, color="#888")
        self.line(b, (b[0], yl + sgn * 1.5), w=0.25, color="#888")
        self.line(pa, pb, w=0.35)
        self._tick(pa); self._tick(pb)
        self.text((pa[0] + pb[0]) / 2.0, yl - 1.2 if below else yl - 1.2, label, size=3.2)

    def dim_v(self, y1_in, y2_in, x_in, label, off_mm=12.0, left=True):
        sgn = -1 if left else 1
        a = self.pt(x_in, y1_in); b = self.pt(x_in, y2_in)
        xl = a[0] + sgn * off_mm
        pa = (xl, a[1]); pb = (xl, b[1])
        self.line(a, (xl + sgn * 1.5, a[1]), w=0.25, color="#888")
        self.line(b, (xl + sgn * 1.5, b[1]), w=0.25, color="#888")
        self.line(pa, pb, w=0.35)
        self._tick(pa); self._tick(pb)
        # rotated label
        my = (pa[1] + pb[1]) / 2.0
        self.body.append(
            '<text x="%.2f" y="%.2f" font-family="sans-serif" font-size="3.2" '
            'text-anchor="middle" fill="#111" transform="rotate(-90 %.2f %.2f)">%s</text>'
            % (xl - 1.4, my, xl - 1.4, my, esc(label)))

    # ----- page assembly -----
    def titleblock(self, pid, name, material, qty, notes):
        x0, y0 = MARGIN, PAGE_H - MARGIN - TB_H
        x1, y1 = PAGE_W - MARGIN, PAGE_H - MARGIN
        self.body.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" '
                         'fill="none" stroke="#111" stroke-width="0.5"/>'
                         % (x0, y0, x1 - x0, y1 - y0))
        self.line((x0, y0 + 9), (x1, y0 + 9), w=0.3)
        self.text(x0 + 3, y0 + 6.5, "ReadingLadder  —  component shop drawing",
                  size=4.0, anchor="start", bold=True)
        self.text(x1 - 3, y0 + 6.5, "Scale 1:%.0f   inches" % round(1 / (self.scale / 25.4)),
                  size=3.0, anchor="end")
        self.text(x0 + 3, y0 + 15, "%s  %s" % (pid, name), size=3.6, anchor="start", bold=True)
        self.text(x0 + 3, y0 + 21, "Material: %s     Qty: %s" % (material, qty),
                  size=3.0, anchor="start")
        ny = y0 + 27
        for ln in notes:
            self.text(x0 + 3, ny, ln, size=2.7, anchor="start", color="#333")
            ny += 3.4

    def svg(self):
        head = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<svg xmlns="http://www.w3.org/2000/svg" width="%gmm" height="%gmm" '
                'viewBox="0 0 %g %g">\n' % (PAGE_W, PAGE_H, PAGE_W, PAGE_H))
        border = ('<rect x="3" y="3" width="%g" height="%g" fill="white" '
                  'stroke="#111" stroke-width="0.6"/>\n' % (PAGE_W - 6, PAGE_H - 6))
        return head + border + "\n".join(self.body) + "\n</svg>\n"


def rect_pts(w, h):
    return [(0, 0), (w, 0), (w, h), (0, h)]


def render_rect(pid, name, material, qty, w, h, notes, extra=None, draw_box=True):
    d = Drawing()
    d.fit(w, h)
    if draw_box:
        d.poly(rect_pts(w, h))
        d.dim_h(0, w, 0, fmt(w))
        d.dim_v(0, h, 0, fmt(h))
    if extra:
        extra(d)
    d.titleblock(pid, name, material, qty, notes)
    return d.svg()


# ---- per-part feature overlays ----
def side_extra(d):
    prof = [(0,0),(0,8),(10,8),(10,16),(20,16),(20,24),(30,24),(30,46),(42,42),(42,0)]
    d.poly(prof)
    # left-panel shelf cutout
    cut = [(10.75,0.75),(29.25,0.75),(29.25,15.25),(10.75,15.25)]
    d.poly(cut, w=0.5, color="#b00")
    d.dim_h(0, 42, 0, '42"')              # overall depth (bottom)
    d.dim_v(0, 46, 0, '46"')              # overall height (left)
    d.dim_h(10.75, 29.25, 0.75, '18.5"', off_mm=6, below=False)
    d.dim_v(0.75, 15.25, 10.75, '14.5"', off_mm=6, left=False)


def lectern_front_extra(d):
    bands = [(0.0,13.0),(13.75,26.5),(27.25,40.0)]
    for z0, z1 in bands:
        d.poly([(0.75,z0),(21.75,z0),(21.75,z1),(0.75,z1)], w=0.5, color="#b00")
    d.dim_h(0.75, 21.75, 0.75, '21"', off_mm=6, below=False)
    # opening band heights as a chain on the right
    d.dim_v(0, 13, 22.5, '13"', off_mm=8, left=False)
    d.dim_v(13.75, 26.5, 22.5, '12.75"', off_mm=8, left=False)
    d.dim_v(27.25, 40, 22.5, '12.75"', off_mm=8, left=False)


PARTS = [
    # pid, name, material, qty, w, h, notes, extra
    ("A", "Side panel (profile)", '3/4" ply', "2", 42, 46,
     ["Cut to side profile. Coords (in): (0,0)(0,8)(10,8)(10,16)",
      "(20,16)(20,24)(30,24)(30,46)(42,42)(42,0).",
      "LEFT panel: 18.5x14.5 shelf opening (red), 10.75 from",
      "back, 0.75 up. RIGHT panel = mirror, NO opening."],
     side_extra),
    ("E", "Lectern front", '3/4" ply', "1", 22.5, 42,
     ["Three cubby openings (red), 21 wide (3/4 frame each side).",
      "Bands z: 0-13, 13.75-26.5, 27.25-40."],
     lectern_front_extra),
    ("D", "Lectern back wall", '3/4" ply', "1", 22.5, 22,
     ["Vertical at x=30, z 24-46. Butt to sides + platform."], None),
    ("F", "Reading surface", '3/4" ply', "1", 22.5, 12.649,
     ["Sloped top ~18.4 deg. Bevel both long (22.5) edges to",
      "seat on lectern-back top and meet the front lip."], None),
    ("B", "Step tread", '3/4" ply', "3", 22.5, 10,
     ["Horizontal. Treads at z = 8, 16, 24 (top = platform)."], None),
    ("C", "Riser", '3/4" ply', "3", 22.5, 8,
     ["Vertical. Risers at x = 0, 10, 20."], None),
    ("G", "Cubby shelf", '3/4" ply', "2", 22.5, 10.5,
     ["Horizontal dividers in cubby, at z = 13 and 26.5."], None),
    ("H", "Cubby back (optional)", '3/4" ply', "1", 22.5, 40,
     ["Vertical at x=31.5; boxes cubby off from carcass."], None),
    ("J", "Bottom panel (optional)", '3/4" ply', "1", 22.5, 42,
     ["Closes the underside."], None),
    ("K", "Grab post", "lumber 2x2", "1", 36, 1.5,
     ["1.5 x 1.5 (2x2) x 36 long. Platform left-front, z 24-60."], None),
    ("L", "Front lip", "lumber", "1", 22.5, 1.5,
     ["3/4 x 1.5 x 22.5. Book stop on reading surface."], None),
]


def main():
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    written = []
    for pid, name, mat, qty, w, h, notes, extra in PARTS:
        # Part A's true outline is the profile (drawn by its extra), not a box.
        svg = render_rect(pid, name, mat, qty, w, h, notes, extra,
                          draw_box=(pid != "A"))
        path = os.path.join(OUT, "%s_%s.svg" % (pid, name.split()[0].replace("/", "")))
        with open(path, "w") as f:
            f.write(svg)
        written.append(os.path.basename(path))
    print("Wrote %d drawings to %s:" % (len(written), OUT))
    for n in written:
        print("  ", n)


if __name__ == "__main__":
    main()
