import FreeCAD as App
import Part

from specklepy.api import operations
from specklepy.api.wrapper import StreamWrapper

if __name__ == "__main__":
    stream_url = "https://app.speckle.systems/projects/6cf358a40e/models/e01ffbc891"
    wrapper = StreamWrapper(stream_url)

    transport = wrapper.get_transport()

    rec = operations.receive("6c99bc17d0d10833f3c01855c37174fc", transport)

sBrep = rec

sCurve3D = sBrep.Curve3D
fEdges = []
for curve in sCurve3D :
	sStart = curve.start
	sEnd = curve.end
	fStart = App.Vector(sStart.x, sStart.y, sStart.z)
	fEnd = App.Vector(sEnd.x, sEnd.y, sEnd.z)
	fLineSegment = Part.LineSegment(fStart, fEnd)
	fEdge = fLineSegment.toShape()
	fEdges.append(fEdge)

sLoops = sBrep.Loops
sTrims = sBrep.Trims

fFaces = []
for face in sBrep.Faces :
	sOuterLoopIndex = face.OuterLoopIndex
	sOuterLoop = sLoops[sOuterLoopIndex]
	sTrimIndices = sOuterLoop.TrimIndices
	sOwnTrims = [sTrims[i] for i in sTrimIndices]
	fOwnEdges = []
	for trim in sOwnTrims :
		sEdgeIndex = trim.EdgeIndex
		fOwnEdges.append(fEdges[sEdgeIndex])
	fWire = Part.Wire(fOwnEdges)
	fFace = Part.Face(fWire)
	fFaces.append(fFace)

fShell = Part.Shell(fFaces)

Part.show(fShell)