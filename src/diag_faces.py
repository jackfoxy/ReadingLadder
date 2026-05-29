# Diagnostic: enumerate faces of the Massing solid
# Reports index, area (in^2), centroid (in), and normal direction.
import FreeCAD
doc = FreeCAD.ActiveDocument
MM = 25.4

massing = doc.getObject("Massing")
shape = massing.Shape
print("Solid volume (in^3): %.1f" % (shape.Volume / MM**3))
print("Face count:", len(shape.Faces))
for i, f in enumerate(shape.Faces):
    c = f.CenterOfMass
    # normal at face center (uv midpoint)
    u0, u1, v0, v1 = f.ParameterRange
    n = f.normalAt((u0+u1)/2.0, (v0+v1)/2.0)
    print("Face%d | area=%.1f in^2 | centroid=(%.1f, %.1f, %.1f) in | normal=(%.2f, %.2f, %.2f)" % (
        i+1,
        f.Area / MM**2,
        c.x/MM, c.y/MM, c.z/MM,
        n.x, n.y, n.z,
    ))
