# ReadingLadder - TechDraw shop drawings for the component parts.
# One page per (unique) part: to-scale top view + overall dimensions
# (3D vertex refs identified by coordinate) + a notes block. Exports each
# page to build/drawings/<name>.svg. Per-part try/except -> robust + reports.
#
# Requires the parts model. Run reading_ladder_parts.py first, then:
#   exec(open('/mnt/mars/gitrepos/ReadingLadder/src/reading_ladder_drawings.py').read())

import os, glob
import FreeCAD

IN = 25.4
PARTS_DOC = "ReadingLadder_Parts"
OUT = "/mnt/mars/gitrepos/ReadingLadder/build/drawings"

doc = FreeCAD.getDocument(PARTS_DOC)

# Resolve a bundled A4 landscape template dynamically (AppImage path varies).
tmpls = glob.glob(os.path.join(FreeCAD.getResourceDir(), "**",
                  "Default_Template_A4_Landscape.svg"), recursive=True)
TEMPLATE = tmpls[0] if tmpls else None
print("template:", TEMPLATE or "(none - blank pages)")

if not os.path.isdir(OUT):
    os.makedirs(OUT)

# Remove prior drawing objects (pages, views, dims, annos, templates)
for o in list(doc.Objects):
    if o.TypeId.startswith("TechDraw::"):
        doc.removeObject(o.Name)
doc.recompute()

def vname(obj, x_mm, y_mm, z_mm, tol=0.05 * IN):
    """Subelement name 'VertexN' of obj nearest the given point (or None)."""
    P = FreeCAD.Vector(x_mm, y_mm, z_mm)
    best, bd = None, 1e18
    for i, v in enumerate(obj.Shape.Vertexes):
        d = (v.Point - P).Length
        if d < bd:
            bd, best = d, i
    return ("Vertex%d" % (best + 1)) if bd <= tol else None

def add_dim(page, obj, dtype, va, vb, name):
    if not (va and vb):
        return None
    d = doc.addObject("TechDraw::DrawViewDimension", name)
    d.Type = dtype                  # "DistanceX" / "DistanceY"
    d.MeasureType = "True"
    d.References3D = [(obj, va), (obj, vb)]
    page.addView(d)
    return d

# (page_name, [objs to show], notes-lines)
SPECS = [
    ("DWG_A_Side",        ["A_Side_L"],
        ["A - SIDE PANEL  (Qty 2)  3/4\" ply",
         "Cut to side profile (in): (0,0)(0,8)(10,8)(10,16)",
         "  (20,16)(20,24)(30,24)(30,46)(42,42)(42,0)",
         "Overall 42 deep x 46 high. Grain vertical.",
         "LEFT panel only: 18.5w x 14.5h shelf opening,",
         "  10.75 from back, 0.75 up. RIGHT = mirror, no opening."]),
    ("DWG_E_LecternFront",["E_LecternFront"],
        ["E - LECTERN FRONT  (Qty 1)  3/4\" ply",
         "22.5w x 42h. Three cubby openings, 21 wide",
         "(3/4 frame each side):",
         "  C1 z 0-13, C2 z 13.75-26.5, C3 z 27.25-40."]),
    ("DWG_D_LecternBack", ["D_LecternBack"],
        ["D - LECTERN BACK WALL  (Qty 1)  3/4\" ply", "22.5w x 22h. Sits x=30, z 24-46."]),
    ("DWG_F_ReadingSurf", ["F_ReadingSurface"],
        ["F - READING SURFACE  (Qty 1)  3/4\" ply",
         "22.5w x 12-5/8. Bevel both long edges ~18.4 deg."]),
    ("DWG_B_Tread",       ["B_Tread_1"],
        ["B - STEP TREAD  (Qty 3)  3/4\" ply", "22.5w x 10 deep. Treads at z 8/16/24."]),
    ("DWG_C_Riser",       ["C_Riser_1"],
        ["C - RISER  (Qty 3)  3/4\" ply", "22.5w x 8 high. Risers at x 0/10/20."]),
    ("DWG_G_CubbyShelf",  ["G_CubbyShelf_1"],
        ["G - CUBBY SHELF  (Qty 2)  3/4\" ply", "22.5w x 10.5 deep. At z 13 and 26.5."]),
    ("DWG_H_CubbyBack",   ["H_CubbyBack"],
        ["H - CUBBY BACK (optional)  (Qty 1)  3/4\" ply", "22.5w x 40h. At x=31.5."]),
    ("DWG_J_Bottom",      ["J_Bottom"],
        ["J - BOTTOM PANEL (optional)  (Qty 1)  3/4\" ply", "22.5w x 42 deep."]),
    ("DWG_K_GrabPost",    ["K_GrabPost"],
        ["K - GRAB POST  (Qty 1)  lumber", "1.5 x 1.5 (2x2) x 36 long. Platform left-front."]),
    ("DWG_L_FrontLip",    ["L_FrontLip"],
        ["L - FRONT LIP  (Qty 1)  lumber", "3/4 x 1.5 x 22.5. Book stop on reading surface."]),
]

report = []
for page_name, part_names, notes in SPECS:
    try:
        parts = [doc.getObject(n) for n in part_names]
        page = doc.addObject("TechDraw::DrawPage", page_name)
        if TEMPLATE:
            tpl = doc.addObject("TechDraw::DrawSVGTemplate", page_name + "_Tpl")
            tpl.Template = TEMPLATE
            page.Template = tpl
        page.KeepUpdated = True

        view = doc.addObject("TechDraw::DrawViewPart", page_name + "_V")
        view.Source = parts
        view.Direction = FreeCAD.Vector(0, 0, 1)   # top view -> XY face
        view.ScaleType = "Automatic"
        page.addView(view)
        doc.recompute()

        # Overall dimensions from the (first) part's bounding box corners.
        obj = parts[0]
        bb = obj.Shape.BoundBox
        dimcount = 0
        dx = add_dim(page, obj, "DistanceX",
                     vname(obj, bb.XMin, bb.YMin, bb.ZMin),
                     vname(obj, bb.XMax, bb.YMin, bb.ZMin), page_name + "_DX")
        dy = add_dim(page, obj, "DistanceY",
                     vname(obj, bb.XMin, bb.YMin, bb.ZMin),
                     vname(obj, bb.XMin, bb.YMax, bb.ZMin), page_name + "_DY")
        dimcount = sum(1 for d in (dx, dy) if d)

        anno = doc.addObject("TechDraw::DrawViewAnnotation", page_name + "_Notes")
        anno.Text = notes
        anno.TextSize = 3.0
        page.addView(anno)
        anno.X = 60.0
        anno.Y = 25.0
        doc.recompute()

        # Export SVG
        svg = os.path.join(OUT, page_name + ".svg")
        try:
            import TechDrawGui
            TechDrawGui.exportPageAsSvg(page, svg)
            sz = os.path.getsize(svg)
        except Exception as ee:
            sz = -1
            report.append("  (svg export failed: %s)" % ee)
        report.append("OK  %-20s dims=%d svg=%s bytes" % (page_name, dimcount, sz))
    except Exception as e:
        report.append("FAIL %-20s %s" % (page_name, e))

doc.recompute()
doc.save()
print("\n".join(report))
print("Drawings pass complete.")
