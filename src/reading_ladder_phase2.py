# ReadingLadder - Phase 2: hollow the massing into 3/4" panels
# Shell operation: remove the bottom face, leave a 3/4" wall everywhere else.
# Run from FreeCAD Python console:
#   exec(open('/mnt/mars/gitrepos/ReadingLadder/src/reading_ladder_phase2.py').read())

import FreeCAD

MM = 25.4
THICK_IN = 0.75  # panel thickness

doc = FreeCAD.ActiveDocument
body = doc.getObject("Body")
massing = doc.getObject("Massing")

# --- Remove any previous Thickness attempt ---
old = doc.getObject("Panels")
if old:
    doc.removeObject("Panels")
    doc.recompute()

# --- Find the bottom face by geometry: centroid z ~ 0 and normal pointing -Z ---
bottom_name = None
for i, f in enumerate(massing.Shape.Faces):
    c = f.CenterOfMass
    u0, u1, v0, v1 = f.ParameterRange
    n = f.normalAt((u0 + u1) / 2.0, (v0 + v1) / 2.0)
    if abs(c.z) < 0.5 and n.z < -0.9:
        bottom_name = "Face%d" % (i + 1)
        break

if bottom_name is None:
    raise RuntimeError("Could not locate bottom face")

print("Bottom face:", bottom_name)

# --- Thickness (shell) feature ---
thick = body.newObject("PartDesign::Thickness", "Panels")
thick.Base = (massing, [bottom_name])
thick.Value = THICK_IN * MM
thick.Mode = 0          # Skin
thick.Join = 0          # Arc
thick.Reversed = False  # shell inward, preserve outer dims
doc.recompute()

# --- Report ---
if thick.Shape.isValid():
    print("Panels volume (in^3): %.1f" % (thick.Shape.Volume / MM**3))
else:
    print("WARNING: Panels shape is invalid")

# --- Fit view ---
try:
    import FreeCADGui
    FreeCADGui.ActiveDocument.ActiveView.viewIsometric()
    FreeCADGui.ActiveDocument.ActiveView.fitAll()
except Exception as e:
    print("View:", e)

doc.save()
print("Phase 2 complete.")
