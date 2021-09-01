# <div align="center"> Detection of forest disturbance using the package _fordead_ </div>

This tutorial will walk you through the use of the package _fordead_, a python package developed to perform pixelwise analysis of Sentinel-2 time series and automatically identify anomalies in forest seasonality. 

## Requirements
### Package installation 
If the package is not already installed, follow the instructions of the [installation guide](https://fordead.gitlab.io/fordead_package/). 
If it is already installed, simply launch the command prompt and activate the environment with the command `conda activate <environment name>`

### Downloading the tutorial dataset

The analysis can be performed at the scale of a Sentinel tile, but for this tutorial we will focus on a small area of study, with coniferous forest stands infested with bark beetles. The related dataset can be downloaded from the [fordead_data repository](https://gitlab.com/fordead/fordead_data). It mainly contains unpacked Sentinel-2 data from the launch of the first satellite to summer 2019. 

## Creation of a script to detect bark beetle related forest disturbance in a given area using the fordead package

#### Step 1 : Computing the spectral index and a mask for each SENTINEL-2 date

The first step is to calculate the vegetation index and a mask for each date. The mask corresponds to pixels that should not be used throughout the rest of the detection steps. Sentinel-2 data will simply be recognized by the algorithm, as long as in the **input_directory**, each directory corresponds to a Sentinel-2 date, with the corresponding date in its name. In those directories, there should be a file for each Sentinel-2 band with the band name in the file name (B2 or B02, and so on...).
You can find the guide for this step [here](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/01_compute_masked_vegetationindex/).

##### Running this step using a script

```python
from fordead.steps.step1_compute_masked_vegetationindex import compute_masked_vegetationindex
input_directory = "<MyWorkingDirectory>/study_area"
data_directory = "<output directory>"

compute_masked_vegetationindex(input_directory = input_directory, data_directory = data_directory, lim_perc_cloud = 0.4, interpolation_order = 0, sentinel_source  = "THEIA", soil_detection = False, formula_mask = "B2 > 600", vi = "NDWI", apply_source_mask = True)
```

As you can see, this step includes many options, although only the **input_directory** and **data_directory** parameters don't have a default value, and the **sentinel_source** has to correspond to your data provider ("THEIA","Scihub" or "PEPS").

##### Outputs

Running this script will filter out all Sentinel-2 dates with a cloud percentage above **lim_perc_cloud**, and create two directories in your **data_directory** :
- A "VegetationIndex" directory, containing the chosen vegetation index (in this case, NDWI) calculated for each remaining date using Sentinel-2 data interpolated at 10m resolution (in this case, `interpolation_order = 0` indicates nearest neighbour interpolation).
- A "Mask" directory, containing the associated binary raster mask which corresponds to the two default masks (any negative value in the first band of the stack is considered outside the satellite swath and any pixel with a 0 value in any band is considered a shadow) associated to the **formula_mask** which is chosen by the user, as well as the mask provided by the Sentinel-2 data provider if **apply_source_mask** is True.

Any logical operation formula can be used in **formula_mask** (see [compute_vegetation_index](https://fordead.gitlab.io/fordead_package/reference/fordead/masking_vi/#compute_vegetation_index)), although it is only used if **soil_detection** is False. If **soil_detection** is True, then the masks include bare ground detection as describe in the [step guide](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/01_compute_masked_vegetationindex/), which can be useful but has only been tested on THEIA data on France's coniferous forests and might not be adapted to other contexts and types of data. This package has been used in France to map bark beetle infested stands, in which context this bare ground detection has been useful to filter out clear cuts, deciduous forests as well as late stage bark beetle infested forest stands. This option is described in the step guide, but will not be exploited in this tutorial.

##### Running this step from the command invite

The steps in this package can also be ran from the command invite. The command `fordead masked_vi -h` will be print the help information on this step. For example, to use it with the same parameters, one can use the following command :
```bash
fordead masked_vi -i <MyWorkingDirectory>/study_area -o <output directory> -n 0.4 --interpolation_order 0 --sentinel_source THEIA --formula_mask "(B2 > 600)" --vi NDWI --apply_source_mask
```
Note that if the same parameters are used, the Sentinel-2 dates already computed are ignored. However, if you change any parameter, all previous results are deleted and calculated again. If new Sentinel-2 data are added in the **input_directory**, it is computed as long as it is more recent than the last computed Sentinel-2 date. This way of saving information on previous processes and paths is done using fordead's [TileInfo](https://fordead.gitlab.io/fordead_package/docs/examples/ex_tileinfo_object/) class, of which an object is saved in the data_directory and is retrieved each time a process is launched.

#### Step 2 : Training a vegetation index model pixel by pixel from the first dates

In this second step, early Sentinel-2 dates are considered representative of the normal seasonal behavior of the vegetation index, thus they are used to compute a model of the vegetation index which can then be used to predict its expected value at any date of the year. Such a model probably depends on many factors, forest density, composition, topography, and so on... So a different model is computed for each pixel to take these differences into account. The periodic model used to fit the training dates is the following:
```math
a1 + b1\sin{\frac{2\pi t}{T}} + b2\cos{\frac{2\pi t}{T}} + b3\sin{\frac{4\pi t}{T}} + b4\cos{\frac{4\pi t}{T}}
```
This step's complete guide can be found [here](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/02_train_model/).

##### Running this step using a script

To run this step, simply add the following lines to the script :
```python
from fordead.steps.step2_train_model import train_model
train_model(data_directory = data_directory, nb_min_date = 10, min_last_date_training="2018-01-01", max_last_date_training="2018-06-01")
```

The model will be trained on all Sentinel-2 dates until **min_last_date_training**. If there are not **nb_min_date** valid dates on **min_last_date_training**, the first **nb_min_date** valid dates are used unless this number is not reach at **max_last_date_training** in which case the pixel is dropped and no model will be calculated. This allows, for example in the case of a relatively ancient source of anomalies such as the bark beetle crisis, to start the detection as early as 2018 if there are enough valid dates at the beginning of the year, while allowing the study of pixels in situations with less data available simply by performing the training over a longer period to retrieve other valid dates. 

It is not recommended to end the training before 2018, because since the periodic model is annual, the use of at least two years of SENTINEL-2 data is advised.

This step can also be used if you skipped the first step and computed a vegetation index and a mask for each date through your own means, simply by filling in the parameters **path_vi** and **path_masks** with the corresponding directories.

##### Outputs

The outputs of this second step, in the data_directory folder, are:
- In the **DataModel** folder, two files:
    - **first_detection_date_index.tif**, a raster that contains the index of the first date that will be used for detection. It allows to know for each pixel which dates were used for training and which ones are used for detection.
    - **coeff_model.tif**, a stack with 5 bands, one for each coefficient of the vegetation index model.
- In the **ForestMask** directory, the binary raster **valid_area_mask.tif** which is 1 for pixels where the model could be computed, 0 if there were not enough valid dates.

##### Running this step from the command invite

This step can also be used from the command invite with the command :

```bash
fordead train_model -o <output directory> --nb_min_date 10 --min_last_date_training 2018-01-01 --max_last_date_training 2018-06-01
```
Again, if the model is already computed and no parameters were changed, the process is ignored. If parameters were changed, previous results from this step and subsequent steps are deleted and the model is computed anew.

#### Step 3 : Detecting anomalies by comparing the vegetation index and its predicted value

For each SENTINEL date not used for training, the actual vegetation index is compared to the vegetation index predicted from the model calculated in the previous step. If the difference exceeds a threshold, in the expected direction in case of anomaly, an anomaly is detected. For example, the NDWI goes down as stands suffer bark beetle attacks, so only low NDWI anomalies are registered. The pixel's state is only considered changed if three successive anomalies are detected, confirming them. This allows to ignore one time events of anomalies due to an imperfect mask, or temporary climatic events. If after anomalies have been confirmed, the pixel has three successive dates without anomalies, it returns to normal state. This allows the algorithm to auto-correct false detections based on new Sentinel-2 data, for example in the case of a drought period lasting long enough to get more than three successive anomalies.

This step's complete guide can be found [here](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/03_decline_detection/).

##### Running this step using a script

To run this step, simply add the following lines to the script :
```python
from fordead.steps.step3_decline_detection import decline_detection
decline_detection(data_directory = data_directory, threshold_anomaly = 0.16)
```

##### Outputs

The outputs of this step, in the data_directory folder, are :
- In the **DataDecline** folder, three rasters:
    - **count_decline** : the number of successive dates with anomalies
    - **first_date_decline**: The index of the first date with an anomaly in the last series of anomalies
    - **state_decline**: A binary raster whose value is 1 if the pixel is detected as declining (at least three successive anomalies)
- In the **DataAnomalies** folder, a raster for each date **Anomalies_YYYY-MM-DD.tif** whose value is 1 where anomalies are detected.

##### Running this step from the command invite

This step can also be used from the command invite with the command :
```bash
fordead decline_detection -o <output directory> --threshold_anomaly 0.17
```
As always, if the model is already computed and no parameters were changed, the process is ignored. If parameters were changed, previous results from this step and subsequent steps are deleted and the model is computed anew.

#### Step 4 : Creating a forest mask, which defines the areas of interest

The previous steps compute results on every pixel, but to export results, it will become necessary to restrict the area of study to the vegetation of interest, in our case resinous forests. This steps aims at computing and saving a binary raster which will then be used to filter out pixels outside of these areas of interest. This can be done using a vector, which will be rasterized, or a binary raster which will be clipped but still needs to have the same resolution, and be aligned with the Sentinel-2 data, or no mask can be used. Other options are tied to data specific to France, using IGN's BDFORET or CESBIO's OSO map.

In this tutorial, we will use a vector shapefile whose polygons will be rasterized as a binary raster, the complete guide can be found [here](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/04_compute_forest_mask/).

##### Running this step using a script

To run this step, simply add the following lines to the script :
```python
from fordead.steps.step4_compute_forest_mask import compute_forest_mask
compute_forest_mask(data_directory, forest_mask_source = "vector", vector_path = "<MyWorkingDirectory>/vector/area_interest.shp")
```

##### Outputs

The outputs of this fourth step, in the data_directory folder, are :
- In the folder ForestMask, the binary raster Forest_Mask.tif which has the value 1 on the pixels of interest and 0 elsewhere.

##### Running this step from the command invite

This step can also be used from the command invite with the command :
```bash
fordead forest_mask -o <output directory> -f vector --vector_path <MyWorkingDirectory>/vector/area_interest.shp
```

> **_NOTE :_** Though this step is presented as the fourth, it can actually be used at any point, even on its own in which case the parameter **path_example_raster** is needed to give a raster from which to copy the extent, resolution, etc...

