# <div align="center"> Detection of forest disturbance using the package _fordead_ </div>

This tutorial will walk you through the use of the package _fordead_, a python package developed to perform pixelwise analysis of Sentinel-2 time series and automatically identify anomalies in forest seasonality. 

## Requirements
### Package installation 
If the package is not already installed, follow the instructions of the [installation guide](https://fordead.gitlab.io/fordead_package/). 
If it is already installed, simply launch your command prompt and activate the environment with the command `conda activate fordead_env`

### Downloading the tutorial dataset

The analysis can be performed at the scale of a Sentinel tile, but for this tutorial we will focus on a small area of study, with coniferous forest stands infested with bark beetles. The related dataset can be downloaded from the following repository : [https://gitlab.com/fordead/fordead_data](https://gitlab.com/fordead/fordead_data). It mainly contains unpacked Sentinel-2 data from the launch of the first satellite to summer 2019. 

## Creation of a script to detect bark beetle related forest disturbance in a given area using the fordead package

- Create a python script by creating a new text file and naming it _detection_scolytes.py_ (or any name as long as the extension is .py)
- Open this script with the editor of your choice

#### Step 1 : Computing the spectral index and a mask for each SENTINEL-2 date
