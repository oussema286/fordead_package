## Extracting reflectance from Sentinel-2 data

This step aims at extracting reflectance from Sentinel-2 data using a vector file containing points and exporting the data to a csv file. 
If new acquisitions are added to the Sentinel-2 directory, new data is extracted and added to the existing csv file.

#### INPUTS

The input parameters are :

- **obs_path** : The path to a vector file containing observation points, must have an ID column corresponding to name_column parameter, an 'area_name' column with the name of the Sentinel-2 tile from which to extract reflectance, and a 'espg' column containing the espg integer corresponding to the CRS of the Sentinel-2 tile.
- **sentinel_source** :  Can be either 'Planetary', in which case data is downloaded from Microsoft Planetary Computer stac catalogs, or the path of the directory containing Sentinel-2 data.
- **export_path** : The path to write csv file with extracted reflectance.
- **name_column** *(optional)* : The name of the ID column. The default is "id".
- **cloudiness_path** *(optional)* : Path of a csv with the columns 'area_name','Date' and 'cloudiness', can be calculated by the [extract_cloudiness function](https://fordead.gitlab.io/fordead_package/docs/Tutorials/Validation/03_extract_cloudiness/). Can be ignored if sentinel_source is 'Planetary'
- **lim_perc_cloud**  *(optional)* : Maximum cloudiness at the tile scale, used to filter used SENTINEL dates. Between 0 and 1.
- **bands_to_extract** *(optional)* : List of bands to extract (ex : ["B1","B8A","Mask"]) The "Mask" band corresponds to "CLM" for THEIA data, and "SCL" for Planetary.
- **tile_selection** *(optional)* : List of tiles from which to extract reflectance (ex : ["T31UFQ", "T31UGQ"]). If None, all tiles are extracted.
- **start_date** *(optional)* : First date of the period from which to extract reflectance
- **end_date** *(optional)* : Last date of the period from which to extract reflectance

#### OUTPUT

The output is a csv file at **export_path**. 
It contains the following columns :
- **epsg** : The CRS of the Sentinel-2 tile from which data was extracted
- **area_name** : The name of the Sentinel-2 tile from which data was extracted
- an ID column corresponding to the **name_column** parameter
- **id_pixel** : The ID of the pixel whose centroid is at the point location in 10m Sentinel data in the corresponding epsg. *id_pixel* goes from 1 to the number of pixels in the observation.
- **Date** : Date of the Sentinel-2 acquisition
- One column for each band in the **bands_to_extract** list containg the value extracted from Sentinel-2 data.

## How to use
### From a script

```bash
from fordead.validation.extract_reflectance import extract_reflectance

extract_reflectance(obs_path = <obs_path>, export_path = <export_path>, name_column = <name_column>)

```

### From the command line

```bash
fordead extract_reflectance [OPTIONS]
```

See detailed documentation on the [site](https://fordead.gitlab.io/fordead_package/docs/cli/#fordead-extract_reflectance)

## How does it work ?

### Importing the vector file containing points used as extraction locations
The vector file at **obs_path** is imported using the geopandas package.

### Importing already extracted data if it exists
- If a file already exists at **export_path**, it is imported.
- If changes in last extraction's number of observations are detected, a message is printed to the console and the user is asked if they want to continue. This can prevent issues in case the user uses the wrong **obs_path** or **export_path** by mistake.
> **_Function used:_** [get_already_extracted()](docs/API_Reference/fordead/reflectance_extraction/#get_already_extracted)

### Extracting reflectance from Sentinel-2 data
- For each Sentinel-2 tile (*area_name*) in observation points
	- An item collection is created either from Microsoft Planetary Computer, or from local THEIA data depending on **sentinel_source**.
	-  For each Sentinel-2 acquisition and for each band in **bands_to_extract** list
		 Reflectance is extracted if it was not already done
> **_Function used:_** [extract_raster_values()](docs/API_Reference/fordead/reflectance_extraction/#extract_raster_values), [get_harmonized_planetary_collection()](docs/API_Reference/fordead/stac/stac_module/#get_harmonized_planetary_collection), [get_harmonized_theia_collection()](docs/API_Reference/fordead/stac/stac_module/#get_harmonized_theia_collection)

### Exporting extracted reflectance
Extracted reflectance is written at **export_path**. 
If the file already exists, new data is added to the already existing file.
