# <div align="center"> Preprocessing observations used for validation </div>

This step aims at connecting the observations to the relevant Sentinel-2 pixels. Information from the intersecting Sentinel-2 tiles are added to the vector of observations. If it contains polygons instead of points, they will be converted to a grid of points corresponding to the centers of each 10 m Sentinel-2 pixel included in the polygon.

Each resulting point includes the following attributes :
- original polygon ID
- **id_pixel**: ID of the pixel
- **name_area** : Name of the corresponding area (e.g. Sentinel-2 tile ID)
- **epsg**: CRS of the associated Sentinel-2 tile as the EPSG integer.

These datapoints are used in the next step to extract Sentinel-2 data.

The points generated are kept in the CRS of the original vector file.

#### Using local THEIA data
##### Running this step using a script

Run the following instructions to perform this preprocessing step:

```python
from pathlib import Path

from fordead.validation.obs_to_s2_grid import obs_to_s2_grid

output_dir = Path("<MyOutputDirectory>")
input_dir = Path("<MyInputDirectory>/fordead_data")

obs_path = input_dir / "vector/observations_tuto.shp"
sentinel_dir = input_dir / "sentinel_data/validation_tutorial/sentinel_data/"
preprocessed_obs_path = output_dir / "preprocessed_obs_tuto.shp"


obs_to_s2_grid(
	obs_path = obs_path,
	sentinel_source = sentinel_dir, 
	export_path = preprocessed_obs_path,
	name_column = "id")
	
```

> **_NOTE :_** Set **obs_to_s2_grid** input variable `overwrite = True` to re-run this processing stage, otherwise it will raise an error.

##### Running this step from the command invite

This step can also be ran from the command prompt. The command `fordead obs_to_s2_grid -h` will print the help information of this step. For example, to use it with the same parameters, the following command can be used:
```bash
fordead obs_to_s2_grid --obs_path <MyWorkingDirectory>/vector/observations_tuto.shp --sentinel_source <MyWorkingDirectory>/sentinel_data/validation_tutorial/sentinel_data/ --export_path <MyWorkingDirectory>/vector/preprocessed_obs_tuto.shp --name_column id
```

#### Using Planetary Computer

##### Running this step using a script

Run the following instructions to perform this preprocessing step:

```python
from pathlib import Path

from fordead.validation.obs_to_s2_grid import obs_to_s2_grid

output_dir = Path("<MyOutputDirectory>")
input_dir = Path("<MyInputDirectory>/fordead_data")

obs_path = input_dir / "vector/observations_tuto.shp"
preprocessed_obs_path = output_dir / "preprocessed_obs_tuto.shp"


obs_to_s2_grid(
	obs_path = obs_path,
	sentinel_source = "Planetary", 
	export_path = preprocessed_obs_path,
	name_column = "id")
	
```

> **_NOTE :_** Set **obs_to_s2_grid** input variable `overwrite = True` to re-run this processing stage, otherwise it will raise an error.

##### Running this step from the command invite

This step can also be ran from the command prompt. The command `fordead obs_to_s2_grid -h` will print the help information of this step. For example, to use it with the same parameters, the following command can be used:
```bash
fordead obs_to_s2_grid --obs_path <MyWorkingDirectory>/vector/observations_tuto.shp --sentinel_source Planetary --export_path <MyWorkingDirectory>/vector/preprocessed_obs_tuto.shp --name_column id
```

#### OUTPUTS

The vector file containing only points is written in the file **fordead_data/vector/preprocessed_obs_tuto.shp** given by the parameter *preprocessed_obs_path*.

Observations outside of the footprint of the Sentinel-2 data are removed from the resulting vector and their ID printed in the command prompt. 

The observations vector's polygons for this tutorial are inside two overlapping Sentinel-2 tiles, T31UGP and T32ULU. THEIA data for this tutoriel only contains data from T31UGP, but if Planetary is used as a source, points will be created for each tile unless  `tile_selection = ["T31UGP"]` is specified for example.

The following figure shows a zoomed view on observation 7 with Sentinel-2 THEIA data.

![points_obs](Figures/points_obs.png "points_obs")


> **_NOTE :_** If the initial vector file contains points, their locations are preserved and their id_pixel attribute is set to 1.


