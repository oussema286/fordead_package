## (OPTIONAL) STEP 5: Computing a confidence index to classify anomalies by intensity
This step computes an index meant to describe the intensity of the detected disturbance. The index is a weighted mean of the difference between the vegetation index and the predicted vegetation index for all unmasked dates after the first anomaly subsequently confirmed. For each date used, the weight corresponds to the number of the date (1, 2, 3, etc...) from the first anomaly).
In case of a disturbance, the intensity of anomalies often goes up which is why later dates have more weight.
Then, pixels are classified into classes, based on the discretization of the confidence index using a list of thresholds. Pixels with only three anomalies are classified as the lowest class, because 3 anomalies are not considered enough to calculate a meaningful index. The results are vectorized and saved in data_directory/Confidence_Index directory.
This step is optional and can be skipped if irrelevant or unnecessary.

#### INPUTS
The input parameters are :
- **data_directory**: The path of the output folder where the detection results will be written.
- **threshold_list**: List of thresholds used as bins to discretize the confidence index into several classes
- **classes_list**: List of classes names, if threshold_list has n values, classes_list must have n+1 values
- **chunks** : Chunk size for dask computation, parallelizing and saving RAM. Must be used for large datasets such as an entire Sentinel tile.

#### OUTPUTS
The outputs of this step, in the data_directory/Confidence_Index folder, are two rasters :
- **confidence_index.tif** : The confidence index 
- **nb_dates.tif**: the number of dates since the first confirmed anomaly
- **confidence_class.shp**: A shapefile resulting from discretization of the confidence index, on all pixels with anomalies confirmed with 3 successive dates excluding areas outside forest mask, where no model could be computed, or detected as bare ground if such a detection occured (see [01_compute_masked_vegetationindex](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/01_compute_masked_vegetationindex/).

## How to use
### From a script

```bash
from fordead.steps.compute_confidence_index import classify_declining_area
classify_declining_area(data_directory, 
						threshold_list = <threshold_list>,
						classes_list = <classes_list>,
						chunks = 1280)
```

### From the command line
```bash
fordead ind_conf [OPTIONS]
```
See detailed documentation on the [site](https://fordead.gitlab.io/fordead_package/docs/cli/#fordead-ind_conf)

## How it works

![Diagramme_ind_conf](Diagrams/Diagramme_ind_conf.png "Diagramme_ind_conf")

### Importing information on previous processes and deleting obsolete results if they exist
The informations about the previous processes are imported (parameters, data paths, used dates...). If the parameters used have been modified, all the results from this step onwards are deleted. Thus, unless the parameters have been modified or this is the first time this step is performed, the detection of forest disturbance is updated using only with the new SENTINEL dates.
> **_Functions used:_** [TileInfo()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#tileinfo), TileInfo class methods [import_info()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#import_info), [add_parameters()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#add_parameters), [delete_dirs()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#delete_dirs), [delete_attributes()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#delete_attributes)

### Importing the results of the previous steps
The coefficients of the vegetation index prediction model are imported, as well as the array containing the index of the first date used for the detection. The arrays containing the information related to the detection of forest disturbances (state of the pixels, number of successive anomalies, index of the date of the first anomaly) are initialized if the step is used for the first time, or imported if it is an update of the detection.
> **_Functions used:_** [import_coeff_model()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#import_coeff_model), [import_masked_vi()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#import_masked_vi), [import_decline_data()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#import_decline_data), [soil_data()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#soil_data), [initialize_confidence_data()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#initialize_confidence_data), [import_confidence_data()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#import_confidence_data)

### For each date from the first date used for disturbance detection:

#### Import of the calculated vegetation index and the mask
> **_Functions used:_** [import_masked_vi()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#import_masked_vi)

#### (OPTIONAL - if **correct_vi** is True in [model calculation step](https://fordead.gitlab.io/fordead_package/docs/user_guides/03_train_model/)
- Correction term calculated in previous steps is added to the value of the vegetation index of every pixel
> **_Functions used:_** [correct_vi_date()](https://fordead.gitlab.io/fordead_package/reference/fordead/model_spectral_index/#correct_vi_date)

#### Prediction of the vegetation index at the given date.
The vegetation index is predicted from the model coefficients.
> **_Functions used:_** [prediction_vegetation_index()](https://fordead.gitlab.io/fordead_package/reference/fordead/decline_detection/#prediction_vegetation_index)

#### Computing anomalies intensity
The difference between the vegetation index with its prediction is calculated. If the vegetation index to increase in case of a disturbance, the prediction is substracted from the real value, whereas if the vegetation index to decrease, the vegetation index is substracted from its prediction. This way, the value of the difference increases for more intense anomalies.

### Computing the confidence index from the difference between vegetation index and its prediction
The difference between the vegetation and its prediction, if unmasked, is multiplied by an associated weight, then summed. The weight is the number of unmasked Sentinel-2 dates from the first anomaly confirmed.
This sum is then divided by the sum of the weights, the result is the confidence index used.

### Discretization and vectorizing results
The confidence index is discretized using **threshold_list**. Pixels with only three dates from the first anomaly, the minimum number of dates for disturbance detection, are affected to the first group. 
Then, those results are vectorized and affected with the classes from **classes_list**.
Pixels are ignored if outside forest mask, or where no model could be computed, or detected as bare ground if such a detection occured.
> **_Functions used:_** [vectorizing_confidence_class()](https://fordead.gitlab.io/fordead_package/reference/fordead/writing_data/#vectorizing_confidence_class),

#### Writing the results
The number of dates since the first anomaly and the continuous confidence index are written as rasters.
The discretized vector shapefile is also written.
> **_Functions used:_** [write_tif()](https://fordead.gitlab.io/fordead_package/reference/fordead/writing_data/#write_tif),
