# xodr_to_DwMap

---

## Installation

To get started with this repository, follow the steps below to set up the environment and install the required dependencies:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/xodr_to_DwMap.git
   cd xodr_to_DwMap
   conda create --name geopanda python=3.8
   conda activate geopanda
   pip install -r requirements.txt


This repository contains the codebase for converting OpenDRIVE (XODR) file formats to DWMap file formats, which are utilized for storing data in High Definition (HD) maps. The XODR map (in XML format) was originally created and exported using RoadRunner software.

OpenDRIVE provides both an XODR file and a GeoJSON file to describe their HD map. The process begins by converting the GeoJSON file into an XML format. The primary operations are then performed on the XML and XODR files. These files are located in the `data` directory.

The repository is structured into several main components, each serving a distinct purpose in the conversion process:

### `parsegeojson.py`
This script handles the parsing of the GeoJSON file, converting it into an XML format that is compatible with the DWMap conversion process.

### `parsexodr.py`
This script is responsible for parsing the XODR file, extracting the necessary data required for the DWMap format.

### `postprocessing.py`
This module contains functions that transform the data extracted from the XODR file into the specific format needed for DWMap.

### `utilities.py`
This script includes utility functions that facilitate the conversion of coordinates from the XODR format to the DWMap format.

### `writexml.py`
This script writes the final DWMap in XML format, incorporating all the processed data from the previous steps.



