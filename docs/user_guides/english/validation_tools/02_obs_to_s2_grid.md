# Matching with available Sentinel-2 data

This step aims at matching observation data with either available Sentinel-2 tiles or Sentinel-2 infered from Microsoft Planetary Computer item collections.
The resulting vector can be used to extract the matching Sentinel-2 data using the [extraction function](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/validation_tools/04_extract_reflectance/).
If polygons are used, they are converted to grid points located at the centroid of 10m Sentinel-2 pixels.

If points or polygons intersect several Sentinel-2 tiles, the resulting points are duplicated for each of them.
Observation polygons which are not contained in a Sentinel-2 tile, or are too small to contain a pixel centroid are removed and their IDs are printed to the console.

#### INPUTS

The input parameters are :

- **obs_path** : Path to a vector file containing observation points or polygons, must have an ID column corresponding to name_column parameter.
- **sentinel_source** : Can be either 'Planetary', in which case the Sentinel-2 grid is infered from Microsoft Planetary Computer stac catalogs, or the path of the directory containing Sentinel-2 data.
- **export_path** : Path used to write resulting vector file, with added *epsg*, *area_name* and *id_pixel* columns.
- **name_column** (*optional*) : Name of the ID column. The default is *id*.
- **tile_selection** (*optional*) : A list of names of Sentinel-2 directories. If this parameter is used, extraction is  limited to those directories.
- **overwrite** (*optional*) : If **True**, allows overwriting of file at *obs_path*. The default is **False**.

#### OUTPUT

The output is a vector file at **export_path** containing points for each 10m Sentinel-2 pixel of available tiles at the location of points, or contained in the polygons in the vector file at **obs_path**. 
The following attributes are added :
- *area_name* : The name of the matching Sentinel-2 tile, parsed from its directory name in **sentinel_source** or extracted from the item collection.
- *epsg* : The CRS of the matching Sentinel-2 tile
- *id_pixel* : The ID of the pixel whose centroid is at the point location in 10m Sentinel data in the corresponding epsg. *id_pixel* goes from 1 to the number of pixels in the observation.

> **_NOTE :_** Since observation polygons can be in overlapping Sentinel-2 tiles with different CRS. One needs to use *name_column* and *id_pixel* as well as *epsg* to identify a unique point location (and therefore Sentinel-2 pixel).

## How to use
### From a script

```bash
from fordead.validation.obs_to_s2_grid import obs_to_s2_grid

obs_to_s2_grid(obs_path = <obs_path>, export_path = <export_path>, name_column = <name_column>)

```

### From the command line

```bash
fordead obs_to_s2_grid [OPTIONS]
```

See detailed documentation on the [site](https://fordead.gitlab.io/fordead_package/docs/cli/#fordead-obs_to_s2_grid)

## How it works

### Importing the vector file containing observations
The vector file at **obs_path** is imported using the geopandas package.


### Creating a Sentinel-2 tiles extent vector
#### If sentinel_source is a directory containing Sentinel-2  data
- If using local Sentinel-2 data :
	- Available Sentinel-2 tiles in the **sentinel_source** directory are listed
	- The extent of each listed Sentinel-2 tiles is extracted and converted to a GeoDataFrame 
- If using Planetary :
	- The extent of Sentinel-2 tiles are extracted from the full collection and converted to a GeoDataFrame 
- Each GeoDataFrame is given the attributes *area_name* and *epsg*, corresponding to the name of the directory containing the tile data, and the epsg of the tile.
- All GeoDataFrames are concatenated
 > **_Function used:_** [get_polygons_from_sentinel_dirs()](https://fordead.gitlab.io/fordead_package/reference/fordead/reflectance_extraction/#get_polygons_from_sentinel_dirs)
#### If sentinel_source is "Planetary"
- An item collection is retrieved from Microsoft Planetary Computer
- The tile corners are extracted from the item collection geometries and converted to a GeoDataFrame with the attributes *area_name* and *epsg*.
 > **_Functions used:_** [get_harmonized_planetary_collection()](https://fordead.gitlab.io/fordead_package/reference/fordead/stac/stac_module/#get_harmonized_planetary_collection), [get_polygons_from_sentinel_planetComp()](https://fordead.gitlab.io/fordead_package/reference/fordead/reflectance_extraction/#get_polygons_from_sentinel_planetComp)

### If vector file at **obs_path** contains points :
 - Observation points are intersected with the Sentinel-2 tiles extent vector, transferring the attributes *area_name* and *epsg*
 - An *id_pixel* column is added and filled with 0 so the resulting vector can be used in the [export_reflectance](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/validation_tools/04_extract_reflectance/) function.
 - Points outside of available Sentinel-2 tiles are detected and their IDs are printed.
 > **_Function used:_** [get_sen_intersection_points()](https://fordead.gitlab.io/fordead_package/reference/fordead/reflectance_extraction/#get_sen_intersection_points)

### If vector file at **obs_path** contains polygons :

#### Matching observation polygons with Sentinel-2 tiles
- Observation polygons are overlaid with the Sentinel-2 tiles extent vector, transferring the 'area_name' and 'epsg' columns corresponding to the name of the tile, and the projection system respectively
- Observation polygons which are not contained in a Sentinel-2 tile are removed, their IDs are printed to the console.
> **_Function used:_** [get_sen_intersection()](https://fordead.gitlab.io/fordead_package/reference/fordead/reflectance_extraction/#get_sen_intersection)

#### Generating points for pixels inside the polygons
- For each polygon, points are generated in a grid corresponding to the centroids of Sentinel-2 pixels inside the polygon.
- They are given the attributes
- Polygons with no pixels centroids inside of them have their IDs printed to the console.
 > **_Function used:_** [polygons_to_grid_points()](https://fordead.gitlab.io/fordead_package/reference/fordead/reflectance_extraction/#polygons_to_grid_points)
 
###  Exporting the resulting the vector file
The resulting points are exported to **export_path**.

