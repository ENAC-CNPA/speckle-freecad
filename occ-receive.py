# Init python-occ
from OCC.Core.gp import gp_Pnt, gp_Circ, gp_Ax2, gp_Dir
from OCC.Core.GC import GC_MakeArcOfCircle
from OCC.Core.TColgp import TColgp_Array1OfPnt, TColgp_Array2OfPnt, TColgp_Array1OfPnt2d
from OCC.Core.TColStd import TColStd_Array1OfReal, TColStd_Array1OfInteger
from OCC.Core.Geom import Geom_BSplineCurve, Geom_Line, Geom_BSplineSurface, Geom_Circle, Geom_TrimmedCurve
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeVertex, BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeShell
from OCC.Display.SimpleGui import init_display
from OCC.Core.ShapeFix import ShapeFix_Edge, ShapeFix_Shape
from OCC.Core.TopoDS import TopoDS_Edge, TopoDS_Face
from OCC.Core.BRep import BRep_Tool
from OCC.Core.Geom2d import Geom2d_Line, Geom2d_Circle, Geom2d_TrimmedCurve
from OCC.Core.gp import gp_Pnt2d, gp_Lin2d, gp_Circ2d, gp_Ax2d, gp_Vec2d, gp_Dir2d
from OCC.Core.Geom2d import Geom2d_BSplineCurve
from OCC.Core.BRep import BRep_Builder
#from OCC.Core.ElCLib import ElCLib_Parameter

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
    #received = operations.receive("0bd349d32c8a9b00942709495e7b8dab", transport) # arch face
    #received = operations.receive("7b9ef1e597899c804f833d17d917ae05", transport) # planar surface with mix of edges types
    #received = operations.receive("348518420eaa2f0e1c6c0c6bd92d2b89", transport) # planar triangular face
    #received = operations.receive("161c29e5346e8988ab87c00aa5477630", transport) # planar triangular face with triangular hole
    #received = operations.receive("1008040021ab18d29392598684ffe569", transport) # planar pentagonal face with pentagonal hole
    #received = operations.receive("b4a7e732d4f03bea608b59e311f0bf52", transport) # planar pentagonal face with arched hole
    #received = operations.receive("90f988a827c1021abc3125f69e3c70b3", transport) # planar pentagonal face with circular hole
    #received = operations.receive("397dfde2f1e10379f7db810a0e27644c", transport) # planar pentagonal face with multiple holes
    #received = operations.receive("eb5d50ae43a78dcecc4a84e52f179ecb", transport) # planar pentagonal face with multiple holes of each type
    #received = operations.receive("3b320207576b80c0134fde287653806e", transport) # 3D surface
    #received = operations.receive("de3d9777e53fac1b047ff019e594f63e", transport) # spherical triangular face
    #received = operations.receive("42bb9190e8dc0c071898bb434e274f9d", transport) # loft of arcs of circles
    #received = operations.receive("9c6c57fc183435879178ea8b73ebf963", transport) # trimmed 3D surface
    received = operations.receive("bc043113ca32744823c6c627f934469e", transport) # trimmed 3D surface with hole
    #received = operations.receive("972bd504c8bad2a8cc83b5a0147307c5", transport) # planar rectangular face with rectangular holes
    
    
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
    
    # Create a 3D OCC edge
    o_line_edge = BRepBuilderAPI_MakeEdge(o_start, o_end).Edge()

    return o_line_edge

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
    
    o_arc = o_arc_maker.Value()

    # Convert to an edge for display or modeling
    o_arc_edge = BRepBuilderAPI_MakeEdge(o_arc).Edge()

    return o_arc_edge

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
    
    o_curve_edge = BRepBuilderAPI_MakeEdge(o_curve).Edge()
    
    return o_curve_edge

# Convert a Speckle 2D curve (in UV space) to an OpenCascade Geom2d_Curve for Breps
def curve2D_from_speckle_to_occ(s_curve2D):

    if s_curve2D.speckle_type == "Objects.Geometry.Line":
        start_uv = gp_Pnt2d(s_curve2D.start.x, s_curve2D.start.y)
        end_uv = gp_Pnt2d(s_curve2D.end.x, s_curve2D.end.y)
        direction = gp_Dir2d(gp_Vec2d(start_uv, end_uv))
        o_curve2D = Geom2d_Line(gp_Lin2d(start_uv, direction))
        return o_curve2D
    
    elif s_curve2D.speckle_type == "Objects.Geometry.Circle": # Still problematic inside/outside
        # Extract Speckle parameters
        s_radius = s_curve2D.radius
        s_plane = s_curve2D.plane
        s_origin = s_plane.origin
        s_normal = s_plane.normal

        # Convert Speckle data to OCC
        o_center = gp_Pnt2d(s_origin.x, s_origin.y)
        o_radius = s_radius

        # Create an OCC 2D circle
        o_axis = gp_Ax2d(o_center, gp_Dir2d(1, 0))
        o_curve2D = Geom2d_Circle(gp_Circ2d(o_axis, o_radius))

        return o_curve2D
    
        """
    elif s_curve2D.speckle_type == "Objects.Geometry.Arc": # Don't find ElClib
        # Extract Speckle parameters
        s_center = s_curve2D.plane.origin
        s_radius = s_curve2D.radius
        s_start = s_curve2D.startPoint
        s_end = s_curve2D.endPoint

        # Convert to OCC 2D types
        o_center = gp_Pnt2d(s_center.x, s_center.y)
        o_start = gp_Pnt2d(s_start.x, s_start.y)
        o_end = gp_Pnt2d(s_end.x, s_end.y)

        # Define the full 2D circle
        axis = gp_Ax2d(o_center, gp_Dir2d(1, 0))  # Default direction
        full_circle = Geom2d_Circle(gp_Circ2d(axis, s_radius))

        # Get curve parameters for trimming
        start_param = ElCLib_Parameter(full_circle.Circ2d(), o_start)
        end_param = ElCLib_Parameter(full_circle.Circ2d(), o_end)

        # Trim the circle to form an arc
        o_arc = Geom2d_TrimmedCurve(full_circle, start_param, end_param)

        return o_arc
    
        """
    elif s_curve2D.speckle_type == "Objects.Geometry.Curve":
        # Extract Speckle curve data
        s_degree = s_curve2D.degree
        s_points = s_curve2D.points
        s_knots = s_curve2D.knots
        s_weights = s_curve2D.weights
        s_periodic = s_curve2D.periodic
        s_rational = s_curve2D.rational

        num_poles = len(s_points) // 3

        # Convert poles to OCC format
        o_poles = TColgp_Array1OfPnt2d(1, num_poles)
        for i, c in enumerate(range(0, len(s_points), 3), start=1):
            o_poles.SetValue(i, gp_Pnt2d(s_points[c], s_points[c+1]))

        # Convert knots to OCC format
        def process_knots(s_knots):
            unique_knots = list(dict.fromkeys(s_knots))  # Remove duplicates
            num_knots = len(unique_knots)
            knots = TColStd_Array1OfReal(1, num_knots)
            mults = TColStd_Array1OfInteger(1, num_knots)
            
            last_knot = None
            i = 1
            for j, knot in enumerate(s_knots, start=1):
                if last_knot is None or last_knot != knot:
                    knots.SetValue(i, knot)
                    mults.SetValue(i, 1)
                    i += 1
                else:
                    mults.SetValue(i - 1, mults.Value(i - 1) + 1)
                last_knot = knot

            # Ensure first and last multiplicities are (degree + 1)
            mults.SetValue(1, s_degree + 1)
            mults.SetValue(num_knots, s_degree + 1)

            return knots, mults
        
        o_knots, o_mults = process_knots(s_knots)

        # Convert weights
        if s_rational:
            o_weights = TColStd_Array1OfReal(1, len(s_weights))
            for i, weight in enumerate(s_weights, start=1):
                o_weights.SetValue(i, weight)
        else:
            o_weights = None

        # Create OpenCascade 2D B-Spline Curve
        if o_weights != None:
            o_curve2D = Geom2d_BSplineCurve(
                o_poles, o_weights, o_knots, o_mults, s_degree, s_periodic
            )
        else:
            o_curve2D = Geom2d_BSplineCurve(
                o_poles, o_knots, o_mults, s_degree, s_periodic
            )
        
        return o_curve2D

# Receive elements
for element in all_elements:
    
    if element.speckle_type == "Objects.Geometry.Point":
        o_point = point_from_speckle_to_occ(element)
        #Display Point
        display.DisplayShape(o_point, update=True)
    
    elif element.speckle_type == "Objects.Geometry.Line":
        o_line, _ = line_from_speckle_to_occ(element)
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
        s_curve2D = s_brep.Curve2D
        s_loops = s_brep.Loops
        s_trims = s_brep.Trims
        
        o_faces = []
        o_TopoDS_Faces = []
        o_Geom_Surfaces = []
		
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
            
            o_Geom_Surfaces.append(o_b_spline_surface)
                        
            # Convert the surface into a TopoDS_Face
            o_surface = BRepBuilderAPI_MakeFace(o_b_spline_surface, 1e-6).Face()
            
            o_TopoDS_Faces.append(o_surface)
            
        #display.DisplayShape(o_TopoDS_Faces[0], update=True)
        
        # List edges and create pcurves
        def create_edge(element):
            if element.speckle_type == "Objects.Geometry.Line":
                return line_from_speckle_to_occ(element)
            elif element.speckle_type == "Objects.Geometry.Circle":
                return circle_from_speckle_to_occ(element)
            elif element.speckle_type == "Objects.Geometry.Arc":
                return arc_from_speckle_to_occ(element)
            elif element.speckle_type == "Objects.Geometry.Curve":
                return curve_from_speckle_to_occ(element)
        
        o_TopoDS_Edges = []
        for curve3D in s_curve3D:
            edge = create_edge(curve3D)
            o_TopoDS_Edges.append(edge)
        
        o_Geom2d_Curves = []    
        for curve2D in s_curve2D:      
            # Convert Speckle 2D curve to OCC Geom2d_Curve
            pcurve = curve2D_from_speckle_to_occ(curve2D)
            o_Geom2d_Curves.append(pcurve)
            
        # Loops and trims
        for i, loop in enumerate(s_loops):
            # Get Speckle parameters
            FaceIndex = loop.FaceIndex
            TrimIndices = loop.TrimIndices
            
            # Create Wire Maker
            o_wire_maker = BRepBuilderAPI_MakeWire()
            
            # Inspect Trims
            trims = [s_trims[i] for i in TrimIndices]
            for trim in trims:
                # Attach pcurve to edge
                EdgeIndex = trim.EdgeIndex
                edge = o_TopoDS_Edges[EdgeIndex]
                CurveIndex = trim.CurveIndex
                pcurve = o_Geom2d_Curves[CurveIndex]
                face = o_TopoDS_Faces[0]
                tolerance = 1e-3
                builder = BRep_Builder()
                builder.UpdateEdge(edge, pcurve, face, tolerance)
                # Add edge to wire
                o_wire_maker.Add(edge)
                
            # Make Wire and Trim the Surface
            o_wire = o_wire_maker.Wire()
            if i == 0:
                o_trimmed_face_maker = BRepBuilderAPI_MakeFace(o_Geom_Surfaces[FaceIndex], o_wire, True)
                o_trimmed_face = o_trimmed_face_maker.Face()
            else:
                o_trimmed_face_maker = BRepBuilderAPI_MakeFace(o_trimmed_face, o_wire)
                o_trimmed_face = o_trimmed_face_maker.Face()
        
        # Fix Shape
        fixer = ShapeFix_Shape(o_trimmed_face)
        fixer.Perform()
        o_fixed_face = fixer.Shape()
                
        # Display Brep
        display.DisplayShape(o_fixed_face, update=True)    
        
    start_display()