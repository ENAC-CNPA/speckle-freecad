#import FreeCAD libraries
import FreeCAD as App
import Part, math

#import Speckle libraries
from typing import List
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_default_account
from specklepy.objects import Base
from specklepy.objects.geometry import (
     Mesh, Curve, Interval, Box, Point, Plane, Vector, Polyline, Circle
)

#set links to Speckle
client = SpeckleClient(host="https://app.speckle.systems/")
account = get_default_account()
client.authenticate_with_account(account)
stream_id = "6cf358a40e"

#set container of all elements
data = Base()
data.elements = []

#get FreeCAD Part objects
objects = App.ActiveDocument.Objects
for object in objects:
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
		print(basePlane.to_list())
		#create Speckle box
		myBox = Box(
		    basePlane = basePlane,
		    xSize = Interval.from_list([0, width.Value]),
		    ySize = Interval.from_list([0, length.Value]),
		    zSize = Interval.from_list([0, height.Value])
		)
		#add to data to be sent
		data.elements.append(myBox)
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
		myCircle = Circle(
			radius = radius,
			plane = plane,
			domain = domain
		)
		#add to data to be sent
		data.elements.append(myCircle)
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