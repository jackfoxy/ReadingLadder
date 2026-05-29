# ReadingLadder - Phase 1: side-profile massing block
# Run from FreeCAD Python console:
#   exec(open('/mnt/mars/gitrepos/freecad-mcp/src/reading_ladder_phase1.py').read())

import FreeCAD
import Part

MM = 25.4  # 1 inch in mm

doc = FreeCAD.ActiveDocument

# --- Remove any previous attempts ---
for name in ["Massing002","SideProfile002","Massing001","SideProfile001","Massing","SideProfile"]:
    obj = doc.getObject(name)
    if obj:
        doc.removeObject(name)
doc.recompute()

# --- Body ---
body = doc.getObject("Body")
body.Label = "ReadingLadder"

# --- Sketch on XZ plane ---
# Sketch local frame: local-X = world-X, local-Y = world-Z
# So points are FreeCAD.Vector(world_x, world_z, 0)
sk = body.newObject("Sketcher::SketchObject", "SideProfile")
sk.AttachmentSupport = [(doc.getObject("XZ_Plane"), "")]
sk.MapMode = "FlatFace"
doc.recompute()

# Side-profile polygon in inches: (depth_x, height_z)
PROFILE_IN = [
    (0,  0),
    (0,  8),
    (10, 8),
    (10, 16),
    (20, 16),
    (20, 24),
    (30, 24),
    (30, 46),
    (42, 42),
    (42, 0),
]

pts = [(x * MM, z * MM) for x, z in PROFILE_IN]
n = len(pts)
for i in range(n):
    x1, z1 = pts[i]
    x2, z2 = pts[(i + 1) % n]
    sk.addGeometry(Part.LineSegment(
        FreeCAD.Vector(x1, z1, 0),
        FreeCAD.Vector(x2, z2, 0),
    ))

doc.recompute()

# --- Pad 24" wide in +Y direction ---
pad = body.newObject("PartDesign::Pad", "Massing")
pad.Profile = sk
pad.Length = 24.0 * MM
doc.recompute()

# --- Fit view ---
try:
    import FreeCADGui
    FreeCADGui.ActiveDocument.ActiveView.viewIsometric()
    FreeCADGui.ActiveDocument.ActiveView.fitAll()
except Exception as e:
    print("View:", e)

doc.saveAs('/mnt/mars/gitrepos/freecad-mcp/models/ReadingLadder.FCStd')
print("ReadingLadder phase 1 complete.")
