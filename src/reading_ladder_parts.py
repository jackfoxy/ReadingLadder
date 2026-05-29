# ReadingLadder - Component parts model (for cut list + TechDraw drawings)
# Builds every component as its own flat 3/4" solid in a NEW document,
# laid out in a grid (each part's big face in the XY plane so a top view
# gives a clean panel outline). Nominal spec dimensions; butt joints.
#
# Run from FreeCAD Python console:
#   exec(open('/mnt/mars/gitrepos/ReadingLadder/src/reading_ladder_parts.py').read())

import FreeCAD
import Part

IN = 25.4
T = 0.75 * IN            # panel / sheet thickness
DOCNAME = "ReadingLadder_Parts"
CELL = 60 * IN           # grid cell size
COLS = 4

# Fresh document
if DOCNAME in [d.Name for d in FreeCAD.listDocuments().values()]:
    FreeCAD.closeDocument(DOCNAME)
doc = FreeCAD.newDocument(DOCNAME)

_parts = []  # collect (label, shape) then place into grid

def panel(w_in, h_in, thick=T):
    """Flat rectangular panel: w along X, h along Y, thickness up Z."""
    return Part.makeBox(w_in * IN, h_in * IN, thick)

def side_profile(left=False):
    """The 10-point side profile, extruded T; optional shelf cutout (left)."""
    pts = [(0,0),(0,8),(10,8),(10,16),(20,16),(20,24),(30,24),(30,46),(42,42),(42,0)]
    v = [FreeCAD.Vector(px*IN, pz*IN, 0) for px, pz in pts]
    v.append(v[0])
    sol = Part.Face(Part.makePolygon(v)).extrude(FreeCAD.Vector(0, 0, T))
    if left:
        # side-shelf opening: x 10.75..29.25, z(height) 0.75..15.25
        cut = Part.makeBox((29.25-10.75)*IN, (15.25-0.75)*IN, T+2,
                           FreeCAD.Vector(10.75*IN, 0.75*IN, -1))
        sol = sol.cut(cut)
    return sol

def lectern_front():
    """22.5 x 42 panel with three cubby openings (21 wide)."""
    sol = panel(22.5, 42)
    bands = [(0.0, 13.0), (13.75, 26.5), (27.25, 40.0)]  # (z_lo, z_hi)
    for z0, z1 in bands:
        hole = Part.makeBox(21*IN, (z1-z0)*IN, T+2,
                            FreeCAD.Vector(0.75*IN, z0*IN, -1))
        sol = sol.cut(hole)
    return sol

# --- Assemble the parts list (label, shape) ---
_parts.append(("A_Side_L", side_profile(left=True)))
_parts.append(("A_Side_R", side_profile(left=False)))
_parts.append(("E_LecternFront", lectern_front()))
_parts.append(("J_Bottom", panel(22.5, 42)))
_parts.append(("H_CubbyBack", panel(22.5, 40)))
_parts.append(("D_LecternBack", panel(22.5, 22)))
_parts.append(("F_ReadingSurface", panel(22.5, 12.649)))
for i in (1, 2, 3):
    _parts.append(("B_Tread_%d" % i, panel(22.5, 10)))
for i in (1, 2, 3):
    _parts.append(("C_Riser_%d" % i, panel(22.5, 8)))
for i in (1, 2):
    _parts.append(("G_CubbyShelf_%d" % i, panel(22.5, 10.5)))
# Lumber sticks, laid flat (length along X)
_parts.append(("K_GrabPost", Part.makeBox(36*IN, 1.5*IN, 1.5*IN)))
_parts.append(("L_FrontLip", Part.makeBox(22.5*IN, 1.5*IN, 0.75*IN)))

# --- Place into a grid, add to doc ---
created = []
for idx, (label, shape) in enumerate(_parts):
    col = idx % COLS
    row = idx // COLS
    shape.translate(FreeCAD.Vector(col * CELL, -row * CELL, 0))
    o = doc.addObject("Part::Feature", label)
    o.Shape = shape
    o.Label = label
    created.append(o)

doc.recompute()

# --- Report ---
bad = [o.Label for o in created if not o.Shape.isValid()]
print("Created %d parts. Invalid: %s" % (len(created), bad or "none"))
for o in created:
    bb = o.Shape.BoundBox
    print("  %-18s %.2f x %.2f x %.2f in" % (
        o.Label, bb.XLength/IN, bb.YLength/IN, bb.ZLength/IN))

try:
    import FreeCADGui
    FreeCADGui.ActiveDocument.ActiveView.viewTop()
    FreeCADGui.ActiveDocument.ActiveView.fitAll()
except Exception as e:
    print("View:", e)

doc.saveAs('/mnt/mars/gitrepos/ReadingLadder/models/ReadingLadder_Parts.FCStd')
print("Parts model complete.")
