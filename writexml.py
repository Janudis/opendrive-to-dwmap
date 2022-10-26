from xml.etree import ElementTree
from postprocessing import*
from utilities import*
from parsexodr import read_junctions
import math


# read all data from the csvs
boundary_properties = pd.read_csv("boundary_properties.csv")
center_lanes = pd.read_csv("center_lanes.csv")
coordinates = pd.read_csv("coordinates.csv")
lane_boundaries = pd.read_csv("lane_boundaries.csv")
lane_properties = pd.read_csv("lane_properties.csv")
left_lanes = pd.read_csv("left_lanes.csv")
objects = pd.read_csv("objects.csv")
predecessors = pd.read_csv("predecessors.csv")
right_lanes = pd.read_csv("right_lanes.csv")
speeds = pd.read_csv("speeds.csv")
successors = pd.read_csv("successors.csv")

successorsLanes = pd.read_csv("successorsLanes.csv")
predecessorsLanes = pd.read_csv("predecessorsLanes.csv")
geo = pd.read_csv("geo.csv")
junctions = read_junctions('final2.xodr')

road_ids = get_road_ids("road_ids.csv")
road_types = get_road_types("types.txt")

dwmaps = ElementTree.Element("dwMap", version="5")
roadSegments = ElementTree.SubElement(dwmaps,"roadSegments")

border_with_id = pd.DataFrame(columns=['laneId', 'id0', 'id1', 'id2', 'id3'])
for i in road_ids:
    next_roads=[]
    previous_roads=[]
    roadSegment = ElementTree.SubElement(roadSegments, "roadSegment")
    # dwmaps/roadSegments/roadSegment
    roadSegmentId = ElementTree.SubElement(roadSegment, "roadSegmentId")
    # dwmpas/roadSegments/roadSegment/roadSegmentId
    ElementTree.SubElement(roadSegmentId, "id0").text = str(i)
    ElementTree.SubElement(roadSegmentId, "id1").text = "0"
    ElementTree.SubElement(roadSegmentId, "id2").text = "0"

    # dwmaps/roadSegments/roadSegment
    # ElementTree.SubElement(roadSegment, "type").text = str(translate_road_type(road_types[str(i)]))
    ElementTree.SubElement(roadSegment, "type").text = "0"
    origin = road_origin(i, left_lanes, right_lanes, lane_properties, coordinates)
    ElementTree.SubElement(roadSegment, "origin").text = point_str(origin[0], origin[1], origin[2])
    ElementTree.SubElement(roadSegment, "hdCompliance").text = "1"

    laneGroups = ElementTree.SubElement(roadSegment, "laneGroups")
    # dwmaps/roadSegments/roadSegment/laneGroups
    laneGroup = ElementTree.SubElement(laneGroups, "laneGroup")

    op_lane_id = []
    li = 0
    df_lanes = get_lanes(i, left_lanes, right_lanes)
    for l in range(len(df_lanes)):
        # dwmaps/roadSegments/roadSegment/laneGroups/laneGroup
        laneGroup_member = ElementTree.SubElement(laneGroup, "member")
        # dwmaps/roadSegments/roadSegment/laneGroups/laneGroup/member
        member_laneId = ElementTree.SubElement(laneGroup_member, "laneId")

        li = df_lanes['Id'].loc[l]
        op_lane_id.append(df_lanes['laneId'].loc[l])
        id0, id1, id2, id3 = set_id(i, li, 'lane')

        # dwmaps/roadSegments/roadSegment/laneGroups/laneGroup/member/laneId
        ElementTree.SubElement(member_laneId, "id0").text = str(id0)
        ElementTree.SubElement(member_laneId, "id1").text = str(id1)
        ElementTree.SubElement(member_laneId, "id2").text = str(id2)
        ElementTree.SubElement(member_laneId, "id3").text = str(id3)

        # dwmaps/roadSegments/roadSegment/laneGroups/laneGroup/member
        num = num_lanes(i, lane_boundaries)
        if(num > 1):
            ElementTree.SubElement(laneGroup_member, "traversability").text = str(id2)
    
    dividers = get_dividers(op_lane_id, lane_properties)
    if dividers != None:
    # dwmaps/roadSegments/roadSegment
        laneDividerGroups = ElementTree.SubElement(roadSegment, "laneDividerGroups")
        for d in dividers:
            # dwmaps/roadSegments/roadSegment/laneDividerGroups
            laneDividerGroup = ElementTree.SubElement(laneDividerGroups, "laneDividerGroup")
    
            # dwmaps/roadSegments/roadSegment/laneDividerGroups/laneDividerGroup
            laneDividerGroupId = ElementTree.SubElement(laneDividerGroup, "laneDividerGroupId")
            did0, did1, did2, did3 = set_id(i, li, 'lanedivider')
            border_with_id = save_ids(border_with_id, d, did0, did1, did2, did3)
    
            # dwmaps/roadSegments/roadSegment/laneDividerGroups/laneDividerGroup/laneDividerGroupId
            ElementTree.SubElement(laneDividerGroupId, "id0").text = str(did0)
            ElementTree.SubElement(laneDividerGroupId, "id1").text = str(did1)
            ElementTree.SubElement(laneDividerGroupId, "id2").text = str(did2)
            ElementTree.SubElement(laneDividerGroupId, "id3").text = str(did3)
            # dwmaps/roadSegments/roadSegment/laneDividerGroups/laneDividerGroup
            laneDividers = ElementTree.SubElement(laneDividerGroup, "laneDividers")
    
            # dwmaps/roadSegments/roadSegment/laneDividerGroups/laneDividerGrouplaneDividers
            laneDivider = ElementTree.SubElement(laneDividers, "laneDivider")
    
            # dwmaps/roadSegments/roadSegment/laneDividerGroups/laneDividerGroup/laneDividers/laneDivider
            ElementTree.SubElement(laneDivider, "type").text = "0"
            ElementTree.SubElement(laneDivider, "material").text = "0"
            ElementTree.SubElement(laneDivider, "color").text = "0"
            laneDivider_absGeometry = ElementTree.SubElement(laneDivider, "absGeometry")
            geopoints = get_geopoints(d, coordinates)
            for gp in range(len(geopoints)):
                ElementTree.SubElement(laneDivider_absGeometry, "geoPoint").text = point_str(geopoints['y'].loc[gp], geopoints['x'].loc[gp], geopoints['z'].loc[gp])
    
            # dwmaps/roadSegments/roadSegment/laneDividerGroups/laneDividerGroup/laneDividers/laneDivider
            ld_geometry = ElementTree.SubElement(laneDivider, "geometry")
            for gp in range(len(geopoints)):
                x, y, z = transform_wgs84_to_local(geopoints['y'].loc[gp], geopoints['x'].loc[gp], geopoints['z'].loc[gp],origin[0], origin[1], origin[2])
                ElementTree.SubElement(ld_geometry, "point").text = point_str(x, y, z)

    lanes = ElementTree.SubElement(roadSegment, "lanes")

    for l in range(len(df_lanes)):
        # dwmaps/roadSegments/roadSegment

        # dwmaps/roadSegments/roadSegment/lanes
        lane = ElementTree.SubElement(lanes, "lane")

        li = df_lanes['Id'].loc[l]
        id0, id1, id2, id3 = set_id(i, li, 'lane')

        # dwmaps/roadSegments/roadSegment/lanes/lane
        laneId = ElementTree.SubElement(lane, "laneId")

        # dwmaps/roadSegments/roadSegment/lanes/lane/laneId
        ElementTree.SubElement(laneId, "id0").text = str(id0)
        ElementTree.SubElement(laneId, "id1").text = str(id1)
        ElementTree.SubElement(laneId, "id2").text = str(id2)
        ElementTree.SubElement(laneId, "id3").text = str(id3)

        get_speed_limit(l, df_lanes)
        # dwmaps/roadSegments/roadSegment/lanes/lane
        ElementTree.SubElement(lane, "type").text = str(get_lane_type(l, df_lanes))
        ElementTree.SubElement(lane, "drivingDirection").text = str(get_lane_driving_dir(l, df_lanes))
        ElementTree.SubElement(lane, "speedLimit").text = str(get_speed_limit(l, df_lanes))
        
        op_lane = df_lanes['laneId'].loc[l]
        lgeopoints = get_geopoints(op_lane, coordinates)
        lane_absGeometry = ElementTree.SubElement(lane, "absGeometry")
        for gp in range(len(lgeopoints)):
            ElementTree.SubElement(lane_absGeometry, "geoPoint").text = point_str(lgeopoints['y'].loc[gp], lgeopoints['x'].loc[gp], lgeopoints['z'].loc[gp])

        lane_geometry = ElementTree.SubElement(lane, "geometry")
        
        for gp in range(len(lgeopoints)):
            x, y, z = transform_wgs84_to_local(lgeopoints['y'].loc[gp], lgeopoints['x'].loc[gp], lgeopoints['z'].loc[gp],origin[0], origin[1], origin[2])
            ElementTree.SubElement(lane_geometry, "point").text = point_str(x, y, z)

        bid = find_boundary_id(op_lane, lane_properties, border_with_id, 'right')
        if bid == None:
            continue
        else:

            laneDividerGroupRight = ElementTree.SubElement(lane, "laneDividerGroupRight")
            
            l_laneDividerGroupIdR = ElementTree.SubElement(laneDividerGroupRight, "laneDividerGroupId")

            ElementTree.SubElement(l_laneDividerGroupIdR, "id0").text = str(bid[0])
            ElementTree.SubElement(l_laneDividerGroupIdR, "id1").text = str(bid[1])
            ElementTree.SubElement(l_laneDividerGroupIdR, "id2").text = str(bid[2])
            ElementTree.SubElement(l_laneDividerGroupIdR, "id3").text = str(bid[3])

        bid = find_boundary_id(op_lane, lane_properties, border_with_id, 'left')
        if bid ==None:
            continue
        else:
            laneDividerGroupLeft = ElementTree.SubElement(lane, "laneDividerGroupLeft")

            l_laneDividerGroupIdL = ElementTree.SubElement(laneDividerGroupLeft, "laneDividerGroupId")

            ElementTree.SubElement(l_laneDividerGroupIdL, "id0").text = str(bid[0])
            ElementTree.SubElement(l_laneDividerGroupIdL, "id1").text = str(bid[1])
            ElementTree.SubElement(l_laneDividerGroupIdL, "id2").text = str(bid[2])
            ElementTree.SubElement(l_laneDividerGroupIdL, "id3").text = str(bid[3])
            
        n = connection_lanes2(i, 'next',successors,predecessors,successorsLanes,predecessorsLanes,left_lanes,right_lanes,junction,lane_properties)
        if n!=None:
            for k in n:
                l_nextConnections = ElementTree.SubElement(lane, "nextConnections")
    
                n_laneConnection = ElementTree.SubElement(l_nextConnections, "laneConnection")
    
                n_laneId = ElementTree.SubElement(n_laneConnection, "laneId")
                id0, id1, id2, id3 = set_id(k[1], k[2], 'lane')
    
                ElementTree.SubElement(n_laneId, "id0").text = str(id0)
                ElementTree.SubElement(n_laneId, "id1").text = str(id1)
                ElementTree.SubElement(n_laneId, "id2").text = str(id2)
                ElementTree.SubElement(n_laneId, "id3").text = str(id3)
    
                #sid = search_indexes(op_lane, lane_properties, 'Id')
                #print(sid)
                current_direction = get_lane_driving_dir2(k[3])
                previous_direction = get_lane_driving_dir2(k[0])
    
                s = same_direction(current_direction, previous_direction)
                
                ElementTree.SubElement(n_laneConnection, "sameDirection").text = str(s)
    
        p = connection_lanes2(i, 'prev',successors,predecessors,successorsLanes,predecessorsLanes,left_lanes,right_lanes,junction,lane_properties)
        if p!=None:
            for k in p:
                l_previousConnections = ElementTree.SubElement(lane, "previousConnections")
    
                p_laneConnection = ElementTree.SubElement(l_previousConnections, "laneConnection")
    
                p_laneId = ElementTree.SubElement(p_laneConnection, "laneId")
                id0, id1, id2, id3 = set_id(k[1], k[2], 'lane')
                ElementTree.SubElement(p_laneId, "id0").text = str(id0)
                ElementTree.SubElement(p_laneId, "id1").text = str(id1)
                ElementTree.SubElement(p_laneId, "id2").text = str(id2)
                ElementTree.SubElement(p_laneId, "id3").text = str(id3)
                
            
                #sid = search_indexes(op_lane, lane_properties, 'Id')
                current_direction = get_lane_driving_dir2(k[3])
                previous_direction = get_lane_driving_dir2(k[0])
    
                s = same_direction(current_direction, previous_direction)
    
                ElementTree.SubElement(p_laneConnection, "sameDirection").text = str(s)
        
        features = ElementTree.SubElement(roadSegment, "features")
        feature = ElementTree.SubElement(features, "feature")
        o_id = ElementTree.SubElement(feature, "id")
        local_ctrl_p = [[0.0, 0.0, 0.0],
                [-70.0, -60.0, 0.0],
                 [-80.0,-70.0, 0.0]]

    # geodetic [lat,lon,h] Control points
        geodet_ctrl_p = [[41.1472050, 24.9160020, 0.0],
                     [41.1466647, 24.9151682, 0.0],
                      [41.1456647, 24.9141682, 0.0]]
            
        for j in obj_id(i):
            ElementTree.SubElement(o_id, "id0").text = str(j)
            
            ElementTree.SubElement(feature, "type").text = "0"
            
        for k in objxy(i):
            a = local_to_wgs84(geodet_ctrl_p, local_ctrl_p, k)
            x,y,z = transform_wgs84_to_local(a[0][0],a[0][1],0, origin[0], origin[1], 0)
            
            f_abs = ElementTree.SubElement(feature, "absGeometry")
            ElementTree.SubElement(f_abs, "geoPoint").text = point_str(a[0][0],a[0][1],0)
            
            f_geometry = ElementTree.SubElement(feature, "geometry")
            ElementTree.SubElement(f_geometry, "point").text = point_str(x,y,z)

        if connection_road2(i,'nextr',successors,predecessors,left_lanes,right_lanes,lane_properties,coordinates,junction)!=None:
            t, con = connection_road2(i,'nextr')
            nextConnections = ElementTree.SubElement(roadSegment, "nextConnections")
            
            if(str(t) == 'junction'):
                for c in con:
                    n_roadSegmentConnection = ElementTree.SubElement(nextConnections, "roadSegmentConnection")
                    n_rs_id = ElementTree.SubElement(n_roadSegmentConnection, "roadSegmentId")
    
                    ElementTree.SubElement(n_rs_id, "id0").text = str(c[1])
                    ElementTree.SubElement(n_rs_id, "id1").text = "0"
                    ElementTree.SubElement(n_rs_id, "id2").text = "0"
    
                    ElementTree.SubElement(n_roadSegmentConnection, "sameDirection")
                    co = np.array([[float(origin[0])], [float(origin[1])], [float(origin[2])]])
                    no = np.array([[float(c[0][0])], [float(c[0][1])], [float(c[0][2])]])
                    r, t = rigid_transform_3D(co, no)
                    ElementTree.SubElement(n_roadSegmentConnection, "connectedToLocal").text = rt_tostring(r, t) #TI EINAI AUTO?
        
            if(str(t) == 'road'):
                for c in con:
                    n_roadSegmentConnection = ElementTree.SubElement(nextConnections, "roadSegmentConnection")
                    n_rs_id = ElementTree.SubElement(n_roadSegmentConnection, "roadSegmentId")
        
                    ElementTree.SubElement(n_rs_id, "id0").text = str(c[1])
                    ElementTree.SubElement(n_rs_id, "id1").text = "0"
                    ElementTree.SubElement(n_rs_id, "id2").text = "0"
        
                    ElementTree.SubElement(n_roadSegmentConnection, "sameDirection")
                    co = np.array([[float(origin[0])], [float(origin[1])], [float(origin[2])]])
                    no = np.array([[float(c[0][0])], [float(c[0][1])], [float(c[0][2])]])
                    r, t = rigid_transform_3D(co, no)
                    ElementTree.SubElement(n_roadSegmentConnection, "connectedToLocal").text = rt_tostring(r, t)
                
        if connection_road2(i,'prev',successors,predecessors,left_lanes,right_lanes,lane_properties,coordinates,junction)!= None:
            t, con = connection_road2(i,'prev') 
            previousConnections = ElementTree.SubElement(roadSegment, "previousConnections")
        
        if(str(t) == 'junction'):
            for c in con:
                p_roadSegmentConnection = ElementTree.SubElement(previousConnections, "roadSegmentConnection")
                p_rs_id = ElementTree.SubElement(p_roadSegmentConnection, "roadSegmentId")

                ElementTree.SubElement(p_rs_id, "id0").text = str(c[1])
                ElementTree.SubElement(p_rs_id, "id1").text = "0"
                ElementTree.SubElement(p_rs_id, "id2").text = "0"

                ElementTree.SubElement(p_roadSegmentConnection, "sameDirection")
                co = np.array([[float(origin[0])], [float(origin[1])], [float(origin[2])]])
                po = np.array([[float(c[0][0])], [float(c[0][1])], [float(c[0][2])]])
                r, t = rigid_transform_3D(co, po)
                ElementTree.SubElement(p_roadSegmentConnection, "connectedToLocal").text = rt_tostring(r, t)
        
        if(str(t) == 'road'):
            for c in con:
                p_roadSegmentConnection = ElementTree.SubElement(previousConnections, "roadSegmentConnection")
                p_rs_id = ElementTree.SubElement(p_roadSegmentConnection, "roadSegmentId")
    
                ElementTree.SubElement(p_rs_id, "id0").text = str(c[1])
                ElementTree.SubElement(p_rs_id, "id1").text = "0"
                ElementTree.SubElement(p_rs_id, "id2").text = "0"
    
                ElementTree.SubElement(p_roadSegmentConnection, "sameDirection")
                co = np.array([[float(origin[0])], [float(origin[1])], [float(origin[2])]])
                po = np.array([[float(c[0][0])], [float(c[0][1])], [float(c[0][2])]])
                r, t = rigid_transform_3D(co, po)
                ElementTree.SubElement(p_roadSegmentConnection, "connectedToLocal").text = rt_tostring(r, t)
            
        

tree = ElementTree.ElementTree(dwmaps)
#ElementTree.indent(tree, '  ')
tree.write("filename3.xml")
