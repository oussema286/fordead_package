# <div align="center"> Preprocessing observations used for validation </div>

To extract Sentinel-2 data from the polygons, they must first be converted to points corresponding to the Sentinel-2 pixels with their centroid inside the polygon. If a polygon is contained in several Sentinel-2 tiles, a set of point is generated for each tile. The points are located at the center of the pixels, are given an ID are and associated with the name of the tile, and its CRS. Two points can have the same IDs, but have different locations if they are associated with two tiles of different CRS.
Since, we chose an area intersecting two Sentinel-2 tiles, T31UGP and T32ULU, this is what will happen in this tutorial.

##### Running this step using a script

Run the following instructions to perform this preprocessing step:

```python
from fordead.validation.obs_to_s2_grid import obs_to_s2_grid

obs_path = "<MyWorkingDirectory>/vector/observations_tuto.shp"
sentinel_dir = "<MyWorkingDirectory>/sentinel_data/validation_tutorial/sentinel_data/"
preprocessed_obs_path = "<MyWorkingDirectory>/vector/preprocessed_obs_tuto.shp"
name_column = "id"

obs_to_s2_grid(
	obs_path = obs_path,
	sentinel_dir = sentinel_dir, 
	export_path = preprocessed_obs_path,
	name_column = "id")
```

##### Running this step from the command invite

This step can also be ran from the command prompt. The command `fordead masked_vi -h` will print the help information of this step. For example, to use it with the same parameters, the following command can be used:
```bash
fordead obs_to_s2_grid --obs_path <MyWorkingDirectory>/vector/observations_tuto.shp --sentinel_dir <MyWorkingDirectory>/sentinel_data/validation_tutorial/sentinel_data/ --export_path <MyWorkingDirectory>/vector/preprocessed_obs_tuto.shp --name_column id
```


As we can see from the attribute table and a view from QGIS zoomed on observation 7, the attributes "epsg", "area_name", and "id_pixel" were added, linking each point with a Sentinel-2 tile.
![preprocessed_obs](Figures/preprocessed_obs.png "preprocessed_obs")  |  ![preprocessed_obs](Figures/preprocessed_obs.png "preprocessed_obs")

That way the points are at the centroid of their corresponding Sentinel-2 pixel before they are clipped by the observation polygon. Here is another illustration of the resulting points, with the other Sentinel-2 tile T32ULU instead of T31UGP as background.
![preprocessed_obs_T32ULU](Figures/preprocessed_obs_T32ULU.png "preprocessed_obs_T32ULU")

[PREVIOUS PAGE](https://fordead.gitlab.io/fordead_package/docs/Tutorials/Validation/00_Intro) [NEXT PAGE](https://fordead.gitlab.io/fordead_package/docs/Tutorials/Validation/02_extract_reflectance)
