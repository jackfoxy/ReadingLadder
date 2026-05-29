# ReadingLadder - Phase 4: grab post (newel) on the platform
# A 1.5" square vertical post rising 36" from the platform top (z=24 -> z=60),
# at the left front corner of the platform, to hold while reaching high shelves.
#
# Run from FreeCAD Python console:
#   exec(open('/mnt/mars/gitrepos/freecad-mcp/src/reading_ladder_phase4_grabpost.py').read())

import FreeCAD
import Part
import Sketcher

MM = 25.4

doc = FreeCAD.ActiveDocument
body = doc.getObject("Body")

# --- Clean up any previous attempt ---
for name in ["GrabPost", "GrabPostSketch"]:
    if doc.getObject(name):
        doc.removeObject(name)
doc.recompute()

base_vol = body.Shape.Volume / MM**3
print("Volume before grab post (in^3): %.1f" % base_vol)

# --- Sketch on XY plane, offset up to the platform top (z = 24") ---
# Sketch local frame: local-x = global X, local-y = global Y, normal = +Z.
sk = body.newObject("Sketcher::SketchObject", "GrabPostSketch")
sk.AttachmentSupport = [(doc.getObject("XY_Plane"), "")]
sk.MapMode = "FlatFace"
sk.AttachmentOffset = FreeCAD.Placement(
    FreeCAD.Vector(0, 0, 24 * MM), FreeCAD.Rotation()
)
doc.recompute()

# Post footprint in inches: sx = global X, sy = global Y.
# 1.5" square near the platform front edge (x=20) on the left side (y~0).
POST_IN = (20.75, 22.25, -1.75, -0.25)

def add_rect(sketch, x_lo, x_hi, y_lo, y_hi):
    p = [
        FreeCAD.Vector(x_lo * MM, y_lo * MM, 0),
        FreeCAD.Vector(x_hi * MM, y_lo * MM, 0),
        FreeCAD.Vector(x_hi * MM, y_hi * MM, 0),
        FreeCAD.Vector(x_lo * MM, y_hi * MM, 0),
    ]
    base = sketch.GeometryCount
    for i in range(4):
        sketch.addGeometry(Part.LineSegment(p[i], p[(i + 1) % 4]))
    for i in range(4):
        a = base + i
        b = base + (i + 1) % 4
        sketch.addConstraint(Sketcher.Constraint("Coincident", a, 2, b, 1))

add_rect(sk, *POST_IN)
doc.recompute()

# --- Pad the post up 36" (+Z) ---
pad = body.newObject("PartDesign::Pad", "GrabPost")
pad.Profile = sk
pad.Length = 36.0 * MM
pad.Reversed = False         # extrude in +Z (up)
doc.recompute()

def vol_in3(o):
    try:
        return o.Shape.Volume / MM**3
    except Exception:
        return None

v = vol_in3(pad)
# A pad ADDS material; if it didn't grow or is invalid, flip direction.
if (not pad.Shape.isValid()) or (v is None) or (v <= base_vol + 0.1):
    print("First direction looked wrong (valid=%s vol=%s); flipping Reversed." % (
        pad.Shape.isValid(), v))
    pad.Reversed = True
    doc.recompute()
    v = vol_in3(pad)

print("GrabPost valid=%s volume_in3=%s (added %.1f)" % (
    pad.Shape.isValid(), v, (v - base_vol) if v else float('nan')))

try:
    import FreeCADGui
    FreeCADGui.ActiveDocument.ActiveView.viewIsometric()
    FreeCADGui.ActiveDocument.ActiveView.fitAll()
except Exception as e:
    print("View:", e)

doc.save()
print("Phase 4 complete.")
