# ReadingLadder - Phase 3c: side-loading shelf under steps 2 & 3
# Opens the LEFT side panel (y=0) over the under-step-2 footprint to make one
# side-access book compartment. Simple rectangle up to the lower ceiling
# (underside of the step-2 tread, z~15.25"). Pocketed ~23.25" in, leaving a
# 3/4" back wall on the far (y=-24) side.
#
# Run from FreeCAD Python console:
#   exec(open('/mnt/mars/gitrepos/ReadingLadder/src/reading_ladder_phase3c_sideshelf.py').read())

import FreeCAD
import Part
import Sketcher

MM = 25.4

doc = FreeCAD.ActiveDocument
body = doc.getObject("Body")

# --- Clean up any previous attempt ---
for name in ["SideShelf", "SideShelfSketch"]:
    if doc.getObject(name):
        doc.removeObject(name)
doc.recompute()

# Volume before this feature (auto-correct pocket direction against it)
base_vol = body.Shape.Volume / MM**3
print("Volume before side shelf (in^3): %.1f" % base_vol)

# --- Sketch on XZ plane (already at y=0, the left side face) ---
# Sketch local frame: local-x = global X, local-y = global Z, normal = +/-Y.
sk = body.newObject("Sketcher::SketchObject", "SideShelfSketch")
sk.AttachmentSupport = [(doc.getObject("XZ_Plane"), "")]
sk.MapMode = "FlatFace"
doc.recompute()

# Opening rectangle in inches: sx = global X, sy = global Z.
# x inset 3/4" off the risers at x=10 and x=30; z from a 3/4" base up to the
# underside of the step-2 tread (16 - 0.75 = 15.25).
RECT_IN = (10.75, 29.25, 0.75, 15.25)

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

add_rect(sk, *RECT_IN)
doc.recompute()

# --- Pocket ~23.25" into the body, leaving a 3/4" far wall ---
pkt = body.newObject("PartDesign::Pocket", "SideShelf")
pkt.Profile = sk
pkt.Length = 23.25 * MM
pkt.Reversed = True          # cut in -Y (into the body)
doc.recompute()

def vol_in3(o):
    try:
        return o.Shape.Volume / MM**3
    except Exception:
        return None

v = vol_in3(pkt)
# A real cut reduces volume; if it grew / is invalid, flip direction.
if (not pkt.Shape.isValid()) or (v is None) or (v >= base_vol - 1.0):
    print("First direction looked wrong (valid=%s vol=%s); flipping Reversed." % (
        pkt.Shape.isValid(), v))
    pkt.Reversed = False
    doc.recompute()
    v = vol_in3(pkt)

print("SideShelf valid=%s volume_in3=%s (removed %.1f)" % (
    pkt.Shape.isValid(), v, (base_vol - v) if v else float('nan')))

try:
    import FreeCADGui
    FreeCADGui.ActiveDocument.ActiveView.viewIsometric()
    FreeCADGui.ActiveDocument.ActiveView.fitAll()
except Exception as e:
    print("View:", e)

doc.save()
print("Phase 3c complete.")
