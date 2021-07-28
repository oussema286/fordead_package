# STEP 1: Compute vegetation indices and masks for each SENTINEL-2 date

#### INPUTS
The input parameters are:

- **input_directory**: the path of the folder corresponding to a tile or area containing a folder for each SENTINEL date containing a file for each band. The folders must contain the corresponding date in their name in one of the following formats: YYYY-MM-DD, YYYY_MM_DD, YYYYMMDD, DD-MM-YYYY, DD_MM_YYYY or DDMMYYYY. The band files must contain the name of the corresponding band (B2 or B02, B3 or B03, etc.).
- **data_directory**: The path of the output folder, in which the vegetation indices and masks will be written
- **lim_perc_cloud** : The maximum percentage of clouds. If the cloudiness percentage of the SENTINEL date, calculated from the provider's classification, is higher than this threshold, the date is ignored. If set to -1, all dates are used regardless of their cloudiness, and the provider's mask is not needed.
- **interpolation_order** : Interpolation order for the conversion of the bands from a 20m resolution to a 10m resolution. 0 : nearest neighbor, 1 : linear, 2 : bilinear, 3 : cubic
- **sentinel_source** : Provider of the data among 'THEIA' and 'Scihub' and 'PEPS'.
- **apply_source_mask** : If True, the mask of the provider is also used to mask the data
- **vi** : Vegetation index used
- **extent_shape_path** : Path of a shapefile containing a polygon used to restrict the calculation to an area. If not provided, the calculation is applied to the whole tile
- **path_dict_vi** : Path to a text file used to add potential vegetation indices. If not filled in, only the indices provided in the package can be used (CRSWIR, NDVI, NDWI). The file examples/ex_dict_vi.txt gives the example of the formatting of this file. You have to fill in its name, its formula, and "+" or "-" according to whether the index increases in case of depletion, or if it decreases.

Note : **input_directory** and **data_directory** have no default value and must be filled in. The **sentinel_source** must correspond to the provider of your data. The package has been almost exclusively tested with THEIA data.

#### OUTPUTS
The outputs of this first step, in the data_directory folder, are :
- A TileInfo file which contains information about the studied area, dates used, raster paths... It is imported by the following steps for reuse of this information.
- In the **VegetationIndex** folder, a raster for each date where the vegetation index is calculated for each pixel
- In the **Mask** folder, a binary raster for each date where the masked pixels are 1, and the valid pixels are 0.
- In the **DataSoil** folder, three rasters:
    - **count_soil** : the number of successive dates with soil anomalies
    - **first_date_soil**: The index of the first date with a soil anomaly in the last set of soil anomalies
    - state_soil**: A binary raster that is worth 1 if the pixel is detected as soil (at least three successive soil anomalies)
From state_soil and first_date_soil, it is therefore possible to know which pixels are detected as bare soil/cutting, and from which date. count_soil allows to update these data by adding new SENTINEL dates.

## Usage
### From a script

```bash
from fordead.steps.step1_compute_masked_vegetationindex import compute_masked_vegetationindex
compute_masked_vegetationindex(input_directory = <input_directory>, data_directory = <data_directory>)
```

### From the command line

```bash
fordead masked_vi [OPTIONS]
```

See detailed documentation on the [site](https://fordead.gitlab.io/fordead_package/docs/cli/#fordead-masked_vi)

## Detail of the operation

![Diagram_step1](Diagrams/Diagram_step1.png "Diagram_step1")

### Import of previous results, deletion of obsolete results 
The information related to the previous treatments is imported (parameters, data paths, used dates...). If the parameters used have been modified, all the results from this step onwards are deleted. Thus, unless the parameters have been modified, only the following calculations are performed on the new SENTINEL dates.
**_Functions used:_** [TileInfo()](https://fordead.gitlab.io/fordead_package/reference/fordead/ImportData/#tileinfo), methods of the TileInfo class [import_info()](https://fordead.gitlab.io/fordead_package/reference/fordead/ImportData/#import_info), [add_parameters()](https://fordead.gitlab.io/fordead_package/reference/fordead/ImportData/#add_parameters), [delete_dirs()](https://fordead.gitlab.io/fordead_package/reference/fordead/ImportData/#delete_dirs)

### Filtering out overly cloudy dates
The cloudiness of each SENTINEL date is calculated from the supplier mask.
> Functions used:_** [get_cloudiness()](https://fordead.gitlab.io/fordead_package/reference/fordead/ImportData/#get_cloudiness), [get_date_cloudiness_perc()](https://fordead.gitlab.io/fordead_package/reference/fordead/ImportData/#get_date_cloudiness_perc)

We then use only the new dates in the **input_directory** folder with a resolution lower than **lim_perc_cloud**.

### Import and resampling of the SENTINEL data
 - The interest bands of these dates are imported and resampled to 10m 
> Functions used:_** [import_resampled_sen_stack()](https://fordead.gitlab.io/fordead_package/reference/fordead/ImportData/#import_resampled_sen_stack)

### Mask creation
The creation of the mask for each date is done in four steps:
 > **_Functions used :_** [compute_masks()](https://fordead.gitlab.io/fordead_package/reference/fordead/masking_vi/#compute_masks)

##### Creation of the premask
Detection of soil anomalies : (B11 > 1250) AND (B2 < 600) AND ((B3 + B4) > 800)
Detection of shadows: 0 in any of the bands
Detection of areas outside the satellite swath: Value less than 0 in any of the bands (normally worth -10000 for THEIA data) 
Invalids : aggregation of shadows, out of swath and very marked clouds (B2 >= 600)
 **_Functions used:_** [get_pre_masks()](https://fordead.gitlab.io/fordead_package/reference/fordead/masking_vi/#get_pre_masks)

##### Bare ground detection
Three consecutive dates with soil anomalies (soil_anomaly is True) and invalid dates (invalid is True)
 **_Functions used:_** [detect_soil()](https://fordead.gitlab.io/fordead_package/reference/fordead/masking_vi/#detect_soil)

##### Cloud detection
To detect clouds, we take the set of well marked clouds (B2 > 700)
We add the thinner clouds $`\frac{B3}{B8A+B4+B3} >0.15`$ AND $`B2 >400`$ by removing the pixels detected as bare ground or ground anomaly with which there may be confusion. Then we operate a dilation of three pixels to recover the edges of the clouds.
 > **_Functions used:_** [detect_clouds()](https://fordead.gitlab.io/fordead_package/reference/fordead/masking_vi/#detect_clouds)

##### Aggregation of masks
Aggregate shadows, clouds, out of swath pixels, bare ground, bare ground anomalies.
If **apply_source_mask** is True, the source mask is also applied.
 **_Functions used:_** [get_source_mask()](https://fordead.gitlab.io/fordead_package/reference/fordead/masking_vi/#get_source_mask)

### Calculation of the vegetation index
The selected vegetation index is calculated.
 > **_Functions used :_** [compute_vegetation_index()](https://fordead.gitlab.io/fordead_package/reference/fordead/masking_vi/#compute_vegetation_index)

### Writing the results
The vegetation indices, masks and ground detection data are written. All parameters, data paths and dates used are also saved.
 **_Functions used:_** [write_tif()](https://fordead.gitlab.io/fordead_package/reference/fordead/writing_data/#write_tif), TileInfo method [save_info()](https://fordead.gitlab.io/fordead_package/reference/fordead/ImportData/#save_info)
