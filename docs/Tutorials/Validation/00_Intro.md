# <div align="center"> Validation of the detections from observations </div>

In this tutorial, we will show how observations can be used to extract Sentinel-2 data, so the method provided in this package can be applied on a specific dataset, allowing a user to run tests very quickly which can be used to optimize the parameters and to validate the method using this observation dataset.

## Requirements
### Package installation 
If the package is not already installed, follow the instructions of the [installation guide](https://fordead.gitlab.io/fordead_package/docs/Installation/). 
If it is already installed, simply launch the command prompt and activate the environment with the command `conda activate <environment name>`

### Downloading the tutorial dataset

To apply the steps shown in this tutorial, one simply needs a vector file containing points or polygons with an ID column as well as a folder containing a subfolder for each available Sentinel-2 tile.
Sentinel-2 acquisition dates and bands are then parsed from the folder names and the filenames inside as to extract the whole time series on the points or polygons of the vector file.

Here, we provide a small tutorial dataset which you can download from the [fordead_data repository](https://gitlab.com/fordead/fordead_data), if you have not already downloaded it for the [dieback detection tutorial](https://fordead.gitlab.io/fordead_package/docs/Tutorials/Dieback_Detection/00_Intro/).
The Sentinel-2 data relevant to this specific tutorial is located in the folder ~/sentinel_data/validation_tutorial, it focuses on another small study area infested with bark beetles, but the validation tools presented here can be run on several Sentinel-2 tiles.

In this example,  we use data provided by [THEIA](https://www.theia-land.fr/), but data from other providers ([ESA-Copernicus](https://scihub.copernicus.eu/), [CNES-PEPS](https://peps.cnes.fr/rocket/#/home)) can also be used.
More specifically, we use level-2A FRE (**F**lat **RE**flectance) data, which means it is atmospherically and topographically corrected, and contains a Scene Classification Map (for more information, please visit the [related page](https://labo.obs-mip.fr/multitemp/sentinel-2/theias-sentinel-2-l2a-product-format/#English) ).

Here is the file tree for the Sentinel-2 directory example for this tutorial :

```
├── fordead_data/sentinel_data/validation_tutorial/sentinel_data
│   ├── T31UGP
│       ├── SENTINEL2A_20151130-105641-486_L2A_T31UGP_D_V1-1
│           ├── MASKS
│           ├── SENTINEL2A_20151130-105641-486_L2A_T31UGP_D_V1-1_FRE_B2.tif
│           ├── SENTINEL2A_20151130-105641-486_L2A_T31UGP_D_V1-1_FRE_B3.tif
│           ├── SENTINEL2A_20151130-105641-486_L2A_T31UGP_D_V1-1_FRE_B4.tif
│           ├── ...
│       ├── SENTINEL2A_20151207-104805-033_L2A_T31UGP_D_V1-1
│       ├── ...
```

And the vector file containing observation data has the following path : fordead_data/vector/observations_tuto.shp. It contaings an ID column called "id".
Here they are shown, against the Sentinel-2 acquisition of 27-02-2019 on tile T31UGP along with their attributes.

Observations on the Sentinel-2 acquisition of 27-02-2019   |  Attribute table of the observations
:-------------------------:|:-------------------------:
![observations](Figures/observations.png "observations")  |  ![observation_dataframe](Figures/observation_dataframe.png "observation_dataframe")


### Memory space required

For this tutorial, you should have 1Go of memory space, to download the package, the tutorial dataset, and save the computed results.

[NEXT PAGE](https://fordead.gitlab.io/fordead_package/docs/Tutorials/Validation/01_preprocessing_observations)

