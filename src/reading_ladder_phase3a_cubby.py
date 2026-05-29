# ReadingLadder - Phase 3a: front book-cubby (3 compartments, 2 shelves)
# Three stacked rectangles pocketed into the front face; the 3/4" gaps
# left between them become the two shelf panels. Lowest compartment
# bottoms out at the floor (z=0).
#
# Run from FreeCAD Python console:
#   exec(open('/mnt/mars/gitrepos/freecad-mcp/src/reading_ladder_phase3a_cubby.py').read())

import FreeCAD
import Part
import Sketcher

MM = 25.4

doc = FreeCAD.ActiveDocument
body = doc.getObject("Body")

# --- Clean up any previous attempt ---
for name in ["BookCubby", "CubbySketch"]:
    if doc.getObject(name):
        doc.removeObject(name)
doc.recompute()

# --- Sketch on YZ plane, offset to the front face at x = 42" ---
# Sketch local frame: local-x = global Y, local-y = global Z, normal = +global X.
sk = body.newObject("Sketcher::SketchObject", "CubbySketch")
sk.AttachmentSupport = [(doc.getObject("YZ_Plane"), "")]
sk.MapMode = "FlatFace"
sk.AttachmentOffset = FreeCAD.Placement(
    FreeCAD.Vector(0, 0, 42 * MM), FreeCAD.Rotation()
)
doc.recompute()

# Compartment rectangles in inches as (sx_lo, sx_hi, sy_lo, sy_hi),
# where sx = global Y (body spans 0..-24), sy = global Z (height).
# Side panels: 3/4" inset each side -> sx in [-23.25, -0.75].
# Shelves 3/4" thick at z=13..13.75 and z=26.5..27.25.
RECTS_IN = [
    (-23.25, -0.75, 0.0,   13.0),    # C1  (floor compartment)
    (-23.25, -0.75, 13.75, 26.5),    # C2
    (-23.25, -0.75, 27.25, 40.0),    # C3
]

def add_rect(sketch, x_lo, x_hi, y_lo, y_hi):
    """Add a closed rectangle (4 lines + coincidence constraints), inches."""
    p = [
        FreeCAD.Vector(x_lo * MM, y_lo * MM, 0),
        FreeCAD.Vector(x_hi * MM, y_lo * MM, 0),
        FreeCAD.Vector(x_hi * MM, y_hi * MM, 0),
        FreeCAD.Vector(x_lo * MM, y_hi * MM, 0),
    ]
    base = sketch.GeometryCount
    for i in range(4):
        sketch.addGeometry(Part.LineSegment(p[i], p[(i + 1) % 4]))
    # close the loop: end of each line coincident with start of the next
    for i in range(4):
        a = base + i
        b = base + (i + 1) % 4
        sketch.addConstraint(Sketcher.Constraint("Coincident", a, 2, b, 1))

for r in RECTS_IN:
    add_rect(sk, *r)

doc.recompute()
print("Cubby sketch geometry count:", sk.GeometryCount)

# --- Pocket the three rectangles into the body ---
pkt = body.newObject("PartDesign::Pocket", "BookCubby")
pkt.Profile = sk
pkt.Length = 10.5 * MM       # book depth
pkt.Reversed = True          # cut in -X (into the body)
doc.recompute()

# Auto-correct direction if the cut went the wrong way / failed.
panels_vol = 3992.0  # in^3, from phase 2
def vol_in3(o):
    try:
        return o.Shape.Volume / MM**3
    except Exception:
        return None

v = vol_in3(pkt)
if (not pkt.Shape.isValid()) or (v is None) or (v >= panels_vol - 1.0):
    print("First direction looked wrong (valid=%s vol=%s); flipping Reversed." % (
        pkt.Shape.isValid(), v))
    pkt.Reversed = False
    doc.recompute()
    v = vol_in3(pkt)

print("BookCubby valid=%s volume_in3=%s" % (pkt.Shape.isValid(), v))

try:
    import FreeCADGui
    FreeCADGui.ActiveDocument.ActiveView.viewIsometric()
    FreeCADGui.ActiveDocument.ActiveView.fitAll()
except Exception as e:
    print("View:", e)

doc.save()
print("Phase 3a complete.")
