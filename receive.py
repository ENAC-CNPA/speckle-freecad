import FreeCAD as App
import Part

from specklepy.api import operations
from specklepy.api.wrapper import StreamWrapper

if __name__ == "__main__":
    stream_url = "https://app.speckle.systems/projects/6cf358a40e/models/e01ffbc891"
    wrapper = StreamWrapper(stream_url)

    transport = wrapper.get_transport()
	
	#id of Model version:
    received = operations.receive("f10fb97b5f8fd16491477c184002f3db", transport)

allElements = []

def process_item(item):
	if item.speckle_type == "Speckle.Core.Models.Collection":
		for element in item.elements:
			process_item(element)
	else:
		allElements.append(item)
process_item(received)

for element in allElements:
	if element.speckle_type == "Objects.Geometry.Brep":
		
		sBrep = element

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