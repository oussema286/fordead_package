# <div align="center"> Preprocessing observations used for validation </div>

In this step, we will use observation polygons to generate a vector file containing points at the center of each 10m Sentinel-2 pixel inside of the polygons. 
They keep the original polygon ID, and are also given the following attributes :
- **id_pixel**: 
- **name_area** : Name of the associated Sentinel-2 tile 
- **epsg**: CRS of the associated Sentinel-2 tile as the EPSG integer.
They can then be used in the next step to extract Sentinel-2 data at those point locations.

The points generated are kept in the CRS of the original vector file.

##### Running this step using a script

Run the following instructions to perform this preprocessing step:

```python
from fordead.validation.obs_to_s2_grid import obs_to_s2_grid

obs_path = "<MyWorkingDirectory>/vector/observations_tuto.shp"
sentinel_dir = "<MyWorkingDirectory>/sentinel_data/validation_tutorial/sentinel_data/"
preprocessed_obs_path = "<MyWorkingDirectory>/vector/preprocessed_obs_tuto.shp"

obs_to_s2_grid(
	obs_path = obs_path,
	sentinel_dir = sentinel_dir, 
	export_path = preprocessed_obs_path,
	name_column = "id")
```

##### Running this step from the command invite

This step can also be ran from the command prompt. The command `fordead obs_to_s2_grid -h` will print the help information of this step. For example, to use it with the same parameters, the following command can be used:
```bash
fordead obs_to_s2_grid --obs_path <MyWorkingDirectory>/vector/observations_tuto.shp --sentinel_dir <MyWorkingDirectory>/sentinel_data/validation_tutorial/sentinel_data/ --export_path <MyWorkingDirectory>/vector/preprocessed_obs_tuto.shp --name_column id
```

#### OUTPUTS

Running this script will create a new vector file at <MyWorkingDirectory>/vector/preprocessed_obs_tuto.shp containing only points.
Since there is an observation outside of the available Sentinel-2 data, it is removed from the resulting vector and its ID is printed to the console.

Here we can see a view from QGIS zoomed on observation 7, as well as the attribute table.

![points_obs](Figures/points_obs.png "points_obs")


[PREVIOUS PAGE](https://fordead.gitlab.io/fordead_package/docs/Tutorials/Validation/00_Intro) [NEXT PAGE](https://fordead.gitlab.io/fordead_package/docs/Tutorials/Validation/02_extract_reflectance)
