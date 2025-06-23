# The code below works. 
# To trim surfaces, it doesn't project 3D curves on 2D curves related to the surface (pcurves), but do it directly in 3D.
# The resulting face is not directly clean and requires ShapeFix_Shape.

# Initialize python-occ
from OCC.Core.BRep import BRep_Builder, BRep_Tool
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeVertex, BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeWire, BRepBuilderAPI_Sewing, BRepBuilderAPI_MakeSolid
from OCC.Core.GC import GC_MakeArcOfCircle
from OCC.Core.Geom import Geom_BSplineCurve, Geom_BSplineSurface, Geom_Circle
from OCC.Core.gp import gp_Pnt, gp_Circ, gp_Dir, gp_Ax2
from OCC.Core.ShapeFix import ShapeFix_Shape
from OCC.Core.TColgp import TColgp_Array1OfPnt, TColgp_Array2OfPnt
from OCC.Core.TColStd import TColStd_Array1OfReal, TColStd_Array1OfInteger
from OCC.Core.TopAbs import TopAbs_VERTEX, TopAbs_FORWARD, TopAbs_REVERSED
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Display.SimpleGui import init_display

# Initialize the display
display, start_display, add_menu, add_function_to_menu = init_display()

# Initialize Speckle
from specklepy.api import operations
from specklepy.api.wrapper import StreamWrapper

if __name__ == "__main__":
    stream_url = "https://app.speckle.systems/projects/864c4d4027/models/9c0ec10379"
    wrapper = StreamWrapper(stream_url)

    transport = wrapper.get_transport()
 
    #Objects sent from Rhinoceros 3D to Speckle :
    
    #Is working:
    
    #Curves :
    #received = operations.receive("fa8b2bea472ea99eb074585802c144c1", transport) # point
    #received = operations.receive("4b6b20120c4270406e8cefb0e31d8e6e", transport) # line
    #received = operations.receive("c0efbf4617325abdb10c5d85f192fdad", transport) # polyline
    #received = operations.receive("c9132104319d7d09c251a9896de93060", transport) # circle
    #received = operations.receive("a65d3dec8951963906ff9c122b874675", transport) # arc
    #received = operations.receive("26d680179faff3c9be98f88aa5de71d3", transport) # curve
    
    #Planar faces:
    #received = operations.receive("348518420eaa2f0e1c6c0c6bd92d2b89", transport) # triangular face
    #received = operations.receive("4ba26e43e5b70463cdb060b36cc448d3", transport) # rectangular face
    #received = operations.receive("cdc9f429541627224c00610898c664d7", transport) # pentagonal face
    #received = operations.receive("390dc996c2567991b1f36004c20cba69", transport) # circular face
    #received = operations.receive("0bd349d32c8a9b00942709495e7b8dab", transport) # arched face
    #received = operations.receive("1e20a0b13e4e0843044b79d35231074b", transport) # curved face
    #received = operations.receive("7b9ef1e597899c804f833d17d917ae05", transport) # face with mix of edges types
    #received = operations.receive("658ef9b63021d1266573c00f527c2bdc", transport) # cylinder, only lower and upper faces
    
    #Planar faces with holes:
    #received = operations.receive("161c29e5346e8988ab87c00aa5477630", transport) # triangular face with triangular hole
    #received = operations.receive("1008040021ab18d29392598684ffe569", transport) # pentagonal face with pentagonal hole
    #received = operations.receive("90f988a827c1021abc3125f69e3c70b3", transport) # pentagonal face with circular hole
    #received = operations.receive("b4a7e732d4f03bea608b59e311f0bf52", transport) # pentagonal face with arched hole
    #received = operations.receive("972bd504c8bad2a8cc83b5a0147307c5", transport) # rectangular face with rectangular holes
    #received = operations.receive("397dfde2f1e10379f7db810a0e27644c", transport) # pentagonal face with multiple straight holes
    #received = operations.receive("eb5d50ae43a78dcecc4a84e52f179ecb", transport) # pentagonal face with multiple holes of each type
    #received = operations.receive("0298c70cbe7783aefd1a8d0ae3bd6a92", transport) # curved planar face with curved hole
    #received = operations.receive("2f4c57e6f1535a8edd0a0c8e6eb89d98", transport) # curved planar face with two curved holes
    
    #3D faces
    #received = operations.receive("3b320207576b80c0134fde287653806e", transport) # rectangular face deformed in 3D
    #received = operations.receive("9c6c57fc183435879178ea8b73ebf963", transport) # trimmed rectangular face deformed in 3D
    #received = operations.receive("93b7da1e9cd0c00101998e4fda51d800", transport) # triangular face deformed in 3D
    #received = operations.receive("42bb9190e8dc0c071898bb434e274f9d", transport) # dome-like shape = loft of arcs of circles
    #received = operations.receive("81539f5dcbf1b439c34684dc745aa1d2", transport) # portion of cylinder, without lower and upper faces, sent from grasshopper to control edges
    
    #3D faces with holes:
    #received = operations.receive("bc043113ca32744823c6c627f934469e", transport) # trimmed rectangular face deformed in 3D, with hole
    #received = operations.receive("c11c75b599c6066668481aa22d5c3719", transport) # curved face deformed in 3D, with curved hole
    
    #Complex BReps with multiple faces and holes
    #received = operations.receive("76bf73ff646a5833e7eb6145b035b44d", transport) # planar face with straight edges, extruded
    #received = operations.receive("794f4da8239920b851f820e77b457cc2", transport) # two planar triangular faces, one with a hole
    #received = operations.receive("7efc65e33c33f548e1c05ec425203164", transport) # pyramid = multiple faces
    #received = operations.receive("8b86058cc3d1f87ff8e47e1156e9a5e0", transport) # pyramid with one hole on one face
    #received = operations.receive("5369930079697d28c4568dc2d99b6d97", transport) # closed curved planar face, extruded
    received = operations.receive("ac4aae21998abfa560084adbe02fbd5e", transport) # curved face deformed in 3D, with curved hole, extruded    
    
    #Is not working:
    #received = operations.receive("de3d9777e53fac1b047ff019e594f63e", transport) # spherical triangular face
    #received = operations.receive("97686fd99a42b3f3deae4cf1a2c71fdb", transport) #cylinder, all faces
    #received = operations.receive("9216df6bd47121ddc75ee1b4abc87c5c", transport) #cylinder, without lower and upper faces
    #received = operations.receive("6a903e7c6afa9f29c91ba2647d83fc72", transport) #curved planar face with two holes, extruded
    
    
    #Objects sent from pyton-occ with s.py
    
    #Is working:
    #received = operations.receive("86699b789249e00e1a554a6d647d1f2e", transport) # one triangular and one rectangular planar faces
    #received = operations.receive("55111a41e4a3f962917f174f67b91001", transport) # one triangular and two rectangular planar faces
    #received = operations.receive("67d2a43908c1854b4b4e790cbb282d78", transport) # two triangular and two rectangular planar faces
    #received = operations.receive("f96a51ac8d3c0bfe03193e29b25ed653", transport) # triangular face, extruded
    #received = operations.receive("066f7f70e2565c7350d5cff4f44ef247", transport) # one triangular and one rectangular planar faces, one with a hole

    
    #Is not working:
    #received = operations.receive("7609c3333acbf65cbb347ab37f0cc8f8", transport) #two triangular and two rectangular planar faces, one with a hole
    
    
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
    s_start = element.start
    s_end = element.end
    o_start = gp_Pnt(s_start.x, s_start.y, s_start.z)
    o_end = gp_Pnt(s_end.x, s_end.y, s_end.z)
    o_line_edge = BRepBuilderAPI_MakeEdge(o_start, o_end).Edge()
    return o_line_edge

# Polyline
def polyline_from_speckle_to_occ(element):
    s_polyline = element
    o_points = [gp_Pnt(s_polyline.value[i], s_polyline.value[i+1], s_polyline.value[i+2])
                for i in range(0, len(s_polyline.value), 3)]
    wire_builder = BRepBuilderAPI_MakeWire()
    for i in range(len(o_points) - 1):
        edge = BRepBuilderAPI_MakeEdge(o_points[i], o_points[i+1]).Edge()
        wire_builder.Add(edge)
    if s_polyline.closed and len(o_points) > 2:
        edge = BRepBuilderAPI_MakeEdge(o_points[-1], o_points[0]).Edge()
        wire_builder.Add(edge)
    o_polyline = wire_builder.Wire()
    return o_polyline

# Circle
def circle_from_speckle_to_occ(element):
    s_radius = element.radius
    s_plane = element.plane
    s_origin = s_plane.origin
    s_normal = s_plane.normal
    o_center = gp_Pnt(s_origin.x, s_origin.y, s_origin.z)
    o_normal = gp_Dir(s_normal.x, s_normal.y, s_normal.z)
    o_radius = s_radius
    o_circle = Geom_Circle(gp_Circ(gp_Ax2(o_center, o_normal), o_radius))
    o_circle_edge = BRepBuilderAPI_MakeEdge(o_circle).Edge()
    return o_circle_edge

# Arc
def arc_from_speckle_to_occ(element):
    s_startPoint = element.startPoint
    s_midPoint = element.midPoint
    s_endPoint = element.endPoint
    o_start_pnt = gp_Pnt(s_startPoint.x, s_startPoint.y, s_startPoint.z)
    o_mid_pnt = gp_Pnt(s_midPoint.x, s_midPoint.y, s_midPoint.z)
    o_end_pnt = gp_Pnt(s_endPoint.x, s_endPoint.y, s_endPoint.z)
    o_arc_maker = GC_MakeArcOfCircle(o_start_pnt, o_mid_pnt, o_end_pnt)
    o_arc = o_arc_maker.Value()
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
    
    # Define knots
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
    for i in range(1, len(o_knots_list) + 1):
        o_knots.SetValue(i, o_knots_list[i - 1])
    
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
    for i in range(1, len(o_multiplicities_list) + 1):
        o_multiplicities.SetValue(i, o_multiplicities_list[i - 1])
    
    # Define other parameters
    o_degree = s_degree
    #o_periodic = s_periodic
    # WIP: there is a mismatch between occ-periodic curves and knots count: currently all curves are set to non-periodic
    o_periodic = False
    o_check_rational = s_rational
    
    # Create curve
    o_curve = Geom_BSplineCurve(
        o_poles, o_weights, o_knots, o_multiplicities, o_degree, o_periodic, o_check_rational
    )
    o_curve_edge = BRepBuilderAPI_MakeEdge(o_curve).Edge()
    return o_curve_edge

# Receive elements
for element in all_elements:
    
    if element.speckle_type == "Objects.Geometry.Point":
        o_point = point_from_speckle_to_occ(element)
        display.DisplayShape(o_point, update=True)
    
    elif element.speckle_type == "Objects.Geometry.Line":
        o_line = line_from_speckle_to_occ(element)
        display.DisplayShape(o_line, update=True)
        
    elif element.speckle_type == "Objects.Geometry.Polyline":
        o_polyline = polyline_from_speckle_to_occ(element)
        display.DisplayShape(o_polyline, update=True)
    
    elif element.speckle_type == "Objects.Geometry.Circle":
        o_circle = circle_from_speckle_to_occ(element)
        display.DisplayShape(o_circle, update=True)
        
    elif element.speckle_type == "Objects.Geometry.Arc":
        o_arc = arc_from_speckle_to_occ(element)
        display.DisplayShape(o_arc, update=True)
    
    elif element.speckle_type == "Objects.Geometry.Curve":
        o_curve = curve_from_speckle_to_occ(element)
        display.DisplayShape(o_curve, update=True)
        
    elif element.speckle_type == "Objects.Geometry.Brep":
        
        s_brep = element
        
        s_surfaces = s_brep.Surfaces
        s_curve3D = s_brep.Curve3D
        s_curve2D = s_brep.Curve2D
        s_loops = s_brep.Loops
        s_faces = s_brep.Faces
        s_trims = s_brep.Trims
		
        o_Geom_Surfaces = []
        
        for surface in s_surfaces:
            s_degreeU = surface.degreeU
            s_degreeV = surface.degreeV
            s_pointData = surface.pointData
            s_countU = surface.countU
            s_countV = surface.countV
            s_knotsU = surface.knotsU
            s_knotsV = surface.knotsV
            
            o_poles = TColgp_Array2OfPnt(1, s_countU, 1, s_countV)
            index = 0
            for u in range(1, s_countU + 1):
                for v in range(1, s_countV + 1):
                    x = s_pointData[index]
                    y = s_pointData[index + 1]
                    z = s_pointData[index + 2]
                    o_poles.SetValue(u, v, gp_Pnt(x, y, z))
                    index += 4 # the fourth coordinate is the weight, skip
            
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
                mults.SetValue(1, degree + 1)
                mults.SetValue(num_unique_knots, degree + 1)
                return knots, mults
            
            o_knotsU, o_multsU = receive_knots_and_mults(s_knotsU, s_degreeU)
            o_knotsV, o_multsV = receive_knots_and_mults(s_knotsV, s_degreeV)
            
            o_uPeriodic = False
            o_vPeriodic = False
            o_degreeU = s_degreeU
            o_degreeV = s_degreeV
                        
            o_b_spline_surface = Geom_BSplineSurface(
                o_poles, o_knotsU, o_knotsV, o_multsU, o_multsV, o_degreeU, o_degreeV, o_uPeriodic, o_vPeriodic
            )
            o_Geom_Surfaces.append(o_b_spline_surface)
            
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
 
        if len(s_faces) > 1:
            sewing = BRepBuilderAPI_Sewing()
            
        for k, face in enumerate(s_faces):
            SurfaceIndex = face.SurfaceIndex
            OuterLoopIndex = face.OuterLoopIndex
            LoopIndices = face.LoopIndices         
            loops = []
            for j, loop in enumerate(s_loops):
                if j == OuterLoopIndex:
                    outer_loop = loop
                elif j in LoopIndices:
                    loops.append(loop)
            loops.insert(0, outer_loop)
            for i, loop in enumerate(loops):
                TrimIndices = loop.TrimIndices
                o_wire_maker = BRepBuilderAPI_MakeWire()
                trims = [s_trims[i] for i in TrimIndices]
                builder = BRep_Builder()
                for trim in trims:
                    edge = o_TopoDS_Edges[trim.EdgeIndex]
                    if trim.IsReversed:
                        edge.Orientation(TopAbs_REVERSED)
                    else:
                        edge.Orientation(TopAbs_FORWARD)
                    o_wire_maker.Add(edge)
                    vertex_explorer = TopExp_Explorer(edge, TopAbs_VERTEX)
                    verts = []
                    while vertex_explorer.More():
                        v = vertex_explorer.Current()
                        pnt = BRep_Tool.Pnt(v)
                        verts.append((pnt.X(), pnt.Y(), pnt.Z()))
                        vertex_explorer.Next()
                o_wire = o_wire_maker.Wire()
                if i == 0:
                    print(SurfaceIndex)
                    o_trimmed_face_maker = BRepBuilderAPI_MakeFace(o_Geom_Surfaces[SurfaceIndex], o_wire, True)
                    o_trimmed_face = o_trimmed_face_maker.Face()
                else:
                    o_trimmed_face_maker = BRepBuilderAPI_MakeFace(o_trimmed_face, o_wire)
                    o_trimmed_face = o_trimmed_face_maker.Face()

            fixer = ShapeFix_Shape(o_trimmed_face)
            fixer.Perform()
            o_fixed_face = fixer.Shape()
            
            if len(s_faces) == 1:
                display.DisplayShape(o_fixed_face, update=True)

            elif len(s_faces) > 1:
                sewing.Add(o_fixed_face)

        if len(s_faces) > 1:
            sewing.Perform()
            shell = sewing.SewedShape()
            if s_brep.IsClosed is False:
                display.DisplayShape(shell, update=True)
            else:
                solid_maker = BRepBuilderAPI_MakeSolid(shell)
                solid = solid_maker.Solid()
                display.DisplayShape(solid, update=True)
                
start_display()