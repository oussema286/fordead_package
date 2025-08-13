---
title: Introduction
---
# <div align="center"> Detection of FORest DEgradation And Dieback with the package _fordead_ </div>

This tutorial introduces the main functionalities of the package _fordead_  (FORest Degradation And Dieback). 
_fordead_ is a python package initially developed to detect anomalies in seasonality induced by bark beetle outbreaks on spruce forests from Sentinel-2 time series.

## Requirements
### Package installation 
If the package is not already installed, follow the [installation instruction guide](../../Installation.md). 
If already installed, launch the command prompt and activate the environment with the command `conda activate <environment name>`

### Download the tutorial dataset
This tutorial uses a subset extracted from a Sentinel-2 time series, corresponding to a coniferous forest stand attacked by bark beetle in North East region of France. 
The subset can be downloaded manually from the [fordead_data repository](https://gitlab.com/fordead/fordead_data), or automatically with the command line :

```python
wget https://gitlab.com/fordead/fordead_data/-/archive/main/fordead_data-main.zip
```

This dataset includes all Sentinel-2 images acquired since the launch of Sentinel-2A in 2015 until September 2019. 
The dataset was downloaded from the [Theia](https://www.theia-land.fr/) data catalogue. 
Level-2A FRE (Flat REflectance) products will be used for this tutorial (for more information, please visit [this webpage](https://labo.obs-mip.fr/multitemp/sentinel-2/theias-sentinel-2-l2a-product-format/#English)).
_fordead_ can also process data obtained from other providers ([ESA-Copernicus](https://scihub.copernicus.eu/), [CNES-PEPS](https://peps.cnes.fr/rocket/#/home)).

### Disk space requirements

Once _fordead_ is installed, a minimum of 1 Go of free disk space is recommended.






