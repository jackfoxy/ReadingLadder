# Diagnostic: report document object states
import FreeCAD
doc = FreeCAD.ActiveDocument
for o in doc.Objects:
    state = getattr(o, 'State', None) or getattr(o, 'Shape', None)
    shape_info = ""
    if hasattr(o, 'Shape'):
        try:
            shape_info = " | volume=%.1f" % o.Shape.Volume
        except Exception as e:
            shape_info = " | shape err: " + str(e)
    sk_info = ""
    if hasattr(o, 'GeometryCount'):
        sk_info = " | geom=%d closed=%s" % (o.GeometryCount, getattr(o, 'Closed', '?'))
    print(o.Name, "/", o.Label, "|", o.TypeId, shape_info, sk_info)

# Try to refresh view
try:
    import FreeCADGui
    FreeCADGui.ActiveDocument.ActiveView.viewIsometric()
    FreeCADGui.ActiveDocument.ActiveView.fitAll()
    print("View refreshed.")
except Exception as e:
    print("View error:", e)
