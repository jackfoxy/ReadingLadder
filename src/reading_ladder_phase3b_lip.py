# ReadingLadder - Phase 3b: front lip on the reading surface
# A raised rail along the front-top edge (the low end of the sloped reading
# surface) so a book set on the slope doesn't slide off. Full 24" width,
# 3/4" deep, standing ~1.5" proud of the front edge.
#
# Run from FreeCAD Python console:
#   exec(open('/mnt/mars/gitrepos/freecad-mcp/src/reading_ladder_phase3b_lip.py').read())

import FreeCAD
import Part
import Sketcher

MM = 25.4

doc = FreeCAD.ActiveDocument
body = doc.getObject("Body")

# --- Clean up any previous attempt ---
for name in ["FrontLip", "LipSketch"]:
    if doc.getObject(name):
        doc.removeObject(name)
doc.recompute()

# Volume before this feature (auto-correct pad direction against it)
base_vol = body.Shape.Volume / MM**3
print("Volume before lip (in^3): %.1f" % base_vol)

# --- Sketch on YZ plane offset to the front face (x = 42") ---
sk = body.newObject("Sketcher::SketchObject", "LipSketch")
sk.AttachmentSupport = [(doc.getObject("YZ_Plane"), "")]
sk.MapMode = "FlatFace"
sk.AttachmentOffset = FreeCAD.Placement(
    FreeCAD.Vector(0, 0, 42 * MM), FreeCAD.Rotation()
)
doc.recompute()

# Lip rectangle: sx = global Y (full width 0..-24), sy = global Z (42..43.5).
LIP_IN = (-24.0, 0.0, 42.0, 43.5)

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

add_rect(sk, *LIP_IN)
doc.recompute()

# --- Pad the lip 3/4" into the body (-X) ---
pad = body.newObject("PartDesign::Pad", "FrontLip")
pad.Profile = sk
pad.Length = 0.75 * MM
pad.Reversed = True          # extrude in -X (toward the body)
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
    pad.Reversed = False
    doc.recompute()
    v = vol_in3(pad)

print("FrontLip valid=%s volume_in3=%s (added %.1f)" % (
    pad.Shape.isValid(), v, (v - base_vol) if v else float('nan')))

try:
    import FreeCADGui
    FreeCADGui.ActiveDocument.ActiveView.viewIsometric()
    FreeCADGui.ActiveDocument.ActiveView.fitAll()
except Exception as e:
    print("View:", e)

doc.save()
print("Phase 3b complete.")
