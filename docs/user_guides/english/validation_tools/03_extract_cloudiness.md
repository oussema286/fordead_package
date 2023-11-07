# Extracting cloudiness from Sentinel-2 data

# <div align="center"> Extraction of cloudiness from Sentinel-2 data </div>
This step is optionnal if you are extracting data using Planetary, or don't wish to filter acquisitions on cloudiness.
In this step, the percentage of pixels in the mask provided by the Sentinel-2 data provider is extracted for each acquisition.
The results are exported in a csv file
For THEIA, all pixels different to 0 in the CLM mask are considered cloudy
For Scihub and PEPS, all pixels different to 4 or 5 in the SCL mask are considered cloudy

----------
## INPUT PARAMETERS
----------
- sentinel_dir (str) : Path of the directory containing Sentinel-2 data.
- export_path (str) : Path to write csv file with extracted cloudiness.
- tile_selection (list) : List of tiles from which to extract reflectance (ex : ["T31UFQ", "T31UGQ"]). If None, all tiles are extracted.
- sentinel_source (str) : 'THEIA', 'Scihub' or 'PEPS' depending on the Sentinel-2 data provider.

----------
## OUPUT FILE
----------
The results are exported in a csv file, with the columns :
- *area_name* : the name of the Sentinel-2 tile
- *Date* : the date of the Sentinel-2 acquisition
- *cloudiness* : the percentage of cloudy pixels

----------
## Running this step
----------

#### Using a script

```python
from fordead.validation.extract_cloudiness import extract_cloudiness

extract_cloudiness(
	sentinel_dir = <sentinel_dir>, 
	export_path = <export_path>,
	tile_selection = <tile_selection>,
	sentinel_source = <sentinel_source>)
```

#### from the command invite

This step can also be ran from the command prompt. 
```bash
fordead extract_cloudiness [OPTIONS]
```
See detailed documentation for the command line prompt [here](https://fordead.gitlab.io/fordead_package/docs/cli/#fordead-extract_cloudiness)