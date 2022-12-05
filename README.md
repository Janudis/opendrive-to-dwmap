# xodr_to_DwMap
---
This repository includes the code that translates an OpenDRIVE (xodr) HD map to DwMap HD map.
The xodr map (XML format) was created and exported from RoadRunner software.
OpenDRIVE provides a xodr file and a geojson file for descriping their HD map. This repository is divided in 5 parts.

# parsegeojson.py
Parse the geojson file.

# parsexodr.py
Parse the xodr file.

# postprocessing.py
Create the functions that convert the information of xodr to the type needed in DwMap format.

# utilies.py
Create the functions that convert the coordinates of xodr to DwMap.

# writexml.py
Write the DWMap xml.


