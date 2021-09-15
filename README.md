# fordead : a python package for forest change detection from SENTINEL-2 images

Read this in french [here](https://gitlab.com/fordead/fordead_package/-/blob/master/README_fr.md).

The `fordead` package has been developed for the detection of changes in forests from SENTINEL-2 time series, in particular in the context of a bark beetle health crisis on spruce trees. Based on functions simplifying the use of SENTINEL-2 satellite data, it allows the mapping of bark beetle forest disturbances since 2018. However, except for the masks used which are certainly too specific to the study of coniferous forests, the rest of the process can probably be used for other issues. 

## Installation

The installation guide can be found [here](https://fordead.gitlab.io/fordead_package/docs/Installation/).

## Tutorial

A tutorial to get started and test the package on a small dataset can be found [here](https://fordead.gitlab.io/fordead_package/docs/Tutorial/00_Intro/).

## Dieback detection

![diagramme_general_english](docs/user_guides/english/Diagrams/Diagramme_general.png "diagramme_general_english")

The detection of Forest disturbance is done in five steps.
- [The calculation of vegetation indices and masks for each SENTINEL-2 date](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/01_compute_masked_vegetationindex/)
- [The training by modeling the vegetation index pixel by pixel from the first dates](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/02_train_model/)
- [Detecting anomalies by comparing the vegetation index predicted by the model with the actual vegetation index](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/03_decline_detection/)
- [Creating a forest mask, which defines the areas of interest](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/04_compute_forest_mask/)
- (Optional) [Computing a confidence index to classify anomalies by intensity](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/05_compute_confidence/)
- [The export of results as shapefiles allowing to visualize the results with the desired time step](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/06_export_results/)

It is possible to correct the vegetation index using a correction factor calculated from the median of the vegetation index of the large-scale stands of interest, in which case the mask creation step must be performed before the model training step.

All the documentation and user guides for these steps are available at [site](https://fordead.gitlab.io/fordead_package/).

