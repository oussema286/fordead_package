# <div align="center"> Detection of forest disturbance using the package _fordead_ </div>

This tutorial will walk you through the use of the package _fordead_, a python package developed to perform pixelwise analysis of Sentinel-2 time series and automatically identify anomalies in forest seasonality. 

## Requirements
### Package installation 
If the package is not already installed, follow the instructions of the [installation guide](https://fordead.gitlab.io/fordead_package/). 
If it is already installed, simply launch the command prompt and activate the environment with the command `conda activate <environment name>`

### Downloading the tutorial dataset

The analysis can be performed at the scale of a Sentinel tile, but for this tutorial we will focus on a small area of study, with coniferous forest stands infested with bark beetles. The related dataset can be downloaded from the following repository : [https://gitlab.com/fordead/fordead_data](https://gitlab.com/fordead/fordead_data). It mainly contains unpacked Sentinel-2 data from the launch of the first satellite to summer 2019. 

## Creation of a script to detect bark beetle related forest disturbance in a given area using the fordead package

- Create a python script by creating a new text file and naming it _detection_scolytes.py_ (or any name as long as the extension is .py)
- Open this script with the editor of your choice

#### Step 1 : Computing the spectral index and a mask for each SENTINEL-2 date

The first step is to calculate the spectral index and the mask for each date. The mask corresponds to the invalid pixels, which can correspond to clouds, snow, shade, pixels out of the satellite swath or bare ground...
You can find the guide for this step [here](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/01_compute_masked_vegetationindex/).

##### Running this step from a script
To run this step, add to the script :
- to import the function :
```bash
from fordead.steps.step1_compute_masked_vegetationindex import compute_masked_vegetationindex
```
- To choose parameters :
```bash
input_directory = "<MyWorkingDirectory>/study_area"
data_directory = "<output directory>"
```
> **_NOTE :_** Use "/" instead of "\" when writing paths

- To run the function :
```bash
compute_masked_vegetationindex(input_directory = input_directory, data_directory = data_directory)
```
To run the python script from the command prompt, first go to the directory of the script with the following command :
```bash
cd <path of directory containing the script>
```
Then run the script :
```bash
python detection_scolytes.py
```

