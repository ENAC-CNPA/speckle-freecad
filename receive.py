import FreeCAD as App
import Part

from specklepy.api import operations
from specklepy.api.wrapper import StreamWrapper

if __name__ == "__main__":
    stream_url = "https://app.speckle.systems/projects/6cf358a40e/models/e01ffbc891"
    wrapper = StreamWrapper(stream_url)

    transport = wrapper.get_transport()

    rec = operations.receive("df70892b7556cde3630aa3a1d67377fe", transport)

sBrep = rec

fVertexes = []
for vertex in sBrep.Vertices :
	fVertex = App.Vector(vertex.x, vertex.y, vertex.z)
	fVertexes.append(fVertex)

fEdges = []
for curve3D in sBrep.Curve3D :
	fStart = App.Vector(curve3D.start.x, curve3D.start.y, curve3D.start.z)
	fEnd = App.Vector(curve3D.end.x, curve3D.end.y, curve3D.end.z)
	fLineSegment = Part.LineSegment(fStart, fEnd)
	fEdge = fLineSegment.toShape()
	fEdges.append(fEdge)

fWire = Part.Wire(fEdges)

fFace = Part.Face(fWire)

Part.show(fFace)