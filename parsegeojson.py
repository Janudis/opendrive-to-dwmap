from xml.etree import ElementTree
import pandas as pd

# parses the coordinates from the geojson converted into xml and saves it into a csv file
# the coordinates parsed are not juction, surface, or gate type
def export_coordinates(filename, output):

    root = ElementTree.parse(filename).getroot()

    df = pd.DataFrame(columns = ['Id', 'x', 'y', 'z'])

    feature = root.findall("features")

    for f in feature:
        f = ElementTree.ElementTree(f)
        id = f.find("properties/Id").text
        type = f.find("properties/Type").text
        if(type == "Junction" or type == "Surface" or type == "Gate"):
            continue
        item = f.findall("geometry/coordinates")
        for i in item:
            i = ElementTree.ElementTree(i)
            coordinates =[]
            en = i.findall("entry")
            for e in en:
                coordinates.append(e.text)
            df.loc[len(df)] = [id, coordinates[0], coordinates[1], coordinates[2]]

    df.to_csv(output)

# checks if a tag of an xml exists in the file
def check_appearance(element):
    if(element is not None):
        return element.text
    else:
        return None

# parses the properties of the lanes from the geojson file
def export_properties(filename, output_lane, output_boundaries):

    root = ElementTree.parse(filename).getroot()

    df_lane = pd.DataFrame(columns = ['Id', 'LaneType', 'LeftBoundaryID', 'LeftBoundaryDir', 'RightBoundaryId', 'RightBoundaryDir', 'PredecessorId', 'PredecessorDir', 
                                'SuccessorId', 'SuccessorDir', 'SpeedLimit', 'TravelDir', 'Type'])

    df_boundaries = pd.DataFrame(columns = ['Id', 'LeftLaneId', 'LeftLaneDir', 'RightLaneId', 'RightLaneDir', 'Type'])

    feature = root.findall("features")

    for f in feature:
        f = ElementTree.ElementTree(f)

        type = f.find("properties/Type").text

        if(type == "Junction" or type == "Surface" or type == "Gate"):
            continue

        if(type == "Lane"):
            id = f.find("properties/Id").text
            lane_type = f.find("properties/LaneType").text
            left_boundary_id = check_appearance(f.find("properties/LeftBoundary/Id"))
            left_boundary_dir = check_appearance(f.find("properties/LeftBoundary/Dir"))
            right_boundary_id = check_appearance(f.find("properties/RightBoundary/Id"))
            right_boundary_dir = check_appearance(f.find("properties/RightBoundary/Dir"))
            predecessor_id = check_appearance(f.find("properties/Predecessors/Id"))
            predecessor_dir = check_appearance(f.find("properties/Predecessors/Dir"))
            successor_id = check_appearance(f.find("properties/Successors/Id"))
            successor_dir = check_appearance(f.find("properties/Successors/Dir"))
            speed_limit = check_appearance(f.find("properties/SpeedLimit"))
            travel_dir = check_appearance(f.find("properties/TravelDir"))

            df_lane.loc[len(df_lane)] = [id, lane_type, left_boundary_id, left_boundary_dir, right_boundary_id, right_boundary_dir, 
                            predecessor_id, predecessor_dir, successor_id, successor_dir, speed_limit, travel_dir, type]

        if(type == "LaneBoundary"):
            id = f.find("properties/Id").text
            print(id)
            left_lane_id = check_appearance(f.find("properties/LeftLane/Id"))
            left_lane_dir = check_appearance(f.find("properties/LeftLane/Dir"))
            right_lane_id = check_appearance(f.find("properties/RightLane/Id"))
            right_lane_dir = check_appearance(f.find("properties/RightLane/Dir"))

            df_boundaries.loc[len(df_boundaries)] = [id, left_lane_id, left_lane_dir, right_lane_id, right_lane_dir, type]

    df_lane.to_csv(output_lane)
    df_boundaries.to_csv(output_boundaries)

export_coordinates('final2.xml', 'coordinates.csv')
export_properties('final2.xml', 'lane_properties.csv', 'boundary_properties.csv')

