#import FreeCAD libraries
import FreeCAD as App
import Part, math

#import Speckle libraries
from typing import List
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_default_account
from specklepy.objects import Base
from specklepy.objects.geometry import (
     Box, Brep, BrepEdge, BrepFace, Circle, Curve, Interval, Line, Mesh, Plane, Point, Polyline, Surface, Vector
)

#set links to Speckle
client = SpeckleClient(host="https://app.speckle.systems/")
account = get_default_account()
client.authenticate_with_account(account)
stream_id = "6cf358a40e" #set here your own stream id

#set container of all elements
data = Base()
data.elements = []

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
  
	elif object.TypeId == 'Part::RuledSurface':
		fSurface = object.Shape.Faces[0].Surface
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
		#add to data to be sent
		data.elements.append(sSurface)
  
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