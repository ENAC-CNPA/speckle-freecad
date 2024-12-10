#WIP : BREP
#is working : building a Freecad BSplineSurface from a Speckle Surface
#still to do to merge with Brep in receive.py : trim the surface with face borders

import FreeCAD as App
import Part

from specklepy.api import operations
from specklepy.api.wrapper import StreamWrapper

if __name__ == "__main__":
    stream_url = "https://app.speckle.systems/projects/6cf358a40e/models/e01ffbc891"
    wrapper = StreamWrapper(stream_url)

    transport = wrapper.get_transport()
	
	#id of main collection:
    received = operations.receive("fb1cd88be7ede3cd981641bc9e98f8ba", transport)

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
		
	if element.speckle_type == "Objects.Geometry.Brep":
		
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
		
		#building Surfaces :
		sSurfaces = sBrep.Surfaces
		for surface in sSurfaces:
			
			#get Speckle parameters :
			sDegreeU = surface.degreeU
			sDegreeV = surface.degreeV
			sPointData = surface.pointData
			sCountU = surface.countU
			sCountV = surface.countV
			sKnotsU = surface.knotsU
			sKnotsV = surface.knotsV
			
			#convert to Freecad parameters :
			fPoles = []
			index = 0
			
			for u in range(sCountU):
				column = []
				for v in range(sCountV):
					x = sPointData[index]
					y = sPointData[index + 1]
					z = sPointData[index + 2]
					fVertex = App.Vector(x, y, z)
					column.append(fVertex)
					index += 4 #the fourth coordinate is the weight
				fPoles.append(column)			
			
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
			fUMults = sKnots_to_fMults(sKnotsU)
			fUMults = (fUMults[0] + 1, *fUMults[1:-1], fUMults[-1] + 1)
			fVMults = sKnots_to_fMults(sKnotsV)
			fVMults = (fVMults[0] + 1, *fVMults[1:-1], fVMults[-1] + 1)
			
			def sKnots_to_fKnots(sKnots):
				fKnotsList = []
				i = 0
				while i < len(sKnots):
					while i + 1 < len(sKnots) and sKnots[i] == sKnots[i + 1]:
						i += 1
					fKnotsList.append(sKnots[i])
					i += 1
				return tuple(fKnotsList)
			fUKnots = sKnots_to_fKnots(sKnotsU)
			fVKnots = sKnots_to_fKnots(sKnotsV)
		
			fUPeriodic = False
			fVPeriodic = False
			fUDegree = sDegreeU
			fVDegree = sDegreeV
			
			#Build Freecad surface :
			fBSpline = Part.BSplineSurface()
			fBSpline.buildFromPolesMultsKnots(
				poles = fPoles,
				umults = fUMults,
				vmults = fVMults,
				uknots = fUKnots,
				vknots = fVKnots,
				uperiodic = fUPeriodic,
				vperiodic = fVPeriodic,
				udegree = fUDegree,
				vdegree = fVDegree
			)
			fBSplineShape = fBSpline.toShape()
			fFaces.append(fBSplineShape)
		
		fShell = Part.Shell(fFaces)
		
		Part.show(fShell)