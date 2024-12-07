import FreeCAD as App
import Part

from specklepy.api import operations
from specklepy.api.wrapper import StreamWrapper

if __name__ == "__main__":
    stream_url = "https://app.speckle.systems/projects/6cf358a40e/models/e01ffbc891"
    wrapper = StreamWrapper(stream_url)

    transport = wrapper.get_transport()
	
	#id of main collection:
    received = operations.receive("8ad53f69de6abf1bf81ab343f0361f51", transport)

allElements = []

def process_item(item):
	if item.speckle_type == "Speckle.Core.Models.Collection":
		for element in item.elements:
			process_item(element)
	else:
		allElements.append(item)
process_item(received)

def toFreecadArc(item):
	sStartPoint = item.startPoint
	sMidPoint = item.midPoint
	sEndPoint = item.endPoint
	fStartPoint = App.Vector(sStartPoint.x, sStartPoint.y, sStartPoint.z)
	fMidPoint = App.Vector(sMidPoint.x, sMidPoint.y, sMidPoint.z)
	fEndPoint = App.Vector(sEndPoint.x, sEndPoint.y, sEndPoint.z)
	fArc = Part.Arc(fStartPoint, fMidPoint, fEndPoint)
	fArcShape = fArc.toShape()
	return fArcShape

for element in allElements:
	
	if element.speckle_type == "Objects.Geometry.Circle":
		sRadius = element.radius
		sPlane = element.plane
		sOrigin = sPlane.origin
		sNormal = sPlane.normal
		fPosition = App.Vector(sOrigin.x, sOrigin.y, sOrigin.z)
		fAxis = App.Vector(sNormal.x, sNormal.y, sNormal.z)
		fRadius = sRadius
		fCircle = Part.Circle(fPosition, fAxis, fRadius)
		fCircleShape = fCircle.toShape()
		Part.show(fCircleShape)
		
	elif element.speckle_type == "Objects.Geometry.Arc":
		fArcShape = toFreecadArc(element)
		Part.show(fArcShape)
		
	elif element.speckle_type == "Objects.Geometry.Brep":
		
		sBrep = element

		sCurve3D = sBrep.Curve3D
		fEdges = []
		for curve in sCurve3D :
			if curve.speckle_type == "Objects.Geometry.Line":
				sStart = curve.start
				sEnd = curve.end
				fStart = App.Vector(sStart.x, sStart.y, sStart.z)
				fEnd = App.Vector(sEnd.x, sEnd.y, sEnd.z)
				fLineSegment = Part.LineSegment(fStart, fEnd)
				fEdge = fLineSegment.toShape()
				fEdges.append(fEdge)
			elif curve.speckle_type == "Objects.Geometry.Arc":
				fArcShape = toFreecadArc(curve)
				fEdges.append(fArcShape)
		
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
			#fFace = Part.Face(fWire) #works only for planar faces
			fFace = Part.makeFilledFace(fWire)
			fFaces.append(fFace)
		
		fShell = Part.Shell(fFaces)
		
		fSolid = Part.Solid(fShell)
		
		Part.show(fSolid)