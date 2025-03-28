# Init python-occ
from OCC.Core.gp import gp_Pnt, gp_Circ, gp_Ax2, gp_Dir
from OCC.Core.GC import GC_MakeArcOfCircle
from OCC.Core.TColgp import TColgp_Array1OfPnt, TColgp_Array2OfPnt
from OCC.Core.TColStd import TColStd_Array1OfReal, TColStd_Array1OfInteger
from OCC.Core.Geom import Geom_BSplineCurve, Geom_Line, Geom_BSplineSurface, Geom_Circle, Geom_TrimmedCurve
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeVertex, BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeShell
from OCC.Display.SimpleGui import init_display

# Initialize the display
display, start_display, add_menu, add_function_to_menu = init_display()

# Init Speckle
from specklepy.api import operations
from specklepy.api.wrapper import StreamWrapper

if __name__ == "__main__":
    stream_url = "https://app.speckle.systems/projects/e52fc1e920/models/4e35c79134"
    wrapper = StreamWrapper(stream_url)

    transport = wrapper.get_transport()
	
	#id of main collection
    #received = operations.receive("fa8b2bea472ea99eb074585802c144c1", transport) # point
    #received = operations.receive("4b6b20120c4270406e8cefb0e31d8e6e", transport) # line
    #received = operations.receive("c0efbf4617325abdb10c5d85f192fdad", transport) # polyline
    #received = operations.receive("c9132104319d7d09c251a9896de93060", transport) # circle
    #received = operations.receive("a65d3dec8951963906ff9c122b874675", transport) # arc
    #received = operations.receive("26d680179faff3c9be98f88aa5de71d3", transport) # curve
    #received = operations.receive("4ba26e43e5b70463cdb060b36cc448d3", transport) # rectangular face
    #received = operations.receive("cdc9f429541627224c00610898c664d7", transport) # pentagone face
    #received = operations.receive("390dc996c2567991b1f36004c20cba69", transport) # circular face
    received = operations.receive("0bd349d32c8a9b00942709495e7b8dab", transport) # arch face
    
    
all_elements = []

def process_item(item):
	if item.speckle_type == "Speckle.Core.Models.Collection":
		for element in item.elements:
			process_item(element)
	else:
		all_elements.append(item)
process_item(received)

# Conversion functions from Speckle to OCC

# Point
def point_from_speckle_to_occ(element):
    s_point = element
    o_point = BRepBuilderAPI_MakeVertex(gp_Pnt(s_point.x, s_point.y, s_point.z)).Vertex()
    return o_point

# Line
def line_from_speckle_to_occ(element):
    # Extract Speckle parameters
    s_start = element.start
    s_end = element.end
    
    # Convert Speckle data to OCC
    o_start = gp_Pnt(s_start.x, s_start.y, s_start.z)
    o_end = gp_Pnt(s_end.x, s_end.y, s_end.z)
    
    # Create an OCC edge
    o_line = BRepBuilderAPI_MakeEdge(o_start, o_end).Edge()
    
    return o_line

# Polyline
def polyline_from_speckle_to_occ(element):
    s_polyline = element
    
    # Convert flat list to a list of gp_Pnt
    o_points = [gp_Pnt(s_polyline.value[i], s_polyline.value[i+1], s_polyline.value[i+2])
                for i in range(0, len(s_polyline.value), 3)]

    # Create a wire builder
    wire_builder = BRepBuilderAPI_MakeWire()

    # Add edges to the wire
    for i in range(len(o_points) - 1):
        edge = BRepBuilderAPI_MakeEdge(o_points[i], o_points[i+1]).Edge()
        wire_builder.Add(edge)

    # Close the polyline if needed
    if s_polyline.closed and len(o_points) > 2:
        edge = BRepBuilderAPI_MakeEdge(o_points[-1], o_points[0]).Edge()
        wire_builder.Add(edge)
        
    # Create wire (polyline)
    o_polyline = wire_builder.Wire()

    return o_polyline

# Circle
def circle_from_speckle_to_occ(element):
    # Extract Speckle parameters
    s_radius = element.radius
    s_plane = element.plane
    s_origin = s_plane.origin
    s_normal = s_plane.normal

    # Convert Speckle data to OCC
    o_center = gp_Pnt(s_origin.x, s_origin.y, s_origin.z)
    o_normal = gp_Dir(s_normal.x, s_normal.y, s_normal.z)
    o_radius = s_radius

    # Create an OCC circle
    o_circle = Geom_Circle(gp_Circ(gp_Ax2(o_center, o_normal), o_radius))

    # Convert to an edge for display or modeling
    o_circle_edge = BRepBuilderAPI_MakeEdge(o_circle).Edge()
    
    return o_circle_edge

# Arc
def arc_from_speckle_to_occ(element):
    # Extract Speckle parameters
    s_startPoint = element.startPoint
    s_midPoint = element.midPoint
    s_endPoint = element.endPoint

    # Convert Speckle data to OCC
    o_start_pnt = gp_Pnt(s_startPoint.x, s_startPoint.y, s_startPoint.z)
    o_mid_pnt = gp_Pnt(s_midPoint.x, s_midPoint.y, s_midPoint.z)
    o_end_pnt = gp_Pnt(s_endPoint.x, s_endPoint.y, s_endPoint.z)

    # Create an OCC arc
    o_arc_maker = GC_MakeArcOfCircle(o_start_pnt, o_mid_pnt, o_end_pnt)
    
    o_arc_curve = o_arc_maker.Value()

    # Convert to an edge for display or modeling
    o_arc = BRepBuilderAPI_MakeEdge(o_arc_curve).Edge()

    return o_arc

# Curve
def curve_from_speckle_to_occ(element):
    # Get Speckle parameters
    s_degree = element.degree
    s_periodic = element.periodic
    s_rational = element.rational
    s_points = element.points
    s_weights = element.weights
    s_knots = element.knots
    
    # Define poles and weights
    o_poles = TColgp_Array1OfPnt(1, len(s_points) // 3)
    o_weights = TColStd_Array1OfReal(1, len(s_weights))
    for i, c in enumerate(range(0, len(s_points), 3), start=1):
        o_poles.SetValue(i, gp_Pnt(s_points[c], s_points[c+1], s_points[c+2]))
        o_weights.SetValue(i, s_weights[i-1])
    
    # Define Knots
    def s_knots_to_o_knots_list(s_knots):
        o_knots_list = []
        i = 0
        while i < len(s_knots):
            while i + 1 < len(s_knots) and s_knots[i] == s_knots[i + 1]:
                i += 1
            o_knots_list.append(s_knots[i])
            i += 1
        return o_knots_list
    o_knots_list = s_knots_to_o_knots_list(s_knots)
    o_knots = TColStd_Array1OfReal(1, len(o_knots_list))
    for i, multiplicity in enumerate(o_knots, start=1):
        o_knots.SetValue(i, o_knots_list[i-1])
    
    # Define multiplicities    
    def s_knots_to_o_multiplicities_list(s_knots):
        o_multiplicities_list = []
        i = 0
        while i < len(s_knots):
            count = 1
            while i + 1 < len(s_knots) and s_knots[i] == s_knots[i + 1]:
                count += 1
                i += 1
            o_multiplicities_list.append(count)
            i += 1
        return o_multiplicities_list
    o_multiplicities_list = s_knots_to_o_multiplicities_list(s_knots)
    o_multiplicities = TColStd_Array1OfInteger(1, len(o_multiplicities_list))
    for i, multiplicity in enumerate(o_multiplicities, start=1):
        o_multiplicities.SetValue(i, o_multiplicities_list[i-1])
    
    # Define other parameters
    o_degree = s_degree
    o_periodic = s_periodic
    o_check_rational = s_rational
    
    # Create curve
    o_curve = Geom_BSplineCurve(
        o_poles, o_weights, o_knots, o_multiplicities, o_degree, o_periodic, o_check_rational
    )
    
    return o_curve

# Receive elements
for element in all_elements:
    
    if element.speckle_type == "Objects.Geometry.Point":
        o_point = point_from_speckle_to_occ(element)
        #Display Point
        display.DisplayShape(o_point, update=True)
    
    elif element.speckle_type == "Objects.Geometry.Line":
        o_line = line_from_speckle_to_occ(element)
        # Display Line
        display.DisplayShape(o_line, update=True)
        
    elif element.speckle_type == "Objects.Geometry.Polyline":
        o_polyline = polyline_from_speckle_to_occ(element)
        # Display Polyline
        display.DisplayShape(o_polyline, update=True)
    
    elif element.speckle_type == "Objects.Geometry.Circle":
        o_circle = circle_from_speckle_to_occ(element)
        # Display Circle
        display.DisplayShape(o_circle, update=True)
        
    elif element.speckle_type == "Objects.Geometry.Arc":
        o_arc = arc_from_speckle_to_occ(element)
        # Display Arc
        display.DisplayShape(o_arc, update=True)
    
    elif element.speckle_type == "Objects.Geometry.Curve":
        o_curve = curve_from_speckle_to_occ(element)
        # Display Curve
        display.DisplayShape(o_curve, update=True)
        
    elif element.speckle_type == "Objects.Geometry.Brep":
        
        s_brep = element
        
        s_curve3D = s_brep.Curve3D
        
        o_edges = []
        
        for curve in s_curve3D :
            if curve.speckle_type == "Objects.Geometry.Line":
                o_edge = line_from_speckle_to_occ(curve)
                o_edges.append(o_edge)
            elif curve.speckle_type == "Objects.Geometry.Circle":
                o_edge = circle_from_speckle_to_occ(curve)
                o_edges.append(o_edge)
            elif curve.speckle_type == "Objects.Geometry.Arc":
                o_edge = arc_from_speckle_to_occ(curve)
                o_edges.append(o_edge)
        
        s_loops = s_brep.Loops
        s_trims = s_brep.Trims
        
        o_faces = []
		
		# Receive surface
        s_surfaces = s_brep.Surfaces
        for surface in s_surfaces:
            
            # Get Speckle parameters
            s_degreeU = surface.degreeU
            s_degreeV = surface.degreeV
            s_pointData = surface.pointData
            s_countU = surface.countU
            s_countV = surface.countV
            s_knotsU = surface.knotsU
            s_knotsV = surface.knotsV
            
            # Convert Speckle control points to OCC poles
            o_poles = TColgp_Array2OfPnt(1, s_countU, 1, s_countV)
            index = 0
            
            for u in range(1, s_countU + 1):
                for v in range(1, s_countV + 1):
                    x = s_pointData[index]
                    y = s_pointData[index + 1]
                    z = s_pointData[index + 2]
                    o_poles.SetValue(u, v, gp_Pnt(x, y, z))
                    index += 4 # the fourth coordinate is the weight, skip
            
            # Convert Speckle knots/multiplicities to OCC 
            def receive_knots_and_mults(s_knots, degree):
                unique_knots = list(dict.fromkeys(s_knots))  # Remove duplicates while preserving order
                num_unique_knots = len(unique_knots)

                knots = TColStd_Array1OfReal(1, num_unique_knots)
                mults = TColStd_Array1OfInteger(1, num_unique_knots)

                i, last_knot = 1, None
                for j, knot in enumerate(s_knots, start=1):
                    if last_knot is None or last_knot != knot:
                        knots.SetValue(i, knot)
                        mults.SetValue(i, 1)
                        i += 1
                    else:
                        mults.SetValue(i - 1, mults.Value(i - 1) + 1)
                    last_knot = knot

                # Ensure first and last multiplicities are (degree + 1)
                mults.SetValue(1, degree + 1)
                mults.SetValue(num_unique_knots, degree + 1)

                return knots, mults
            
            o_knotsU, o_multsU = receive_knots_and_mults(s_knotsU, s_degreeU)
            o_knotsV, o_multsV = receive_knots_and_mults(s_knotsV, s_degreeV)
            
            o_uPeriodic = False
            o_vPeriodic = False
            o_degreeU = s_degreeU
            o_degreeV = s_degreeV
                        
            # Create the OCC B-Spline surface
            o_b_spline_surface = Geom_BSplineSurface(
                o_poles, o_knotsU, o_knotsV, o_multsU, o_multsV, o_degreeU, o_degreeV, o_uPeriodic, o_vPeriodic
            )
            
            # Convert the surface into a TopoDS_Face
            o_surface = BRepBuilderAPI_MakeFace(o_b_spline_surface, 1e-6).Face()
            
        # Collect the edges to form a wire
        o_wire_maker = BRepBuilderAPI_MakeWire()
        for edge in o_edges:
            o_wire_maker.Add(edge)
        o_wire = o_wire_maker.Wire()
        
        # Trim the face with the wire
        o_trimmed_face_maker = BRepBuilderAPI_MakeFace(o_b_spline_surface, o_wire)
        o_trimmed_face = o_trimmed_face_maker.Face()
            
        # Display Brep
        display.DisplayShape(o_trimmed_face, update=True)
        
    start_display()