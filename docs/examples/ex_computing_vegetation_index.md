The following code describe a simple script to compute a temporal series of vegetation index using SENTINEL-2 imagery.

The first step is to import the relevant functions from the modules
```bash
from fordead.import_data import TileInfo, get_band_paths, import_resampled_sen_stack
from fordead.masking_vi import compute_vegetation_index
from fordead.writing_data import write_tif
```

Then define the path of the directory containing SENTINEL data, and path of the output directory, where the vegetation index series will be written. The input directory must contain one directory for each date, containing one file for each band. The date must be in the directory name in any of the following formats :
- YYYY-MM-DD
- YYYY_MM_DD
- YYYYMMDD
- DD-MM-YYYY
- DD_MM_YYYY
- DDMMYYYY

The band name must be in the file name (B2 or B02, B3 or B03, B4 or B04, B5 or B05, B6 or B06, B7 or B07, B8 or B08, B8A, B11, B12).
```bash
input_directory = "<input_directory>"
output_directory = "<output_directory>"
```
Then a TileInfo object can be created, to which the relevant information will be added (Dates in the directory, paths to the directories and files, and so on)
```bash
tile = TileInfo(output_directory)
```
Then, the paths to all the band files will be added to the TileInfo object. It adds a dictionnary to tile.paths with key "Sentinel" and with value another dictionnary where keys are ordered and formatted dates and values are the paths to the directories containing the different bands. The paths to the directories are then replaced with yet another dictionnary where the key is the name of the band, and the value is the file path. For example, the path to the band B2 of the SENTINEL date "2017-05-01" can then be retrieved using `tile.paths["SENTINEL"]["2017-05-01"]["B2"]`.
```bash
tile.getdict_datepaths(key = "Sentinel", path_dir = input_directory)
tile.paths["Sentinel"] = get_band_paths(tile.paths["Sentinel"])
``` 

Output directories are then created and their paths are added to the TileInfo object. All parent directories are created if missing.
```bash
tile.add_dirpath(key = "VegetationIndexDir", path = tile.data_directory / "VegetationIndex")
``` 
In this example, a directory named "VegetationIndex" is created in the output directory (tile.data_directory corresponds to the path given when creating the TileInfo object). This way of defining the path is permitted by the use of pathlib's Path class. The path of the directory containing computed vegetation indices can then be retrieved using `tile.paths["VegetationIndexDir"]`.

Then, for each date the chosen bands are resampled at 10m resolution if needed and imported as an xarray :
```bash
for date in tile.paths["Sentinel"]:
    print(date)
    
    stack_bands = import_resampled_sen_stack(tile.paths["Sentinel"][date], ["B8","B4"])
``` 

And the vegetation index is calculated :
```bash
    vegetation_index = compute_vegetation_index(stack_bands, formula = "(B8-B4)/(B8+B4)")
``` 
Then the computed vegetation_index can be written on the disk :
```bash
    write_tif(vegetation_index, stack_bands.attrs,tile.paths["VegetationIndexDir"] / ("VegetationIndex_"+date+".tif"),nodata=0)
``` 

## Complete script

```bash
from fordead.import_data import TileInfo, get_band_paths, import_resampled_sen_stack
from fordead.masking_vi import compute_vegetation_index
from fordead.writing_data import write_tif

input_directory = "<input_directory>"
output_directory = "<output_directory>"

tile = TileInfo(output_directory)
tile.getdict_datepaths(key = "Sentinel", path_dir = input_directory)
tile.paths["Sentinel"] = get_band_paths(tile.paths["Sentinel"])
tile.add_dirpath(key = "VegetationIndexDir", path = tile.data_directory / "VegetationIndex")

for date in tile.paths["Sentinel"]:
    print(date)
    stack_bands = import_resampled_sen_stack(tile.paths["Sentinel"][date], ["B8","B4"])
    vegetation_index = compute_vegetation_index(stack_bands, formula = "(B8-B4)/(B8+B4)")
    write_tif(vegetation_index, stack_bands.attrs,tile.paths["VegetationIndexDir"] / ("VegetationIndex_"+date+".tif"),nodata=0)
``` 
