import FreeCAD as App
import Part

from specklepy.api import operations
from specklepy.api.wrapper import StreamWrapper

if __name__ == "__main__":
    stream_url = "https://app.speckle.systems/projects/6cf358a40e/models/e01ffbc891"
    wrapper = StreamWrapper(stream_url)

    transport = wrapper.get_transport()
	
	#id of main collection:
    received = operations.receive("af0d1b8acb61b337dd761119e3c7013a", transport)

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
	
	elif element.speckle_type == "Objects.Geometry.Curve":
		
		#get Speckle parameters :
		sDegree = element.degree
		sPeriodic = element.periodic
		sPoints = element.points
		sWeights = element.weights
		sKnots = element.knots
		
		#convert to Freecad parameters :
		fPoles = []
		for i in range(0, len(sPoints), 3):
			pole = App.Vector(sPoints[i], sPoints[i+1], sPoints[i+2])
			fPoles.append(pole)
		
		def sKnots_to_fMults(sKnots):
			fMultsList = []
			i = 0
			while i < len(sKnots):
				count = 1
				while i + 1 < len(sKnots) and sKnots[i] == sKnots[i + 1]:
					count += 1
					i += 1
				fMultsList.append(count)
				i += 1
			return tuple(fMultsList)
		fMults = sKnots_to_fMults(sKnots)
		
		def sKnots_to_fKnots(sKnots):
			fKnotsList = []
			i = 0
			while i < len(sKnots):
				while i + 1 < len(sKnots) and sKnots[i] == sKnots[i + 1]:
					i += 1
				fKnotsList.append(sKnots[i])
				i += 1
			return tuple(fKnotsList)
		fKnots = sKnots_to_fKnots(sKnots)
		
		fDegree = sDegree
		fPeriodic = sPeriodic
		fWeights = tuple(sWeights)
		
		#Build Freecad BSplineCurve :
		fBSpline = Part.BSplineCurve()
		fBSpline.buildFromPolesMultsKnots(
			poles = fPoles,
			mults = fMults,
			knots = fKnots,
			periodic = fPeriodic,
			degree = fDegree,
			weights = fWeights)
		fBSplineShape = fBSpline.toShape()
		Part.show(fBSplineShape)
	
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