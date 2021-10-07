## (OPTIONAL) STEP 5: Computing a confidence index to classify anomalies by intensity
This step computes an index meant to describe the intensity of the detected disturbance. The index is a weighted mean of the difference between the vegetation index and the predicted vegetation index for all unmasked dates after the first anomaly subsequently confirmed. For each date used, the weight corresponds to the number of unmasked dates from the first anomaly.
In case of a disturbance, the intensity of anomalies often goes up which is why later dates have more weight.
Then, pixels are classified into classes, based on the discretization of the confidence index using a list of thresholds. Pixels with only three anomalies are classified as the lowest class, because 3 anomalies are not considered enough to calculate a meaningful index. The results are vectorized and saved in data_directory/Confidence_Index directory.
This step is optional and can be skipped if irrelevant or unnecessary.

#### INPUTS
The input parameters are :
- **data_directory**: The path of the output folder where the results will be written.
- **threshold_list**: List of thresholds used as bins to discretize the confidence index into several classes
- **classes_list**: List of classes names, if threshold_list has n values, classes_list must have n+1 values
- **chunks** : Chunk size for dask computation, parallelizing and saving RAM. Must be used for large datasets such as an entire Sentinel tile.

#### OUTPUTS
The outputs of this step, in the data_directory/Confidence_Index folder, are two rasters and a vector file :
- **confidence_index.tif** : The confidence index 
- **nb_dates.tif**: the number of unmasked dates since the first confirmed anomaly for each pixel
- **confidence_class.shp**: A shapefile resulting from discretization of the confidence index, on all pixels with anomalies confirmed with 3 successive dates excluding areas outside forest mask, where no model could be computed, or detected as bare ground if such a detection occured (see [01_compute_masked_vegetationindex](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/01_compute_masked_vegetationindex/).

## How to use
### From a script

```bash
from fordead.steps.step5_compute_confidence_index import compute_confidence_index
compute_confidence_index(data_directory = <data_directory>, 
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

### Importing information on previous processes and deleting obsolete results if they exist
The informations about the previous processes are imported (parameters, data paths, used dates...). If the parameters used have been modified, all the results from this step onwards are deleted. Thus, unless new Sentinel-2 dates have been added since a previous usage, the confidence index is imported from the previous results.
> **_Functions used:_** [TileInfo()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#tileinfo), TileInfo class methods [import_info()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#import_info), [add_parameters()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#add_parameters), [delete_dirs()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#delete_dirs), [delete_attributes()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#delete_attributes)

### Importing the results of the previous steps
The coefficients of the vegetation index prediction model are imported as well as the information related to the detection of disturbances (pixel status, date of first anomaly...), the information related to the detection of bare soil if it has been done, and the confidence index if it has already been computed and there are no new Sentinel-2 dates.
> **_Functions used:_** [import_coeff_model()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#import_coeff_model), [import_dieback_data()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#import_dieback_data), [soil_data()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#soil_data), [initialize_confidence_data()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#initialize_confidence_data), [import_confidence_data()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#import_confidence_data)

### For each date from the first date used for disturbance detection:

#### Import of the calculated vegetation index and the mask
> **_Functions used:_** [import_masked_vi()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#import_masked_vi)

#### (OPTIONAL - if **correct_vi** is True in [model calculation step](https://fordead.gitlab.io/fordead_package/docs/user_guides/03_train_model/)
- Correction term calculated in previous steps is added to the value of the vegetation index of every pixel
> **_Functions used:_** [correct_vi_date()](https://fordead.gitlab.io/fordead_package/reference/fordead/model_vegetation_index/#correct_vi_date)

#### Prediction of the vegetation index at the given date.
The vegetation index is predicted from the model coefficients.
> **_Functions used:_** [prediction_vegetation_index()](https://fordead.gitlab.io/fordead_package/reference/fordead/dieback_detection/#prediction_vegetation_index)

#### Computing anomalies intensity
The difference between the vegetation index with its prediction is calculated. If the vegetation index to increase in case of a disturbance, the prediction is substracted from the real value, whereas if the vegetation index to decrease, the vegetation index is substracted from its prediction. This way, the value of the difference increases for more intense anomalies.

### Computing the confidence index from the difference between vegetation index and its prediction
The difference between the vegetation and its prediction, if unmasked, is multiplied by an associated weight, then summed. The weight is the number of unmasked Sentinel-2 dates from the first anomaly confirmed.
This sum is then divided by the sum of the weights, the result is the confidence index used. The following graph illustrates the formula used :

![graph_ind_conf](Diagrams/graph_ind_conf.png "graph_ind_conf")


### Discretization and vectorizing results
The confidence index is discretized using **threshold_list**. Pixels with only three dates from the first anomaly, the minimum number of dates for disturbance detection, are affected to the first group. 
Then, those results are vectorized and affected with the classes from **classes_list**.
Pixels are ignored if outside forest mask, or where no model could be computed, or detected as bare ground if such a detection occured.
> **_Functions used:_** [vectorizing_confidence_class()](https://fordead.gitlab.io/fordead_package/reference/fordead/writing_data/#vectorizing_confidence_class),

#### Writing the results
The number of dates since the first anomaly and the continuous confidence index are written as rasters.
The discretized vector shapefile is also written.
> **_Functions used:_** [write_tif()](https://fordead.gitlab.io/fordead_package/reference/fordead/writing_data/#write_tif)
