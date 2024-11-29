#import FreeCAD libraries
import FreeCAD as App
import Part, math

#import Speckle libraries
from typing import List
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_default_account
from specklepy.objects import Base
from specklepy.objects.geometry import (
     Box, Brep, BrepEdge, BrepFace, BrepLoop, BrepLoopType, BrepTrim, BrepTrimType, Circle, Curve, Interval, Line, Mesh, Plane, Point, Polyline, Surface, Vector
)

#set links to Speckle
client = SpeckleClient(host="https://app.speckle.systems/")
account = get_default_account()
client.authenticate_with_account(account)
stream_id = "6cf358a40e"

#set container of all elements
data = Base()
data.elements = []

#Speckle: WIP create Speckle Brep from scratch
#create Speckle Points
sVertices = []
point1 = Point(
	x = 0.0,
	y = 0.0,
	z = 0.0
)
sVertices.append(point1)
point2 = Point(
	x = 1.0,
	y = 0.0,
	z = 0.0
)
sVertices.append(point2)
point3 = Point(
	x = 0.0,
	y = 1.0,
	z = 0.0
)
sVertices.append(point3)
#create Speckle Curve3D
sCurve3D = []
line1 = Line(
	start = point1,
	end = point2
)
sCurve3D.append(line1)
line2 = Line(
	start = point2,
	end = point3
)
sCurve3D.append(line2)
line3 = Line(
	start = point3,
	end = point1
)
sCurve3D.append(line3)
#create Speckle Curve2D
sCurve2D = [line1, line2, line3]
#create Speckle Surface
sSurfaces = []
firstSurface = Surface(
	degreeU = 1,
	degreeV = 1,
	rational = False,
	area = 0.5,
	pointData = [
	    0.0, 0.0, 0.0,
	    1.0, 0.0, 0.0,
	    0.0, 1.0, 0.0
	],
	countU = 2,
	countV = 2,
	#bbox = bbox,
	closedU = False,
	closedV = False,
	domainU = Interval(
		start=0.0,
		end=1.0
	),
	domainV = Interval(
		start = 0.0,
		end = 1.0
	),
	knotsU = [0.0, 1.0],
	knotsV = [0.0, 1.0],
)
sSurfaces.append(firstSurface)
#create Speckle Brep Edge
sEdges = []
edge1 = BrepEdge(
	Curve3dIndex = 0,
	TrimIndices = [0],
	StartIndex = 0,
	EndIndex = 1,
	ProxyCurveIsReversed = False,
	Domain=Interval(start = 0.0, end = 1.0)
)
sEdges.append(edge1)
edge2 = BrepEdge(
	Curve3dIndex = 1,
	TrimIndices = [1],
	StartIndex = 1,
	EndIndex = 2,
	ProxyCurveIsReversed = False,
	Domain=Interval(start = 0.0, end = 1.0)
)
sEdges.append(edge2)
edge3 = BrepEdge(
	Curve3dIndex = 2,
	TrimIndices = [2],
	StartIndex = 2,
	EndIndex = 0,
	ProxyCurveIsReversed = False,
	Domain=Interval(start = 0.0, end = 1.0)
)
sEdges.append(edge3)
#create Speckle Brep Loop
sLoops = []
loop1 = BrepLoop(
	FaceIndex = 0,
	TrimIndices = [0, 1, 2],
	Type = BrepLoopType.Outer
)
sLoops.append(loop1)
#create Speckle Brep Face
sFaces = []
face1 = BrepFace(
	SurfaceIndex = 0,
	OuterLoopIndex = 0,
	OrientationReversed = False,
	LoopIndices = [0]
)
sFaces.append(face1)
#create Speckle Brep Trims
sTrims = []
trim1 = BrepTrim(
	EdgeIndex = 0,
	StartIndex = 0,
	EndIndex = 1,
	FaceIndex = 0,
	LoopIndex = 0,
	CurveIndex = 0,
	IsoStatus = 0,
	TrimType=BrepTrimType.Boundary,
	IsReversed = False,
	Domain=Interval(start = 0.0, end = 1.0),
)
sTrims.append(trim1)
trim2 = BrepTrim(
	EdgeIndex = 1,
	StartIndex = 1,
	EndIndex = 2,
	FaceIndex = 0,
	LoopIndex = 0,
	CurveIndex = 1,
	IsoStatus = 0,
	TrimType=BrepTrimType.Boundary,
	IsReversed = False,
	Domain=Interval(start = 0.0, end = 1.0),
)
sTrims.append(trim2)
trim3 = BrepTrim(
	EdgeIndex = 2,
	StartIndex = 2,
	EndIndex = 0,
	FaceIndex = 0,
	LoopIndex = 0,
	CurveIndex = 2,
	IsoStatus = 0,
	TrimType=BrepTrimType.Boundary,
	IsReversed = False,
	Domain=Interval(start = 0.0, end = 1.0),
)
sTrims.append(trim3)
#create Speckle Brep
sBrep = Brep(
	Surfaces = sSurfaces,
	Curve3D = sCurve3D,
	Curve2D = sCurve2D,
	Vertices = sVertices,
	Edges = sEdges,
	Loops = sLoops,
	Faces = sFaces,
	Trims = sTrims,
	IsClosed = False,
	Orientation = 0
)
#add to data to be sent
data.elements.append(sBrep)

#get FreeCAD Part objects
objects = App.ActiveDocument.Objects
for object in objects:
	#Let's call fObject = from FreeCAD, sObject = from Speckle
	if object.TypeId == 'Part::Box':
		#extract FreeCAD properties
		propertiesList = object.PropertiesList
		height = object.Height
		length = object.Length
		placement = object.Placement
		shape = object.Shape
		width = object.Width
		#extract FreeCAD placement properties
		angle = placement.Rotation.Angle
		axis = placement.Rotation.Axis		
		position = placement.Base
		#create Speckle basePlane
		basePlane = Plane.from_list([
			position.x, position.y, position.z,
			axis.x, axis.y, axis.z,
			math.cos(angle), math.sin(angle), 0.0,
			math.cos(angle+math.pi/2), math.sin(angle+math.pi/2), 0.0,
		])
		#create Speckle box
		sBox = Box(
		    basePlane = basePlane,
		    xSize = Interval.from_list([0, width.Value]),
		    ySize = Interval.from_list([0, length.Value]),
		    zSize = Interval.from_list([0, height.Value])
		)
		#add to data to be sent
		data.elements.append(sBox)
	elif object.TypeId == 'Part::Circle':
		#extract FreeCAD properties
		propertiesList = object.PropertiesList
		radius = object.Radius
		placement = object.Placement
		#extract FreeCAD placement properties
		angle = placement.Rotation.Angle
		axis = placement.Rotation.Axis		
		position = placement.Base
		#create Plane
		plane = Plane.from_list([
			position.x, position.y, position.z,
			axis.x, axis.y, axis.z,
			math.cos(angle), math.sin(angle), 0.0,
			math.cos(angle+math.pi/2), math.sin(angle+math.pi/2), 0.0,
		])
		#create interval
		domain = Interval(start = 0.0, end = 1.0) 
		#create Speckle circle
		sCircle = Circle(
			radius = radius,
			plane = plane,
			domain = domain
		)
		#add to data to be sent
		data.elements.append(sCircle)
	elif object.TypeId == 'Part::Line':
		fEdge = object.Shape.Edges[0]
		fStart = fEdge.Vertexes[0]
		sStart = Point(
			x = fStart.Point.x,
			y = fStart.Point.y,
			z = fStart.Point.z
		)
		fEnd = fEdge.Vertexes[1]
		sEnd = Point(
			x = fEnd.Point.x,
			y = fEnd.Point.y,
			z = fEnd.Point.z
		)
		sLine = Line(
	    	start = sStart,
	    	end = sEnd
		)
		#add to data to be sent
		data.elements.append(sLine)
	
	#Speckle: Brep = Freecad: Face, etc
	elif object.TypeId == 'Part::Face' or object.TypeId == 'Part::RuledSurface':
		fShape = object.Shape
		#map points and edges of the FreeCAD Brep by their coordinates
		#to later find their index when building the Speckle Brep
		fPointsMap = []
		fVertexes = fShape.Vertexes
		for vertex in fVertexes:
			coordinates = (vertex.Point.x, vertex.Point.y, vertex.Point.z)
			fPointsMap.append(coordinates)
		fEdgesMap = []
		fEdges = fShape.Edges
		for edge in fEdges:
			edgeCoordinates = []
			vertexes = edge.Vertexes
			for vertex in vertexes:
				coordinates = (vertex.Point.x, vertex.Point.y, vertex.Point.z)
				edgeCoordinates.append(coordinates)
			fEdgesMap.append(edgeCoordinates)
		fFaces = fShape.Faces
		#convert Freecad Brep data to Speckle Brep data :
		#create Speckle Surfaces for Brep
		sSurfaces = []
		for face in fFaces:
			fSurface = face.Surface
			sDegreeU = fSurface.UDegree
			sDegreeV = fSurface.VDegree
			sRational = fSurface.isURational() or fSurface.isVRational()
			fPoles = fSurface.getPoles()
			sPointData = []
			for subpoles in fPoles:
				for pole in subpoles:
					sPointData.append(pole.x)
					sPointData.append(pole.y)
					sPointData.append(pole.z)
			sCountU = fSurface.NbUPoles
			sCountV = fSurface.NbVPoles
			sClosedU = fSurface.isUClosed()
			sClosedV = fSurface.isVClosed()
			sDomainUStart = fSurface.UKnotSequence[0]
			sDomainUEnd = fSurface.UKnotSequence[-1]
			sDomainVStart = fSurface.VKnotSequence[0]
			sDomainVEnd = fSurface.VKnotSequence[-1]
			sDomainU = Interval(start = sDomainUStart, end = sDomainUEnd)
			sDomainV = Interval(start = sDomainVStart, end = sDomainVEnd)
			sKnotsU = fSurface.UKnotSequence
			sKnotsV = fSurface.VKnotSequence
			sSurface = Surface(
				degreeU = sDegreeU,
				degreeV = sDegreeV,
				rational = sRational,
				pointData = sPointData,
				countU = sCountU,
				countV = sCountV,
				closedU = sClosedU,
				closedV = sClosedV,
				domainU = sDomainU,
				domainV = sDomainV,
				knotsU = sKnotsU,
				knotsV = sKnotsV
			)
			sSurfaces.append(sSurface)
		#create Speckle Curve3D for Brep
		sCurve3D = []
		for edge in fEdges:
			fStart = edge.Vertexes[0]
			sStart = Point(
				x = fStart.Point.x,
				y = fStart.Point.y,
				z = fStart.Point.z
			)
			fEnd = edge.Vertexes[1]
			sEnd = Point(
				x = fEnd.Point.x,
				y = fEnd.Point.y,
				z = fEnd.Point.z
			)
			sLine = Line(
	    		start = sStart,
	    		end = sEnd
			)
			sCurve3D.append(sLine)
		#create Speckle Vertices for Brep
		sVertices = []
		for vertex in fVertexes:
			sPoint = Point(
				x = vertex.Point.x,
				y = vertex.Point.y,
				z = vertex.Point.z
			)
			sVertices.append(sPoint)
		#create Speckle Edges for Brep
		sEdges = []
		for i, edge in enumerate(fEdges):
			vertexes = edge.Vertexes
			startVertex = vertexes[0]
			startCoordinates = (startVertex.Point.x, startVertex.Point.y, startVertex.Point.z)
			endVertex = vertexes[1]
			endCoordinates = (endVertex.Point.x, endVertex.Point.y, endVertex.Point.z)
			for j, point in enumerate(fPointsMap):
				if point == startCoordinates:
					fStartIndex = j
				elif point == endCoordinates:
					fEndIndex = j	
			sBrepEdge = BrepEdge(
				Curve3dIndex = i,
				StartIndex = fStartIndex,
				EndIndex = fEndIndex
			)
			sEdges.append(sBrepEdge)
		#create Speckle Faces for Brep
		sFaces = []
		for face in fFaces:
			sBrepFace = BrepFace(
				SurfaceIndex = 0,
				OuterLoopIndex = 0,
				OrientationReversal = False,
				LoopIndices = [0]
			)
			sFaces.append(sBrepFace)
		#create Speckle Brep
		sBrep = Brep(
			Surfaces = sSurfaces,
			Curve3D = sCurve3D,
			Vertices = sVertices,
			Edges = sEdges, #cause un bug, voir lignes 211 à 213
			#Faces = sFaces #cause un bug
		)
		#add to data to be sent
		data.elements.append(sBrep)
		
#send to Speckle
from specklepy.transports.server import ServerTransport
from specklepy.api import operations
transport = ServerTransport(client=client, stream_id=stream_id)
hash = operations.send(base=data, transports=[transport])
commid_id = client.commit.create(
    stream_id=stream_id, 
    object_id=hash, 
    message="this is Parts I made in FreeCAD",
    )
print("sent")