# ReadingLadder - Phase 5: final checkpoint + exports
# Saves the .FCStd and exports the finished solid to build/ as STEP
# (CAD interchange) and STL (3D printing).
#
# Run from FreeCAD Python console:
#   exec(open('/mnt/mars/gitrepos/freecad-mcp/src/reading_ladder_phase5_export.py').read())

import os
import FreeCAD
import Mesh

MM = 25.4
BUILD = "/mnt/mars/gitrepos/freecad-mcp/build"

doc = FreeCAD.ActiveDocument
tip = doc.getObject("Body").Tip          # final feature (GrabPost)
shape = tip.Shape

# Report final stats
bb = shape.BoundBox
print("Final solid: valid=%s volume_in3=%.1f" % (shape.isValid(), shape.Volume / MM**3))
print("Bounding box (in): X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f" % (
    bb.XMin/MM, bb.XMax/MM, bb.YMin/MM, bb.YMax/MM, bb.ZMin/MM, bb.ZMax/MM))

if not os.path.isdir(BUILD):
    os.makedirs(BUILD)

# --- STEP (interchange) ---
step_path = os.path.join(BUILD, "ReadingLadder.step")
shape.exportStep(step_path)
print("Wrote STEP:", step_path, "(%d bytes)" % os.path.getsize(step_path))

# --- STL (3D printing) ---
stl_path = os.path.join(BUILD, "ReadingLadder.stl")
Mesh.export([tip], stl_path)
print("Wrote STL:", stl_path, "(%d bytes)" % os.path.getsize(stl_path))

# --- Save the .FCStd checkpoint ---
doc.save()
print("Phase 5 complete.")
