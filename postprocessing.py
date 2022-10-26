import pandas as pd
import pickle
import random
import math

def get_road_ids(file):
    ids = pd.read_csv(file)
    road_ids = ids['Road Id'].values.tolist()
    return(road_ids)

def get_road_types(file):
    with open(file, 'rb') as handle:
        data = handle.read()
        d = pickle.loads(data)
        return(d)

def translate_road_type(t):
    if(t == "town"):
        return(4)

def search_indexes(value, df, column_name):
    return(df.loc[df[column_name] == value].index.values)

def road_origin(road_id, df_left, df_right, lane_properties, coordinates):
    origin = []
    df = df_left
    indexes = search_indexes(road_id, df_left, 'Road Id')
    if(len(indexes) == 0):
        df = df_right
        indexes = search_indexes(road_id, df_right, 'Road Id')
    for i in indexes:
        if(df.loc[i].Id == 1 or df.loc[i].Id == -1):
            lane_id = df.loc[i].laneId
            
    center_lane_index = search_indexes(lane_id, lane_properties, 'Id')
    
    if(df.loc[i].Id == 1):
        center_id = lane_properties.loc[center_lane_index[0]].RightBoundaryId
    if(df.loc[i].Id == -1 or -2):
        center_id = lane_properties.loc[center_lane_index[0]].LeftBoundaryID
    
    origin_index = search_indexes(center_id, coordinates, 'Id')
    origin.append(coordinates.loc[origin_index[0]].y)
    origin.append(coordinates.loc[origin_index[0]].x)
    origin.append(coordinates.loc[origin_index[0]].z)

    return(origin)

def set_id(road_id, lane_id, type):
    # id3 is 0 for lane id 
    # for other types will set the id3 to other numbers
    id0 = road_id
    id1 = abs(lane_id)
    if(lane_id>0):
        id2 = 0
    else:
        id2 = 1
    if(type == "lane"):
        id3 = 0
    if(type == "lanedivider"):
        id3 = random.randint(0,100)
    return id0, id1, id2, id3

def get_lanes(road_id, df_left, df_right): 
    road_lanes = pd.DataFrame(columns=['Road Id', 'Id', 'type', 'roadmark type', 'roadmark material', 
                                    'roadmark color', 'roadmark laneChange', 'max speed', 'speed unit',
                                    'laneId', 'travelDir'])
    lefts = search_indexes(road_id, df_left, 'Road Id')
    rights = search_indexes(road_id, df_right, 'Road Id')
    for l in lefts:
        d = df_left.loc[l].to_frame().transpose()
        road_lanes = pd.concat([road_lanes, d], axis=0, ignore_index=True)
    
    for r in rights:
        d = df_right.loc[r].to_frame().transpose()
        road_lanes = pd.concat([road_lanes, d], axis=0, ignore_index=True)
    
    return(road_lanes)

def get_lane_type(index, df):
    t = df['type'].loc[index]
    if(t == "shoulder"):
        return(1)
    if(t == "driving"):
        return(0)

def get_lane_driving_dir(index, df):
    driving_dir = df['travelDir'].loc[index]
    if(driving_dir == "undirected"):
        return(3)
    if(driving_dir == "forward"):
        return(0)
    if(driving_dir == "backward"):
        return(1)
  
def get_lane_driving_dir2(driving_dir):
    
    if(driving_dir) == ('undirected'):
        return(3)
    if(driving_dir) == ('Undirected'):
        return(3)
    if(driving_dir) == ('forward'):
        return(0)
    if(driving_dir)==('Forward'):
        return(0)
    if(driving_dir) == ('Backward'):
        return(1)
    if(driving_dir)==('backward'):
        return(1)

def get_speed_limit(index, df):
    speed = df['max speed'].loc[index]
    return(speed)

def get_geopoints(lane_id, coords):
    d = coords.loc[coords['Id'] == lane_id]
    d.reset_index(drop=True, inplace=True)
    return(d)
    
def point_str(x, y, z):
    return(str(x)+' '+str(y)+' '+str(z))

def get_dividers(op_lane_id, df):
    dividers = []
    # to df einai to lane_properties
    for o in op_lane_id:
        index = search_indexes(o, df, 'Id')
        lane_boundary = df['LeftBoundaryID'].loc[index].values
        if(lane_boundary[0] in dividers):
            continue
        else:
            dividers.append(lane_boundary[0])       
        lane_boundary = df['RightBoundaryId'].loc[index].values
        if(lane_boundary[0] in dividers):
            continue
        else:
            dividers.append(lane_boundary[0])
    return(dividers)

def save_ids(df, op_id, id0, id1, id2, id3):
    m = [op_id, id0, id1, id2, id3]
    m_df = pd.DataFrame(m)
    m_df = m_df.transpose()
    m_df.columns = ['laneId', 'id0', 'id1', 'id2', 'id3']
    df = pd.concat([df, m_df], axis=0, ignore_index=True)
    return(df)

def find_boundary_id(lane_id, df, df_id, lr):
    id = []
    ind = ''
    i = search_indexes(lane_id, df, 'Id')
    if lr == "right":
        ind = df['RightBoundaryId'].loc[i]
    if lr == "left":
        ind = df["LeftBoundaryID"].loc[i] 
    ind_id = search_indexes(ind.values[0], df_id, 'laneId')
    if len(ind_id) == 0:
        return None
    else:
        id.append(df_id['id0'].loc[ind_id.item(0)])
        id.append(df_id['id1'].loc[ind_id.item(0)])
        id.append(df_id['id2'].loc[ind_id.item(0)])
        id.append(df_id['id3'].loc[ind_id.item(0)])
        return(id)

def same_direction(lane_direction, other):
    if(lane_direction ==  other):
        return(1)
    else:
        return(0)

def rt_tostring(r, t):
    string = str(r[0][0])+' '+str(r[0][1])+' '+str(r[0][2])+' '+str(t[0][0])+' '+str(r[1][0])+' '+str(r[1][1])+' '+str(r[1][2])+' '+str(t[1][0])+' '+str(r[2][0])+' '+str(r[2][1])+' '+str(r[2][2])+' '+str(t[2][0])+' '+'0'+' '+'0'+' '+'0'+' '+'1'
    return(string)

def num_lanes(road_id, df):
    index = search_indexes(road_id, df, 'Road Id')
    s = df['rightBoundary'].loc[index.item(0)]
    e = df['leftBoundary'].loc[index.item(0)]
    num = abs(s - e)
    return(num)

def objxy(road_id,objects,geo):
    objects1 = pd.DataFrame(columns=['Road Id', 'id', 'name', 's', 't', 'zOffset', 'hdg', 'roll',
                                        'pitch', 'orientation', 'type', 'height', 'width', 'length'])
    geo1 = pd.DataFrame(columns=['Road Id', 's', 'x', 'hdg', 'length'])
    x = []
   
    objects1 = pd.DataFrame()
    geo1 = pd.DataFrame()
    indexes1 = search_indexes(road_id,objects,'Road id')
    if len(indexes1)==0:
        indexes2 = []
    for i2 in indexes1:
        indexes2 = search_indexes(objects.iloc[i2]['Road id'] ,geo,'Road Id')
    #print(indexes1,indexes2)
    for i1 in indexes1:
        d = objects.loc[i1].to_frame().transpose()
        objects1 = pd.concat([objects1, d], axis=0, ignore_index=True)
    for i3 in indexes2:
        d1 = geo.loc[i3].to_frame().transpose()
        geo1 = pd.concat([geo1, d1], axis=0, ignore_index=True)
       
    for index1,row1 in objects1.iterrows():
        #print(1)
        temp = 0
        if(len(geo1)==1):
            temp = 1
            xa = geo1.iloc[0]['x'] + (objects1.iloc[index1]['s'] - geo1.iloc[0]['s'])* (math.cos(geo1.iloc[0]['hdg']))
            ya = geo1.iloc[0]['y'] + (objects1.iloc[index1]['s'] - geo1.iloc[0]['s'])* (math.cos(geo1.iloc[0]['hdg']))
            xf = xa +(objects1.iloc[index1]['t']*math.sin(objects1.iloc[index1]['hdg']))
            yf = ya +(objects1.iloc[index1]['t']*math.cos(objects1.iloc[index1]['hdg']))
            x.append([xf,yf])
            
            #print(i,index1,index2-1,xa)
        for index2 in range(1,len(geo1)):
            #print(i,len(geo1))
            if (objects1.iloc[index1]['s'] > geo1.iloc[index2-1]['s'] and objects1.iloc[index1]['s'] < geo1.iloc[index2]['s'] and temp==0):
                temp = 2
                xa = geo1.iloc[index2-1]['x'] + (objects1.iloc[index1]['s'] - geo1.iloc[index2-1]['s'])*(math.cos(geo1.iloc[index2-1]['hdg']))
                ya = geo1.iloc[index2-1]['y'] + (objects1.iloc[index1]['s'] - geo1.iloc[index2-1]['s'])*(math.cos(geo1.iloc[index2-1]['hdg']))
                xf = xa +(objects1.iloc[index1]['t']*math.sin(objects1.iloc[index1]['hdg']))
                yf = ya +(objects1.iloc[index1]['t']*math.cos(objects1.iloc[index1]['hdg']))
                x.append([xf,yf])
                
                #print(index1,index2-1)
        if (temp == 0):
            #print(road_id,index1,index2)
            xa = geo1.iloc[index2-1]['x'] + (objects1.iloc[index1]['s'] - geo1.iloc[index2-1]['s'])*(math.cos(geo1.iloc[index2-1]['hdg']))
            ya = geo1.iloc[index2-1]['y'] + (objects1.iloc[index1]['s'] - geo1.iloc[index2-1]['s'])*(math.cos(geo1.iloc[index2-1]['hdg']))
            xf = xa +(objects1.iloc[index1]['t']*math.sin(objects1.iloc[index1]['hdg']))
            yf = ya +(objects1.iloc[index1]['t']*math.cos(objects1.iloc[index1]['hdg']))
            x.append([xf,yf])
            
          
    return(x)

def connection_road2(road_id,connection_type,successors,predecessors,left_lanes,right_lanes,lane_properties,coordinates,junction):
    element_type=''
    element_id = 0
    next_con = []
    prev_con = []
    
    if (connection_type == 'nextr'):
        index = search_indexes(road_id, successors, 'Road Id')
        index1 = search_indexes(road_id, predecessors, 'elementId')
        element_type = successors['elementType'].loc[index.item(0)]
        element_id = successors['elementId'].loc[index.item(0)]
        #print(element_type)
        if(element_type == 'road'):
            origin = road_origin(element_id, left_lanes, right_lanes, lane_properties, coordinates)
            next_con.append([origin, element_id])
            #next_con.append([road_id,element_id])
            
        if(element_type == 'junction'):

            for j in junctions:
                if(j[0] == str(element_id)):
                    for k in j[2]:
                        if(k[1] == str(road_id)):
                            ri = k[2]
                            origin = road_origin(int(ri), left_lanes, right_lanes, lane_properties, coordinates)
                            next_con.append([origin, ri])
                            
                            #next_con.append([road_id, ri])
                            

        for l in index1:
            element_type1 = predecessors['elementType'].loc[l.item(0)]
            origin = road_origin(predecessors['Road Id'].loc[l.item(0)], left_lanes, right_lanes, lane_properties, coordinates)
            
            if(element_type1 == 'road' and [origin,str(predecessors['Road Id'].loc[l.item(0)])] not in next_con):
                next_con.append([origin, str(predecessors['Road Id'].loc[l.item(0)])])
        
        return(element_type,next_con)

    if (connection_type == 'prev'):
        indexx = search_indexes(road_id, predecessors, 'Road Id')
        indexx1 = search_indexes(road_id, successors, 'elementId')
        element_type = predecessors['elementType'].loc[indexx.item(0)]
        element_id = predecessors['elementId'].loc[indexx.item(0)]
        #print(element_type)
        if(element_type == 'road'):
            origin = road_origin(element_id, left_lanes, right_lanes, lane_properties, coordinates)
            prev_con.append([origin, element_id])
            #prev_con.append([road_id,element_id])
            #print(connections)
        if(element_type == 'junction'):
              
            for j in junctions:
                if(j[0] == str(element_id)):
                    
                    for k in j[2]:
                        if(k[1] == str(road_id)):
                            ri = k[2]
                            origin = road_origin(int(ri), left_lanes, right_lanes, lane_properties, coordinates)
                            prev_con.append([origin, ri])
                            #prev_con.append([road_id, ri])
                            #print(connections)
    
        for l in indexx1:
            element_type1 = predecessors['elementType'].loc[l.item(0)]
            origin = road_origin(successors['Road Id'].loc[l.item(0)], left_lanes, right_lanes, lane_properties, coordinates)
            
            if(element_type1 == 'road' and [origin,str(successors['Road Id'].loc[l.item(0)])] not in prev_con):
                prev_con.append([origin, str(successors['Road Id'].loc[l.item(0)])])
            
        return(element_type,prev_con)
    
def connection_lanes2(road_id,connection_type,successors,predecessors,successorsLanes,predecessorsLanes,left_lanes,right_lanes,junction,lane_properties):
    element_type=''
    element_id = 0
    next_con = []
    prev_con = []
    
    if (connection_type == 'next'):
        index = search_indexes(road_id, successors, 'Road Id')
        
        index1 = search_indexes(road_id, predecessors, 'elementId')
        element_type = successors['elementType'].loc[index.item(0)]
        element_id = successors['elementId'].loc[index.item(0)]
        #print(element_type)
        if(element_type == 'road'):
            #print(1)
            indexx = search_indexes(successors['Road Id'].loc[index.item(0)],successorsLanes, 'RoadId')
            #print(indexx)
            
            indexxx = search_indexes(successors['Road Id'].loc[index.item(0)],left_lanes, 'Road Id')
            if len(indexxx)==0:
                #print(road_id,indexxx)
                indexxxx = search_indexes(successors['Road Id'].loc[index.item(0)],right_lanes, 'Road Id')
                #print(indexxxx)
                for a in indexxxx:
                    if right_lanes['Id'][a] == successorsLanes['IdOfSuccessorLane'].loc[indexx.item(0)]:
                        op_lane = right_lanes['laneId'][a]
                        index4 = search_indexes(op_lane,lane_properties,'Id')
                        next_direction = lane_properties['SuccessorDir'].loc[index4.item(0)]
                        next_con.append([next_direction,right_lanes['Road Id'].loc[a.item(0)],right_lanes['Id'].loc[a.item(0)],right_lanes['travelDir'].loc[a.item(0)]])
            else:
                for a in indexxx:
                    
                    if left_lanes['Id'][a] == successorsLanes['IdOfSuccessorLane'].loc[indexx.item(0)]:
                        op_lane = left_lanes['laneId'][a]
                        index4 = search_indexes(op_lane,lane_properties,'Id')
                        next_direction = lane_properties['SuccessorDir'].loc[index4.item(0)]
                        next_con.append([next_direction,left_lanes['Road Id'].loc[a.item(0)],left_lanes['Id'].loc[a.item(0)],left_lanes['travelDir'].loc[a.item(0)]])
                    
               
        if(element_type == 'junction'):

            for j in junctions:
                if(j[0] == str(element_id)):
                    for k in j[2]:
                        if(k[1] == str(road_id)):
                            ri = k[4]
                            next_road = k[2]
                            
                            index2 = search_indexes(road_id,left_lanes,'Road Id')
                            #print(index2)
                            for c in index2:
                                #print(str(left_lanes['Id'][c]))
                                #print(ri)
                                #print(len(ri))
                                #if ri in range(left_lanes['Id'][c]):
                                #if str(left_lanes['Id'][c]) in range(len(ri)):
                                for d in ri:
                                    #print(type(d))
                                    if(str(left_lanes['Id'][c])) in d: 
                                        #print(1)
                                        op_lane = left_lanes['laneId'][c]
                                        index4 = search_indexes(op_lane,lane_properties,'Id')
                                        next_direction = lane_properties['SuccessorDir'].loc[index4.item(0)]
                                        if ([next_direction,left_lanes['Road Id'].loc[c.item(0)],left_lanes['Id'].loc[c.item(0)],left_lanes['travelDir'].loc[c.item(0)]]not in next_con):
                                            next_con.append([next_direction, left_lanes['Road Id'].loc[c.item(0)],left_lanes['Id'].loc[c.item(0)],left_lanes['travelDir'].loc[c.item(0)]])
                                else:
                                    indexx2 = search_indexes(road_id,right_lanes,'Road Id')
                                    for c in indexx2:
                                        #print(str(right_lanes['Id'][c]))
                                        #print(ri)
                                        #if ri in range(right_lanes['Id'][c]):
                                        #if str(right_lanes['Id'][c]) in range(len(ri)):
                                        for d in ri:
                                            #print(d)
                                            if((str(right_lanes['Id'][c])) in d):
                                                op_lane = right_lanes['laneId'][c]
                                                index4 = search_indexes(op_lane,lane_properties,'Id')
                                                next_direction = lane_properties['SuccessorDir'].loc[index4.item(0)]
                                                if ([next_direction,right_lanes['Road Id'].loc[c.item(0)],right_lanes['Id'].loc[c.item(0)],right_lanes['travelDir'].loc[c.item(0)]]not in next_con):
                                                    next_con.append([next_direction,right_lanes['Road Id'].loc[c.item(0)],right_lanes['Id'].loc[c.item(0)],right_lanes['travelDir'].loc[c.item(0)]])
                                    
                              

        for l in index1:
            #print(predecessors['Road Id'].loc[index1.item(0)])
            element_type1 = predecessors['elementType'].loc[l.item(0)]
            if(element_type1 == 'road'): #AN EMFANISTEI 2PLO
                indexx1 = search_indexes(predecessors['Road Id'].loc[l.item(0)], predecessorsLanes, 'RoadId')
                #print(indexx1)
                indexxx1 = search_indexes(predecessors['Road Id'].loc[l.item(0)], left_lanes, 'Road Id')
                if len(indexxx1)==0:
                    #print(indexxx1,road_id)
                    indexxxx1 = search_indexes(predecessors['Road Id'].loc[l.item(0)], right_lanes, 'Road Id')
                    #print(indexxxx1)
                    for b in indexxxx1:
                        if (right_lanes['Id'][b] == predecessorsLanes['IdOfPredecessorLane'].loc[indexx1.item(0)]): 
                            op_lane = right_lanes['laneId'][b]
                            index4 = search_indexes(op_lane,lane_properties,'Id')
                            next_direction = lane_properties['SuccessorDir'].loc[index4.item(0)]
                            if ([next_direction,str(road_id),right_lanes['Id'].loc[b.item(0)],right_lanes['travelDir'].loc[b.item(0)]]not in next_con):
                                next_con.append([next_direction,road_id,right_lanes['Id'].loc[b.item(0)],right_lanes['travelDir'].loc[b.item(0)]])
                else:
                    for b in indexxx1:
                        if (left_lanes['Id'][b] == predecessorsLanes['IdOfPredecessorLane'].loc[indexx1.item(0)]): 
                            op_lane = left_lanes['laneId'][b]
                            index4 = search_indexes(op_lane,lane_properties,'Id')
                            next_direction = lane_properties['SuccessorDir'].loc[index4.item(0)]
                            if ([next_direction, str(road_id),left_lanes['Id'].loc[b.item(0)],left_lanes['travelDir'].loc[b.item(0)]]not in next_con):
                                next_con.append([next_direction,road_id,left_lanes['Id'].loc[b.item(0)],left_lanes['travelDir'].loc[b.item(0)]])
        return(next_con)
    

    if (connection_type == 'prev'):
        indexe = search_indexes(road_id, predecessors, 'Road Id')
        
        indexe1 = search_indexes(road_id, successors, 'elementId')
        elemente_type = predecessors['elementType'].loc[indexe.item(0)]
        elemente_id = predecessors['elementId'].loc[indexe.item(0)]
        #print(element_type)
        if(elemente_type == 'road'):
            #print(1)
            indexxe = search_indexes(predecessors['Road Id'].loc[indexe.item(0)],predecessorsLanes, 'RoadId')
            #print(indexx)
            
            indexxxe = search_indexes(predecessors['Road Id'].loc[indexe.item(0)],left_lanes, 'Road Id')
            if len(indexxxe)==0:
                #print(road_id,indexxx)
                indexxxxe = search_indexes(predecessors['Road Id'].loc[indexe.item(0)],right_lanes, 'Road Id')
                #print(indexxxx)
                for a in indexxxxe:
                    if right_lanes['Id'][a] == predecessorsLanes['IdOfPredecessorLane'].loc[indexxe.item(0)]:
                        op_lane = left_lanes['laneId'][a]
                        index5 = search_indexes(op_lane,lane_properties,'Id')
                        prev_direction = lane_properties['PredecessorDir'].loc[index5.item(0)]
                        prev_con.append([prev_direction,right_lanes['Road Id'].loc[a.item(0)],right_lanes['Id'].loc[a.item(0)],right_lanes['travelDir'].loc[a.item(0)]])
            else:
                for a in indexxxe:
                    if left_lanes['Id'][a] == predecessorsLanes['IdOfPredecessorLane'].loc[indexxe.item(0)]:
                        op_lane = left_lanes['laneId'][a]
                        index5 = search_indexes(op_lane,lane_properties,'Id')
                        prev_direction = lane_properties['PredecessorDir'].loc[index5.item(0)]
                        prev_con.append([prev_direction,left_lanes['Road Id'].loc[a.item(0)],left_lanes['Id'].loc[a.item(0)],left_lanes['travelDir'].loc[a.item(0)]])
                    
               
        if(elemente_type == 'junction'):

            for j in junctions:
                if(j[0] == str(elemente_id)):
                    for k in j[2]:
                        if(k[1] == str(road_id)):
                            ri = k[4]
                            #prev_road = k[2]
                            
                            indexe2 = search_indexes(road_id,left_lanes,'Road Id')
                            #print(index2)
                            for c in indexe2:
                                #print(str(left_lanes['Id'][c]))
                                #print(ri)
                                #print(len(ri))
                                #if ri in range(left_lanes['Id'][c]):
                                #if str(left_lanes['Id'][c]) in range(len(ri)):
                                for d in ri:
                                    #print(type(d))
                                    if(str(left_lanes['Id'][c])) in d: 
                                        op_lane = left_lanes['laneId'][c]
                                        index5 = search_indexes(op_lane,lane_properties,'Id')
                                        prev_direction = lane_properties['PredecessorDir'].loc[index5.item(0)]
                                        if([prev_direction,left_lanes['Road Id'].loc[c.item(0)],left_lanes['Id'].loc[c.item(0)],left_lanes['travelDir'].loc[c.item(0)]]not in prev_con):
                               
                                            prev_con.append([prev_direction,left_lanes['Road Id'].loc[c.item(0)],left_lanes['Id'].loc[c.item(0)],left_lanes['travelDir'].loc[c.item(0)]])
                                else:
                                    indexxe2 = search_indexes(road_id,right_lanes,'Road Id')
                                    for c in indexxe2:
                                        #print(str(right_lanes['Id'][c]))
                                        #print(ri)
                                        #if ri in range(right_lanes['Id'][c]):
                                        #if str(right_lanes['Id'][c]) in range(len(ri)):
                                        for d in ri:
                                            #print(d)
                                            if(str(right_lanes['Id'][c])) in d: 
                                                op_lane = left_lanes['laneId'][c]
                                                index5 = search_indexes(op_lane,lane_properties,'Id')
                                                prev_direction = lane_properties['PredecessorDir'].loc[index5.item(0)]
                                                if([prev_direction,right_lanes['Road Id'].loc[c.item(0)],right_lanes['Id'].loc[c.item(0)],right_lanes['travelDir'].loc[c.item(0)]]not in prev_con):
                                                    prev_con.append([prev_direction,right_lanes['Road Id'].loc[c.item(0)],right_lanes['Id'].loc[c.item(0)],right_lanes['travelDir'].loc[c.item(0)]])
                                    
                              

        for l in indexe1:
            #print(predecessors['Road Id'].loc[index1.item(0)])
            elemente_type1 = successors['elementType'].loc[l.item(0)]
            if(elemente_type1 == 'road'): #AN EMFANISTEI 2PLO
                indexxe1 = search_indexes(successors['Road Id'].loc[l.item(0)], successorsLanes, 'RoadId')
                #print(indexx1)
                indexxxe1 = search_indexes(successors['Road Id'].loc[l.item(0)], left_lanes, 'Road Id')
                if len(indexxxe1)==0:
                    #print(indexxx1,road_id)
                    indexxxxe1 = search_indexes(successors['Road Id'].loc[l.item(0)], right_lanes, 'Road Id')
                    #print(indexxxx1)
                    for b in indexxxxe1:
                        if (right_lanes['Id'][b] == successorsLanes['IdOfSuccessorLane'].loc[indexxe1.item(0)]): 
                            op_lane = left_lanes['laneId'][b]
                            index5 = search_indexes(op_lane,lane_properties,'Id')
                            prev_direction = lane_properties['PredecessorDir'].loc[index5.item(0)]
                            if([prev_direction,str(road_id),right_lanes['Id'].loc[b.item(0)],right_lanes['travelDir'].loc[b.item(0)]]not in prev_con):
                                prev_con.append([prev_direction,road_id,right_lanes['Id'].loc[b.item(0)],right_lanes['travelDir'].loc[b.item(0)]])
                else:
                    for b in indexxxe1:
                        if (left_lanes['Id'][b] == successorsLanes['IdOfSuccessorLane'].loc[indexxe1.item(0)]):
                            op_lane = left_lanes['laneId'][b]
                            index5 = search_indexes(op_lane,lane_properties,'Id')
                            prev_direction = lane_properties['PredecessorDir'].loc[index5.item(0)]
                            
                            if([prev_direction,str(road_id),left_lanes['Id'].loc[b.item(0)],left_lanes['travelDir'].loc[b.item(0)]]not in prev_con):
                                prev_con.append([prev_direction,road_id,left_lanes['Id'].loc[b.item(0)],left_lanes['travelDir'].loc[b.item(0)]])
        return(prev_con)
    
def obj_id(road_id,objects):
    a=[]
    index = search_indexes(road_id,objects,'Road id')
    #print(index)
    for i in index:
        #print(i)
        a.append(objects['id'].loc[i.item(0)])
    return(a)
