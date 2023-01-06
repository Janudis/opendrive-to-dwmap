# xodr_to_DwMap
---
This repository includes the code that translates an OpenDRIVE (xodr) file format to DWMap file format. These file formats are used to store data for High Definition (HD) maps.
The xodr map (XML format) was created and exported from RoadRunner software.
OpenDRIVE provides a xodr file and a geojson file for descriping their HD map. First we convert the geojson file to a xml file. We work with the xml file and the xodr file. These files can be found in data file.
This repository is divided in 5 parts.

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


