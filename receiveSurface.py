#WIP
import FreeCAD as App
import Part

from specklepy.api import operations
from specklepy.api.wrapper import StreamWrapper

if __name__ == "__main__":
    stream_url = "https://app.speckle.systems/projects/6cf358a40e/models/e01ffbc891"
    wrapper = StreamWrapper(stream_url)

    transport = wrapper.get_transport()
	
	#id of main collection:
    received = operations.receive("9678757ba141d255e3445bcfdd34d718", transport)

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
		
		#building Surfaces (wip) :
		sSurfaces = sBrep.Surfaces
		for surface in sSurfaces:
			
			sDegreeU = surface.degreeU
			sDegreeV = surface.degreeV
			sPointData = surface.pointData
			sCountU = surface.countU
			sCountV = surface.countV
			sKnotsU = surface.knotsU
			sKnotsV = surface.knotsV
			
			fPoles = []
			index = 0
			for v in range(sCountV):
				row = []
				for u in range(sCountU):
					x = sPointData[index]
					y = sPointData[index + 1]
					z = sPointData[index + 2]
					fVertex = App.Vector(x, y, z)
					row.append(fVertex)
					index += 4
				fPoles.append(row)
			fUDegree = sDegreeU
			fVDegree = sDegreeV
			fUKnots = sKnotsU
			fVKnots = sKnotsV
			fUMults = [2, 2]
			fVMults = [2, 2]
			fUPeriodic = False
			fVPeriodic = False
			
			fBSpline = Part.BSplineSurface()
			
			fBSpline.buildFromPolesMultsKnots(
				fPoles,
				fUMults,
				fVMults,
				fUKnots,
				fVKnots,
				fUPeriodic,
				fVPeriodic,
				fUDegree,
				fVDegree,
				#fWeights?
			)
			fBSplineShape = fBSpline.toShape()
			fFaces.append(fBSplineShape)
		
		fShell = Part.Shell(fFaces)
		
		Part.show(fShell)