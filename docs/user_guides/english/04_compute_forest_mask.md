## STEP 4: Creation of the forest mask, which defines the area of interest
This step allows you to compute the forest mask and thus define the area of interest.

#### INPUTS
The input parameters are :
- **data_directory**: The path of the output folder in which the forest mask will be written
- **forest_mask_source** : Source of the forest mask, can be "BDFORET" to use the BD Foret of the IGN, "OSO" to use the CESBIO's land use map, the path to a binary raster of 10m resolution with the value 1 on the pixels of interest, or None to not use a forest mask and to extend the area of interest to all pixels
- **dep_path** : Path to a shapefile of French departments containing the insee code in a code_insee field, only useful if forest_mask_source is "BDFORET".
- **bdforet_dirpath** : Path to the folder containing the IGN forest database with one folder per department. Only useful if forest_mask_source is "BDFORET".
- **list_forest_type** : List of forest stand types to be kept in the forest mask, corresponds to the CODE_TFV of the BD Foret. Only useful if forest_mask_source is "BDFORET".
- **path_oso** : Path of the CESBIO's land use raster. Only useful if forest_mask_source is "OSO".
- **list_code_oso**: List of OSO raster values to keep in the forest mask. Only useful if forest_mask_source is "OSO".
- **path_example_raster** : Path of an "example" raster used to know the extent, the projection system, etc... Only useful if there is no TileInfo file in the data_directory created by the previous steps from which this information can be extracted.

#### OUTPUTS
The outputs of this fourth step, in the data_directory folder, are :
- In the folder **ForestMask**, the binary raster Forest_Mask.tif which has the value 1 on the pixels of interest and 0 elsewhere.

## How to use
### From a script

```bash
from fordead.steps.step4_compute_forest_mask import compute_forest_mask
compute_forest_mask(data_directory, 
                    forest_mask_source = <forest_mask_source>, 
                    dep_path = <dep_path>,
                    bdforet_dirpath = <bdforet_dirpath>)
```


### From the command line

```bash
fordead forest_mask [OPTIONS]
```

See detailed documentation on the [site](https://fordead.gitlab.io/fordead_package/docs/cli/#fordead-forest_mask)

## How it works

![Diagramme_step4](Diagrams/Diagramme_step4.png "Diagramme_step4")

### Importing information on previous processes and deleting obsolete results if they exist
The information about the previous steps is imported (parameters, data paths, used dates...). If the parameters used have been modified, all the results from this step onwards are deleted. This step can also be performed independently from the rest of the processing chain, by filling in the **path_example_raster** parameter, in order to obtain a binary forest mask. Otherwise, the **path_example_raster** parameter is automatically extracted from the results of the previous steps so that the forest mask corresponds to the studied area.
> **_Functions used:_** [TileInfo()](https://fordead.gitlab.io/fordead_package/reference/fordead/ImportData/#tileinfo), TileInfo class methods [import_info()](https://fordead.gitlab.io/fordead_package/reference/fordead/ImportData/#import_info), [add_parameters()](https://fordead.gitlab.io/fordead_package/reference/fordead/ImportData/#add_parameters), [delete_dirs()](https://fordead.gitlab.io/fordead_package/reference/fordead/ImportData/#delete_dirs)

### From the IGN BDFORET
- Import of the BDFORET shapefiles of the departments intersecting the study area
- Filtering from the selected forest stand types
- Rasterization as a binary mask
> **_Functions used:_** [rasterize_bdforet()](https://fordead.gitlab.io/fordead_package/reference/fordead/masking_vi/#rasterize_bdforet), [rasterize_polygons_binary()](https://fordead.gitlab.io/fordead_package/reference/fordead/masking_vi/#rasterize_polygons_binary), [bdforet_paths_in_zone()](https://fordead.gitlab.io/fordead_package/reference/fordead/masking_vi/#bdforet_paths_in_zone)

### From CESBIO OSO map
 - Import of the [oso map](http://osr-cesbio.ups-tlse.fr/~oso/) and cropping from the raster at path **path_example_raster**
 - Filter from the **list_code_oso** list so the resulting raster has the value True on the pixels whose value in the OSO map is in the **list_code_oso** list, and False elsewhere.
> **_Functions used:_** [clip_oso()](https://fordead.gitlab.io/fordead_package/reference/fordead/masking_vi/#clip_oso)

### From a binary raster
This option is given for users who want to create their own mask by other means and use it in the processing chain. A copy will be written in the data_directory folder.
 - If forest_mask_source is a path to an existing file, this file is imported. It must be a binary raster file with the value 1 where there are pixels of interest
 - The file is clipped to the extent of the study area, or to the path_example_raster file
> **_Functions used:_** [import_forest_mask()](https://fordead.gitlab.io/fordead_package/reference/fordead/ImportData/#import_forest_mask), [clip_xarray()](https://fordead.gitlab.io/fordead_package/reference/fordead/ImportData/#clip_xarray)

### No mask
If the user chooses not to use a mask, the resulting forest mask is filled entirely with the value True and corresponds to the dimension, resolution and projection system of the raster at the **path_example_raster** path
> **_Functions used:_** [raster_full()](https://fordead.gitlab.io/fordead_package/reference/fordead/masking_vi/#raster_full)

### Writing the results
The forest mask is written, and its path saved in the TileInfo object.
> **_Functions used :_** [write_tif()](https://fordead.gitlab.io/fordead_package/reference/fordead/writing_data/#write_tif), TileInfo method [save_info()](https://fordead.gitlab.io/fordead_package/reference/fordead/ImportData/#save_info)
