# <div align="center"> Detection of vegetation anomalies using the package _fordead_ </div>

This tutorial will walk you through the use of the package _fordead_, a python package developed to perform pixelwise analysis of SENTINEL-2 time series and automatically identify anomalies in forest seasonality. 
This tutorial is focused on a small example area corresponding to a coniferous forest stand attacked by bark beetle. 

## Requirements
### Package installation 
If the package is not already installed, follow the instructions of the [installation guide](https://fordead.gitlab.io/fordead_package/docs/Installation/). 
If it is already installed, simply launch the command prompt and activate the environment with the command `conda activate <environment name>`

### Downloading the tutorial dataset

Even though the analysis can be performed at the scale of a SENTINEL-2 tile, we will focus here on a small study area that presents coniferous forest stands infested with bark beetles. The related dataset can be downloaded from the [fordead_data repository](https://gitlab.com/fordead/fordead_data). It mainly contains unpacked SENTINEL-2 data from the launch of the first satellite in 2015 to summer 2019. 
Here we are using level-2A FRE (**F**lat **RE**flectance) data, which means it is atmospherically and topographically corrected, and contains a Scene Classification Map (for more information, please visit the [related page](https://labo.obs-mip.fr/multitemp/sentinel-2/theias-sentinel-2-l2a-product-format/#English) ). The data provider is [THEIA](https://www.theia-land.fr/).
Data from other providers ([ESA-Copernicus](https://scihub.copernicus.eu/), [CNES-PEPS](https://peps.cnes.fr/rocket/#/home)) can also be used with this package.

### Memory space required

For this tutorial, you should have 900Mo of memory space, to download the package, the tutorial dataset, and save the computed results.

[NEXT PAGE](https://fordead.gitlab.io/fordead_package/docs/Tutorial/01_compute_masked_vegetationindex)





