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

The first step is to calculate the vegetation index and a mask for each date. The mask corresponds to pixels that should not be used throughout the rest of the detection steps.
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
Note that if the same parameters are used, the Sentinel-2 dates already computed are ignored. However, if you change any parameter, all previous results are deleted and calculated again. If new Sentinel-2 data are added in the **input_directory**, it is computed as long as it is more recent than the last computed Sentinel-2 date.








