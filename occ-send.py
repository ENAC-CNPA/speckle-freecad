from OCC.Display.SimpleGui import init_display
from OCC.Core.BRepTools import breptools_Read
from OCC.Core.TopoDS import TopoDS_Shape, topods, TopoDS_Face
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopExp import topexp
from OCC.Core.BRep import BRep_Builder
from OCC.Core.Geom import Geom_BSplineCurve, Geom_RectangularTrimmedSurface
from OCC.Core.BRep import BRep_Tool
from OCC.Core.TopAbs import TopAbs_EDGE, TopAbs_REVERSED, TopAbs_FORWARD
from OCC.Core.Geom import Geom_Line, Geom_BSplineSurface, Geom_Plane
from OCC.Core.BRepTools import breptools, breptools_OuterWire
from OCC.Core.TopTools import TopTools_IndexedMapOfShape
from OCC.Core.TopTools import TopTools_ShapeMapHasher
from OCC.Core.Geom import Geom_BSplineSurface
from OCC.Core.gp import gp_Pln, gp_Pnt, gp_Circ, gp_Ax2, gp_Dir
from OCC.Core.GeomAdaptor import GeomAdaptor_Surface
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeVertex, BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeShell, BRepBuilderAPI_Sewing, BRepBuilderAPI_MakeSolid
from OCC.Core.GeomConvert import geomconvert
from OCC.Core.TColgp import TColgp_Array2OfPnt
from OCC.Core.TColStd import TColStd_Array1OfReal, TColStd_Array1OfInteger
from OCC.Core.Geom2d import Geom2d_Line
from OCC.Core.gp import gp_Pnt2d
from OCC.Core.gp import gp_Pln, gp_Ax3
from OCC.Core.GeomAPI import geomapi
from OCC.Core.TopAbs import (
    TopAbs_VERTEX,
    TopAbs_EDGE,
    TopAbs_WIRE,
    TopAbs_FACE,
    TopAbs_SHELL,
    TopAbs_SOLID,
    TopAbs_COMPSOLID,
    TopAbs_COMPOUND,
    TopAbs_ShapeEnum
)
display, start_display, add_menu, add_function_to_menu = init_display()

#import Speckle libraries
from typing import List
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_default_account
from specklepy.objects import Base
from specklepy.objects.geometry import (
     Box, Brep, BrepEdge, BrepFace, BrepLoop, BrepLoopType, BrepTrim, BrepTrimType, Circle, Curve, Interval, Line, Mesh, Plane, Point, Polyline, Surface, Vector
)
from specklepy.objects.other import Collection

#set links to Speckle
client = SpeckleClient(host="https://app.speckle.systems/")
account = get_default_account()
client.authenticate_with_account(account)
#copy paste your stream id here :
stream_id = "864c4d4027"

#set container of all elements
data = Collection()
data.elements = []


# Functions
def vertex_from_occ_to_speckle(vertex):
    o_point = BRep_Tool.Pnt(vertex)
    s_Vertex = Point(x = o_point.Y(), y = o_point.Y(), z = o_point.Z())
    return s_Vertex
    
def curve_from_occ_to_speckle(edge):
    curve, u_min, u_max = BRep_Tool.Curve(edge)
    
    if curve.DynamicType().Name() == "Geom_Line":
        
        # Get 3D points
        p_start = curve.Value(u_min)
        p_end = curve.Value(u_max)

        # Convert to Speckle Points
        sp_start = Point(x=p_start.X(), y=p_start.Y(), z=p_start.Z())
        sp_end = Point(x=p_end.X(), y=p_end.Y(), z=p_end.Z())

        # Create Speckle Line
        s_curve = Line(
            start=sp_start,
            end=sp_end,
            domain=Interval(start=u_min, end=u_max),
            length=p_start.Distance(p_end),
        )
        
    elif curve.DynamicType().Name() == "Geom_BSplineCurve":
        # Downcast to actual BSplineCurve
        bspline = Geom_BSplineCurve.DownCast(curve)
        if bspline is None:
            raise TypeError("Expected Geom_BSplineCurve, got something else.")

        # Extract properties
        degree = bspline.Degree()
        is_periodic = bspline.IsPeriodic()
        is_rational = bspline.IsRational()
        is_closed = bspline.IsClosed()
        u1 = bspline.FirstParameter()
        u2 = bspline.LastParameter()
        domain = Interval(start=u1, end=u2)

        # Extract poles
        num_poles = bspline.NbPoles()
        points = []
        for i in range(1, num_poles + 1):
            pt = bspline.Pole(i)
            points.extend([pt.X(), pt.Y(), pt.Z()])

        # Extract weights
        if is_rational:
            weights = [bspline.Weight(i) for i in range(1, num_poles + 1)]
        else:
            weights = [1] * num_poles

        # Extract knots and multiplicities
        knots = []
        for i in range(1, bspline.NbKnots() + 1):
            knot_val = bspline.Knot(i)
            mult = bspline.Multiplicity(i)
            knots.extend([knot_val] * mult)

        # Optional display polyline
        display_points = []
        num_segments = 50
        for i in range(num_segments + 1):
            u = u1 + (u2 - u1) * i / num_segments
            p = bspline.Value(u)
            display_points.extend([p.X(), p.Y(), p.Z()])
        polyline = Polyline(value=display_points)

        # Create Speckle Curve
        s_curve = Curve(
            degree=degree,
            periodic=is_periodic,
            rational=is_rational,
            closed=is_closed,
            domain=domain,
            points=points,
            weights=weights,
            knots=knots,
            displayValue=polyline,
        )
    return(s_curve)

def edge_from_occ_to_speckle(edge, Curve3dIndex, vertices_map):
    Curve3dIndex = Curve3dIndex - 1 #index in occ starts from 1, while index in speckle start from 0
    StartVertex = topods.Vertex(topexp.FirstVertex(edge))
    EndVertex = topods.Vertex(topexp.LastVertex(edge))
    StartIndex = vertices_map.FindIndex(StartVertex) - 1
    EndIndex = vertices_map.FindIndex(EndVertex) - 1
    curve, u_min, u_max = BRep_Tool.Curve(edge)
    s_BrepEdge = BrepEdge(
        Curve3dIndex = Curve3dIndex,
        TrimIndices = [],
        StartIndex = StartIndex,
        EndIndex = EndIndex,
        ProxyCurveIsReversed = False,
        Domain = Interval(start = u_min, end = u_max)
    )
    return s_BrepEdge

def pcurve_as_independant_edge(edge, face):
    pcurve, u_min, u_max = BRep_Tool.CurveOnSurface(edge, face)
    xy_plane = gp_Pln(gp_Ax3())
    pcurve3d = geomapi.To3d(pcurve, xy_plane)
    make_edge = BRepBuilderAPI_MakeEdge(pcurve3d)
    pcurve3d_as_edge = make_edge.Edge()
    return pcurve3d_as_edge

def surface_from_occ_to_speckle(o_b_spline_surface: Geom_BSplineSurface):
    # Extracting poles (control points) from the OCC surface
    o_poles = o_b_spline_surface.Poles()
    
    s_countU = o_poles.NbColumns()  # Number of U control points
    s_countV = o_poles.NbRows()  # Number of V control points
    
    point_data = []
    for u in range(1, s_countU+1):
        for v in range(1, s_countV+1):
            pole = o_poles.Value(u, v)
            point_data.extend([pole.X(), pole.Y(), pole.Z(), 1.0])  # Including weights (assumed as 1)

    # Extracting knots (and multiplicities) for U and V directions
    def extract_knots_and_multiplicities(knots_array: TColStd_Array1OfReal):
        knots = []
        multiplicities = []
        last_knot = None
        current_multiplicity = 0
        for i in range(1, knots_array.Length() + 1):
            knot = knots_array.Value(i)
            if last_knot != knot:
                if last_knot is not None:
                    multiplicities.append(current_multiplicity)
                knots.append(knot)
                current_multiplicity = 1
            else:
                current_multiplicity += 1
            last_knot = knot
        multiplicities.append(current_multiplicity)  # Last knot multiplicity
        return knots, multiplicities
    
    knots_u, mults_u = extract_knots_and_multiplicities(o_b_spline_surface.UKnots())
    knots_v, mults_v = extract_knots_and_multiplicities(o_b_spline_surface.VKnots())

    # Extracting other parameters
    degree_u = o_b_spline_surface.UDegree()
    degree_v = o_b_spline_surface.VDegree()
    closed_u = o_b_spline_surface.IsUClosed()
    closed_v = o_b_spline_surface.IsVClosed()
    u_min, u_max, v_min, v_max = o_b_spline_surface.Bounds()
    
    # Constructing the Speckle Surface object
    s_surface = Surface(
        degreeU = degree_u,
        degreeV = degree_v,
        countU = s_countU,
        countV = s_countV,
        rational = False,
        closedU = closed_u,
        closedV = closed_v,
        domainU = Interval(start = u_min, end = u_max),
	    domainV = Interval(start = v_min, end = v_max),
        pointData = point_data,
        knotsU = knots_u,
        knotsV = knots_v
    )
    return s_surface

# Convert the BREP
# Optional: name mapping for convenience
shape_type_names = {
    TopAbs_VERTEX: "VERTEX",
    TopAbs_EDGE: "EDGE",
    TopAbs_WIRE: "WIRE",
    TopAbs_FACE: "FACE",
    TopAbs_SHELL: "SHELL",
    TopAbs_SOLID: "SOLID",
    TopAbs_COMPSOLID: "COMPSOLID",
    TopAbs_COMPOUND: "COMPOUND"
}

# Load the brep file
shape = TopoDS_Shape()
builder = BRep_Builder()
#Copy paste the local path to your brep file here:
breptools.Read(shape, "./breps/model.brep", builder)

has_face = False

# Loop through all shape types and count them
for shape_type in shape_type_names:
    explorer = TopExp_Explorer(shape, shape_type)
    count = 0
    while explorer.More():
        count += 1
        explorer.Next()
    if count > 0:
        if shape_type == TopAbs_FACE:
            has_face = True
            
# After the loop, you can use:
if has_face: #handle as BREP
    
    s_Surfaces = []
    s_Curve3D = []
    s_Curve2D = []
    s_Vertices = []
    s_Edges = []
    s_Loops = []
    s_Faces = []
    s_Trims = []
    s_IsClosed = True #still to get from OCC
    s_Orientation = 1 #still to get from OCC
    
    # Create Speckle Vertices
    vertex_explorer = TopExp_Explorer(shape, TopAbs_VERTEX)
    vertices_map = TopTools_IndexedMapOfShape()    
    while vertex_explorer.More():
        o_vertex = topods.Vertex(vertex_explorer.Current())
        if not vertices_map.Contains(o_vertex):
            vertices_map.Add(o_vertex)
            s_Vertex = vertex_from_occ_to_speckle(o_vertex)
            s_Vertices.append(s_Vertex)
        vertex_explorer.Next()
    
    # Create Speckle Curve3D and BrepEdges
    edge_explorer = TopExp_Explorer(shape, TopAbs_EDGE)
    edges_map = TopTools_IndexedMapOfShape()
    while edge_explorer.More():
        o_edge = topods.Edge(edge_explorer.Current())
        if not edges_map.Contains(o_edge):
            edges_map.Add(o_edge)
            #Curve3D
            s_Curve3D_item = curve_from_occ_to_speckle(o_edge)
            s_Curve3D.append(s_Curve3D_item)
            #BrepEdge
            Curve3dIndex = edges_map.FindIndex(o_edge)
            s_Edge = edge_from_occ_to_speckle(o_edge, Curve3dIndex, vertices_map)
            s_Edges.append(s_Edge)
        edge_explorer.Next()
        
    # Create Speckle Loop map
    wire_explorer = TopExp_Explorer(shape, TopAbs_WIRE)
    wires_map = TopTools_IndexedMapOfShape()
    while wire_explorer.More():
        o_wire = topods.Wire(wire_explorer.Current())
        if not wires_map.Contains(o_wire):
            wires_map.Add(o_wire)
        wire_explorer.Next()
           
    # Create Speckle Surfaces, Faces, Loops, Trims, and Curve2D     
    face_explorer = TopExp_Explorer(shape, TopAbs_FACE)
    faces_map = TopTools_IndexedMapOfShape()
    pcurves_map = TopTools_IndexedMapOfShape() 
    while face_explorer.More():
        o_face = topods.Face(face_explorer.Current())
        if not faces_map.Contains(o_face):
            faces_map.Add(o_face)
            FaceIndex = faces_map.FindIndex(o_face) - 1
            
            # Surfaces
            o_surface = BRep_Tool.Surface(o_face)
            # Convert each surface to bspline surface
            if not isinstance(o_surface, Geom_BSplineSurface):
                u1, u2, v1, v2 = breptools.UVBounds(o_face)
                trimmed_surface = Geom_RectangularTrimmedSurface(o_surface, u1, u2, v1, v2)
                o_surface = geomconvert.SurfaceToBSplineSurface(trimmed_surface)
            s_Surface = surface_from_occ_to_speckle(o_surface)
            s_Surfaces.append(s_Surface)
            
            # Loops
            face_wire_explorer = TopExp_Explorer(o_face, TopAbs_WIRE)
            face_wires_map = TopTools_IndexedMapOfShape()
            LoopIndices = []
            while face_wire_explorer.More():
                o_face_wire = topods.Wire(face_wire_explorer.Current())
                if not face_wires_map.Contains(o_face_wire):
                    face_wires_map.Add(o_face_wire)
                    LoopIndex = wires_map.FindIndex(o_face_wire) - 1
                    LoopIndices.append(LoopIndex)
                    if o_face_wire.Orientation() == TopAbs_FORWARD:
                        OuterLoopIndex = LoopIndex
                        
                    # Curve2D & Trims
                    o_face_wire_edge_explorer = TopExp_Explorer(o_face_wire, TopAbs_EDGE)
                    TrimIndices = []
                    while o_face_wire_edge_explorer.More():
                        o_face_wire_edge = topods.Edge(o_face_wire_edge_explorer.Current())
                        
                        # Curve2D
                        pcurve_as_edge = pcurve_as_independant_edge(o_face_wire_edge, o_face)
                        pcurves_map.Add(pcurve_as_edge)
                        s_Curve2D_item = curve_from_occ_to_speckle(pcurve_as_edge)
                        s_Curve2D.append(s_Curve2D_item)
                            
                        # Trims
                        isReversed = o_face_wire_edge.Orientation() == TopAbs_REVERSED
                        
                        if isReversed == False:
                            StartVertex = topods.Vertex(topexp.FirstVertex(o_face_wire_edge))
                            EndVertex = topods.Vertex(topexp.LastVertex(o_face_wire_edge))
                        else:
                            StartVertex = topods.Vertex(topexp.LastVertex(o_face_wire_edge))
                            EndVertex = topods.Vertex(topexp.FirstVertex(o_face_wire_edge))
                        StartIndex = vertices_map.FindIndex(StartVertex) - 1
                        EndIndex = vertices_map.FindIndex(EndVertex) - 1
                                      
                        EdgeIndex = edges_map.FindIndex(o_face_wire_edge) - 1
                        CurveIndex = pcurves_map.FindIndex(pcurve_as_edge) - 1
                        s_BrepTrim = BrepTrim(
                            EdgeIndex = EdgeIndex,
                            StartIndex = StartIndex,
                            EndIndex = EndIndex,
                            FaceIndex = FaceIndex,
                            LoopIndex = LoopIndex,
                            CurveIndex = CurveIndex,
                            TrimType = BrepTrimType.Boundary,
                            IsReversed = isReversed   
                        )
                        s_Trims.append(s_BrepTrim)
                        
                        TrimIndex = CurveIndex
                        TrimIndices.append(TrimIndex)
                        s_Edges[EdgeIndex].TrimIndices.append(TrimIndex)
                        
                        o_face_wire_edge_explorer.Next()
                        
                    s_Loop = BrepLoop(
                        FaceIndex = FaceIndex,
                        TrimIndices = TrimIndices,
                        Type = 0
                    )
                    s_Loops.append(s_Loop)
                
                face_wire_explorer.Next()

            s_BrepFace = BrepFace(
                SurfaceIndex = FaceIndex,
                OuterLoopIndex = OuterLoopIndex,
                OrientationReversed = False,
                LoopIndices = LoopIndices
            )
            s_Faces.append(s_BrepFace)
            
        face_explorer.Next()
        
    print("Surfaces:", len(s_Surfaces))
    for i,s in enumerate(s_Surfaces):
        print("Surface", i, ": degreeU:", s.degreeU, "degreeV:", s.degreeV, "rational:", s.rational, "area:", s.area, "pointData:", s.pointData, "countU", s.countU, "countV", s.countV, "closedU:", s.closedU, "closedV:", s.closedV, "domainU:", s.domainU, "domainV:", s.domainV, "knotsU:", s.knotsU, "knotsV:", s.knotsV)
    print("Curve3D:", len(s_Curve3D))
    print("Curve2D:", len(s_Curve2D))
    print("Vertices:", len(s_Vertices))
    print("Edges:", len(s_Edges))
    for i,e in enumerate(s_Edges):
        print("Edge", i, ": Curve3dIndex =", e.Curve3dIndex, "TrimIndices =", e.TrimIndices, "StartIndex =", e.StartIndex, "EndIndex =", e.EndIndex)
    print("Loops nombre:", len(s_Loops))
    for i,l in enumerate(s_Loops):
        print("Loop", i, ": FaceIndex =", l.FaceIndex, "TrimIndices =", l.TrimIndices)
    print("Faces nombre:", len(s_Faces))
    for i,f in enumerate(s_Faces):
        print("Face", i, ": SurfaceIndex =", f.SurfaceIndex, "OuterLoopIndex =", f.OuterLoopIndex, "LoopIndices =", f.LoopIndices)
    print("Trims:", len(s_Trims))
    for i,t in enumerate(s_Trims):
        print("Trim", i, "EdgeIndex =", t.EdgeIndex, "StartIndex =", t.StartIndex, "EndIndex =", t.EndIndex, "FaceIndex =", t.FaceIndex, "LoopIndex =", t.LoopIndex, "CurveIndex =", t.CurveIndex, "IsReversed =", t.IsReversed)

    s_Brep = Brep(
        Surfaces = s_Surfaces,
        Curve3D = s_Curve3D,
        Curve2D = s_Curve2D,
        Vertices = s_Vertices,
        Edges = s_Edges,
        Loops = s_Loops,
        Faces = s_Faces,
        Trims = s_Trims,
        IsClosed = s_IsClosed,
        Orientation = s_Orientation
    )
    
    #add to data to be sent
    data.elements.append(s_Brep)
        
else:
    # handle as curve
    edge_explorer = TopExp_Explorer(shape, TopAbs_EDGE)
    while edge_explorer.More():
        edge = topods.Edge(edge_explorer.Current())
        s_curve = curve_from_occ_to_speckle(edge)
        #add to data to be sent
        data.elements.append(s_curve)
        edge_explorer.Next()

#send to Speckle
from specklepy.transports.server import ServerTransport
from specklepy.api import operations
transport = ServerTransport(client=client, stream_id=stream_id)
hash = operations.send(base=data, transports=[transport])
commid_id = client.commit.create(
    stream_id=stream_id, 
    object_id=hash, 
    message="these are elements from OCC",
    )
print("sent")


display.DisplayShape(shape, update=True)
start_display()