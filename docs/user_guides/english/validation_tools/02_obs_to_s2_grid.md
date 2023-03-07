This step aims at attributing intersecting Sentinel-2 tiles to observation points or polygons, adding the corresponding *epsg* and *name*. If polygons are used, they are converted to grid points located at the centroid of Sentinel-2 pixels.
If points or polygons intersect several Sentinel-2 tiles, they are duplicated for each of them.
If some intersect no Sentinel-2 tiles, they are removed and their IDs are printed.

#### INPUTS

The input parameters are :

- **obs_path** : Path to a vector file containing observation points or polygons, must have an ID column corresponding to name_column parameter.
- **sentinel_dir** : Path of the directory containing Sentinel-2 data.
- **export_path** : Path used to write resulting vector file, with added *epsg*, *area_name* and *id_pixel* columns.
- **name_column** : Name of the ID column. The default is *id*.
- **list_tiles** (*optional*): A list of names of Sentinel-2 directories. If this parameter is used, extraction is  limited to those directories.
- **overwrite** : If **True**, allows overwriting of file at *obs_path*. The default is **False**.

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


### Creating a Sentinel-2 tiles extent vector from existing Sentinel-2 data
- Available Sentinel-2 tiles in the **sentinel_dir** directory are listed
- The extent of each listed Sentinel-2 tiles is extracted and converted to a GeoDataFrame 
- Each GeoDataFrame is given the attributes *area_name* and *epsg*, corresponding to the name of the directory containing the tile data, and the epsg of the tile.
- All GeoDataFrames are concatenated
 > **_Function used:_** [get_polygons_from_sentinel_dirs()](https://fordead.gitlab.io/fordead_package/reference/fordead/validation_module/#get_polygons_from_sentinel_dirs)

### If vector file at **obs_path** contains points :
 - Observation points are intersected with the Sentinel-2 tiles extent vector, transfering the attributes *area_name* and *epsg*
 - An *id_pixel* column is added and filled with 0 so the resulting vector can be used in [export_reflectance function]().
 - Points outside of available Sentinel-2 tiles are detected and their IDs are printed.
 > **_Function used:_** [get_sen_intersection_points()](https://fordead.gitlab.io/fordead_package/reference/fordead/validation_module/#get_sen_intersection_points)

