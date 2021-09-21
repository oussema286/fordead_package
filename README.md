# fordead : a python package for vegetation anomalies detection from SENTINEL-2 images

Read in french [here](https://gitlab.com/fordead/fordead_package/-/blob/master/README_fr.md).

The `fordead` package has been developed for the detection of vegetation anomalies from SENTINEL-2 time series. It has been developped to provide monitoring tools to adress the bark beetle health crisis on spruce trees in France, but the many tools simplifying the use of SENTINEL-2 satellite data and anomaly detection can certainly be used in other contexts. The method used takes advantage of the complete SENTINEL-2 time series from the launch of the first satellite and detects anomalies at the pixel level which can be updated whenever new Sentinel-2 dates are added for constant monitoring of the vegetation.

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

All the documentation and user guides for these steps are available at the [documentation website](https://fordead.gitlab.io/fordead_package/).

Here is an example of the result of these steps on a small area :
Period of detection | Confidence class
:-------------------------:|:-------------------------:
![gif_results_original](docs/Tutorial/Figures/gif_results_original.gif "gif_results_original") | ![gif_results_confidence](docs/Tutorial/Figures/gif_results_confidence.gif "gif_results_confidence")

## Visualisation tools

The package also contains built-in visualisation tools, the first one plots the time series of the vegetation index for a particular pixel, along with the associated model, the anomaly detection threshold and the associated detection.

Healthy pixel | Attacked pixel
:-------------------------:|:-------------------------:
![graph_healthy](docs/Tutorial/Figures/graph_healthy.png "graph_healthy") | ![graph_dieback](docs/Tutorial/Figures/graph_dieback.png "graph_dieback")

The second one makes a "timelapse" on a small area to visualize the results at each Sentinel-2 date used, with the Sentinel-2 data in RGB in the background and a slider to navigate between the different dates.

![gif_timelapse](docs/Tutorial/Figures/gif_timelapse.gif "gif_timelapse")

## Installation

The installation guide can be found [here](https://fordead.gitlab.io/fordead_package/docs/Installation/).

## Tutorial

A tutorial to get started and test the package on a small dataset can be found [here](https://fordead.gitlab.io/fordead_package/docs/Tutorial/00_Intro/).

