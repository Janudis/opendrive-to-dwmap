from xml.etree import ElementTree
import pandas as pd
import pickle
from postprocessing import search_indexes

def appear(element):
    if(element is not None):
        return True
    else:
        return False
    
def next_conn1(element, road_id):
    c = []
    c.append(road_id)
    el = element.find("lanes/laneSection/left/lane/link/successor")
    Id = el.get("id")
    c.append(Id)
    return(c)

def next_conn2(element, road_id):
    c = []
    c.append(road_id)
    el = element.find("lanes/laneSection/right/lane/link/successor")
    Id = el.get("id")
    c.append(Id)
    return(c)   

def prev_conn1(element,road_id):
    c = []
    c.append(road_id)
    
    el = element.find("lanes/laneSection/left/lane/link/predecessor")
    Id = el.get("id")
    c.append(Id)
    return(c)

def prev_conn2(element,road_id):
    c = []
    c.append(road_id)
    
    el = element.find("lanes/laneSection/right/lane/link/predecessor")
    Id = el.get("id")
    c.append(Id)
    return(c)

def read_geo(element, road_id, path):
    points = []
    # path = planview/geometry
    geo = element.findall(path)
    for g in geo:
        point = []
        point.append(road_id)
        s = g.get("s")
        point.append(s)
        x = g.get("x")
        point.append(x)
        y = g.get("y")
        point.append(y)
        hdg = g.get("hdg")
        point.append(hdg)
        length = g.get("length")
        point.append(length)
        
        points.append(point)
    #print(points)   
    return points

def read_link(element, road_id, path):
    # path = link/predeseccor
    # or link/successor
    p = []
    p.append(road_id)
    e = element.find(path)
    elementType = e.get("elementType")
    elementId = e.get("elementId")
    p.append(elementType)
    p.append(elementId)
    if(elementType == 'road'):
        contactPoint = e.get("contactPoint")
        p.append(contactPoint)
    else:
        p.append(None)
    return p

def read_speed(element, road_id):
    speeds = []
    e = element.find("type/speed")
    speeds.append(road_id)
    speeds.append(e.get("max"))
    return(speeds)

def read_lanes(element, road_id, path, coordinates):
    # path = lanes/laneSection/left/lane
    # or lanes/laneSections/center/lane
    # or lanes/laneSections/right/lane
    lanes = []
    e = element.findall(path)
    for l in e:
        lane = []
        lane.append(road_id)
        lane_id = l.get("id")
        lane.append(lane_id)
        lane_type = l.get("type")
        lane.append(lane_type)
        l = ElementTree.ElementTree(l)
        if(appear(l.find("roadMark"))):
            roadmark = l.find("roadMark")
            r_type = roadmark.get("type")
            lane.append(r_type)
            r_material = roadmark.get("material")
            lane.append(r_material)
            r_color = roadmark.get("color")
            lane.append(r_color)
            r_laneChange = roadmark.get("laneChange")
            lane.append(r_laneChange)
        if(appear(l.find("speed"))):
            speed = l.find("speed")
            max = speed.get("max")
            lane.append(max)
            unit = speed.get("unit")
            lane.append(unit)
        if(appear(l.find("userData/vectorLane"))):
            vectorlane = l.findall("userData/vectorLane")
            ids = []
            for v in vectorlane:
                laneId = v.get("laneId")
                ids.append(laneId)
            laneId = ids[0]
            lin = search_indexes(laneId, coordinates, 'Id')
            for i in ids:
                ind = search_indexes(i, coordinates, 'Id')
                if (len(ind) > len(lin)):
                    laneId = i
                    lin = ind
            lane.append(laneId)
            travel_dir = v.get("travelDir")
            lane.append(travel_dir)
        lanes.append(lane)
    return(lanes)

def read_lane_boundaries(element, road_id):
    boundaries = []
    e = element.find("lanes/laneSection/userData/vectorLaneSection/carriageway")
    boundaries.append(road_id)
    boundaries.append(e.get("rightBoundary"))
    boundaries.append(e.get("leftBoundary"))
    return(boundaries)

def read_objects(element, road_id, path):
    # path = objects/object
    objects = []
    e = element.findall(path)
    for o in e:
        object = []
        object.append(road_id)
        id = o.get("id")
        object.append(id)
        name = o.get("name")
        object.append(name)
        s = o.get("s")
        object.append(s)
        t = o.get("t")
        object.append(t)
        zOffset = o.get("zOffset")
        object.append(zOffset)
        hdg = o.get("hdg")
        object.append(hdg)
        roll = o.get("roll")
        object.append(roll)
        pitch = o.get("pitch")
        object.append(pitch)
        orientation = o.get("orientation")
        object.append(orientation)
        type = o.get("type")
        object.append(type)
        height = o.get("height")
        object.append(height)
        width = o.get("width")
        object.append(width)
        length = o.get("length")
        object.append(length)
        objects.append(object)
    return(objects)

def read_roads(file_path):
    root = ElementTree.parse(file_path).getroot()

    coordinates = pd.read_csv('csv/coordinates.csv')
    
    df_geo = pd.DataFrame(columns=['Road Id', 's', 'x', 'y', 'hdg', 'length'])
    df_successorsLanes = pd.DataFrame(columns=['RoadId','IdOfSuccessorLane'])
    df_predecessorsLanes = pd.DataFrame(columns=['RoadId', 'IdOfPredecessorLane'])
    df_predecessors = pd.DataFrame(columns=['Road Id', 'elementType', 'elementId','contactPoint'])
    df_successors = pd.DataFrame(columns=['Road Id', 'elementType', 'elementId','contactPoint'])
    df_left_lanes = pd.DataFrame(columns=['Road Id', 'Id', 'type', 'roadmark type', 'roadmark material', 
                                    'roadmark color', 'roadmark laneChange', 'max speed', 'speed unit',
                                    'laneId', 'travelDir'])
    df_center_lanes = pd.DataFrame(columns=['Road Id', 'Id', 'type', 'roadmark type', 'roadmark material',
                                            'roadmark color', 'roadmark laneChange'])
    df_right_lanes = pd.DataFrame(columns=['Road Id', 'Id', 'type', 'roadmark type', 'roadmark material', 
                                    'roadmark color', 'roadmark laneChange', 'max speed', 'speed unit',
                                    'laneId', 'travelDir'])
    df_objects = pd.DataFrame(columns=['Road Id', 'id', 'name', 's', 't', 'zOffset', 'hdg', 'roll',
                                        'pitch', 'orientation', 'type', 'height', 'width', 'length'])
    df_speeds = pd.DataFrame(columns=['Road Id', 'max'])
    df_lane_boundaries = pd.DataFrame(columns=['Road Id', 'rightBoundary', 'leftBoundary'])
    df_road_ids = pd.DataFrame(columns=['Road Id'])
    types = {}
    road = root.findall("./road")
    for r in road:
        road_name = r.get("name")
        if(road_name == "OriginReferenceRoad"):
            continue
        road_id = r.get("id")
        df_road_ids.loc[len(df_road_ids)] = road_id
        road_junction = r.get("junction")

        r = ElementTree.ElementTree(r)
        
        if(appear(r.find("planView/geometry"))):
            o = read_geo(r, road_id, "planView/geometry")
            df = pd.DataFrame(o)
            df.columns = ['Road Id', 's', 'x','y', 'hdg', 'length']
            df_geo = pd.concat([df_geo, df], axis=0, ignore_index=True)
         
        if(appear(r.find("lanes/laneSection/left/lane/link/successor"))):
            c = next_conn1(r, road_id)
            #print(p)
            df = pd.DataFrame(c)
            df = df.transpose()
            df.columns = ['RoadId','IdOfSuccessorLane']
            df_successorsLanes = pd.concat([df_successorsLanes, df], axis=0, ignore_index=True)
            
        if(appear(r.find("lanes/laneSection/right/lane/link/successor"))):
            c = next_conn2(r, road_id)
            #print(p)
            df = pd.DataFrame(c)
            df = df.transpose()
            df.columns = ['RoadId','IdOfSuccessorLane']
            df_successorsLanes = pd.concat([df_successorsLanes, df], axis=0, ignore_index=True)
        
        
        if(appear(r.find("lanes/laneSection/left/lane/link/predecessor"))):
            c = prev_conn1(r, road_id)
            #print(p)
            df = pd.DataFrame(c)
            df = df.transpose()
            df.columns = ['RoadId','IdOfPredecessorLane']
            df_predecessorsLanes = pd.concat([df_predecessorsLanes, df], axis=0, ignore_index=True)
        
        if(appear(r.find("lanes/laneSection/right/lane/link/predecessor"))):
            c = prev_conn2(r, road_id)
            #print(p)
            df = pd.DataFrame(c)
            df = df.transpose()
            df.columns = ['RoadId','IdOfPredecessorLane']
            df_predecessorsLanes = pd.concat([df_predecessorsLanes, df], axis=0, ignore_index=True))

        if(appear(r.find("link/predecessor"))):
            p = read_link(r,road_id, "link/predecessor")
            df = pd.DataFrame(p)
            df = df.transpose()
            df.columns = ['Road Id', 'elementType', 'elementId','contactPoint']
            df_predecessors = pd.concat([df_predecessors, df], axis=0, ignore_index=True)
        
        if(appear(r.find("link/successor"))):
            p = read_link(r, road_id, "link/successor")
            df = pd.DataFrame(p)
            df = df.transpose()
            df.columns = ['Road Id', 'elementType', 'elementId','contactPoint']
            df_successors = pd.concat([df_successors, df], axis=0, ignore_index=True)
        
        if(appear(r.find('type'))):
            p = read_speed(r, road_id)
            ty = r.find('type').get('type')
            types[road_id] = ty
            df = pd.DataFrame(p)
            df = df.transpose()
            df.columns = ['Road Id', 'max']
            df_speeds = pd.concat([df_speeds, df], axis=0, ignore_index=True)

        if(appear(r.find("lanes/laneSection/left/lane"))):
            left = read_lanes(r, road_id, "lanes/laneSection/left/lane", coordinates)
            df = pd.DataFrame(left)
            df.columns = ['Road Id', 'Id', 'type', 'roadmark type', 'roadmark material', 
                                    'roadmark color', 'roadmark laneChange', 'max speed', 'speed unit',
                                    'laneId', 'travelDir']
            df_left_lanes = pd.concat([df_left_lanes, df], axis=0, ignore_index=True)

        if(appear(r.find("lanes/laneSection/center/lane"))):
            center = read_lanes(r, road_id, "lanes/laneSection/center/lane", coordinates)
            df = pd.DataFrame(center)
            df.columns = ['Road Id', 'Id', 'type', 'roadmark type', 'roadmark material',
                                            'roadmark color', 'roadmark laneChange']
            df_center_lanes = pd.concat([df_center_lanes, df], axis=0, ignore_index=True)

        if(appear(r.find("lanes/laneSection/right/lane"))):
            right = read_lanes(r, road_id, "lanes/laneSection/right/lane", coordinates)
            df = pd.DataFrame(right)
            df.columns = ['Road Id', 'Id', 'type', 'roadmark type', 'roadmark material', 
                                    'roadmark color', 'roadmark laneChange', 'max speed', 'speed unit',
                                    'laneId', 'travelDir']
            df_right_lanes = pd.concat([df_right_lanes, df], axis=0, ignore_index=True)
        
        if(appear(r.find("lanes/laneSection/userData/vectorLaneSection/carriageway"))):
            p = read_lane_boundaries(r, road_id)
            df = pd.DataFrame(p)
            df = df.transpose()
            df.columns = ['Road Id', 'rightBoundary', 'leftBoundary']
            df_lane_boundaries = pd.concat([df_lane_boundaries, df], axis=0, ignore_index=True)

        if(appear(r.find("objects/object"))):
            o = read_objects(r, road_id, "objects/object")
            df = pd.DataFrame(o)
            df.columns = ['Road id', 'id', 'name', 's', 't', 'zOffset', 'hdg', 'roll',
                                        'pitch', 'orientation', 'type', 'height', 'width', 'length']
            df_objects = pd.concat([df_objects, df], axis=0, ignore_index=True)
            
    df_geo.to_csv('geo.csv', index=False) 
    df_successorsLanes.to_csv('successorsLanes.csv', index=False)
    df_predecessorsLanes.to_csv('predecessorsLanes.csv', index=False)
    df_predecessors.to_csv('csv2/predecessors.csv', index=False)
    df_successors.to_csv('csv2/successors.csv', index=False)
    df_left_lanes.to_csv('csv2/left_lanes.csv', index=False)
    df_center_lanes.to_csv('csv2/center_lanes.csv', index=False)
    df_right_lanes.to_csv('csv2/right_lanes.csv', index=False)
    df_objects.to_csv('csv2/objects.csv', index=False)
    df_speeds.to_csv('csv2/speeds.csv', index=False)
    df_lane_boundaries.to_csv('csv2/lane_boundaries.csv', index=False)
    df_road_ids.to_csv('csv2/road_ids.csv', index=False)
    file = open("csv2/types.txt", "wb")
    pickle.dump(types, file)
    file.close()

def read_junctions(file_path):
    root = ElementTree.parse(file_path).getroot()
    junction = root.findall("./junction")
    junctions=[]
    for j in junction:
        jun=[]
        junction_id = j.get("id")
        jun.append(junction_id)
        junction_name = j.get("name")
        jun.append(junction_name)
        j = ElementTree.ElementTree(j)
        connections = j.findall("connection")
        conns = []
        for c in connections:
            cs = []
            c_id = c.get("id")
            cs.append(c_id)
            c_incoming_road = c.get("incomingRoad")
            cs.append(c_incoming_road)
            c_connecting_road = c.get("connectingRoad")
            cs.append(c_connecting_road)
            c_contact_point = c.get("contactPoint")
            cs.append(c_contact_point)
            c = ElementTree.ElementTree(c)
            ll = c.findall("laneLink")
            ls = []
            for l in ll:
                f = l.get("from")
                t = l.get("to")
                ls.append([t])
            cs.append(ls)
            conns.append(cs)
        jun.append(conns)
        junctions.append(jun)
    return(junctions)

read_roads('final2.xodr')
junctions = read_junctions('final2.xodr')
        
#
