

Detects 'Stress', 'Healthy' and 'Dieback' periods, calculating for each a weighted mean of the difference between the observed vegetation index value and its prediction, which can be used as an indicator of the intensity of anomalies .
Results at the acquisition level can also be saved for further analysis.

----------
## INPUT PARAMETERS
----------
 - masked_vi_path : *str* : Path of the csv containing the vegetation index for each pixel of each observation, for each valid Sentinel-2 acquisition. Must have the following columns : epsg, area_name, id, id_pixel, Date and vi.
 - pixel_info_path : *str* : Path of the the csv containing pixel info.
 - periods_path : *str* : Path of the csv containing pixel periods.
 - name_column : *str* : Name of the ID column. The default is 'id'.
 - update_masked_vi : *bool*, optional : If True, updates the csv at masked_vi_path with the columns 'period_id', 'state', 'predicted_vi', 'diff_vi' and 'anomaly'. The default is False.
 - threshold_anomaly : *float*, optional : Threshold at which the difference between the actual and predicted vegetation index is considered as an anomaly. The default is 0.16.
 - stress_index_mode : *str*, optional : Chosen stress index, if 'mean', the index is the mean of the difference between the vegetation index and the predicted vegetation index for all unmasked dates after the first anomaly subsequently confirmed. If 'weighted_mean', the index is a weighted mean, where for each date used, the weight corresponds to the number of the date (1, 2, 3, etc...) from the first anomaly. If None, no stress period index is computed. The default is None.
 - vi : str, optional : Chosen vegetation index. The default is "CRSWIR".
 - path_dict_vi : *str*, optional : Path to a text file used to add potential vegetation indices. If not filled in, only the indices provided in the package can be used (CRSWIR, NDVI, NDWI). The file [ex_dict_vi.txt](https://gitlab.com/fordead/fordead_package/-/blob/master/docs/examples/ex_dict_vi.txt) gives an example for how to format this file. One must fill the index's name, formula, and "+" or "-" according to whether the index increases or decreases when anomalies occur. The default is None.

----------
## OUPUT
----------
The csv file containing periods is updated, so for each pixel, the whole time series is covered with the first and last unmasked Sentinel-2 acquisition date of each period, and its associated state.
The 'state' column can now hold the following values :
- **Training** : Period used in training the harmonic model
- **Healthy** : Period detected as healthy, with no stress, dieback or bare ground detected
- **Stress** : Period beginning with 3 successive anomalies, ending with the last anomaly before three successive non-anomalies of the beginning of a 'Healthy' period.
- **Dieback** : Period beginning with 3 successive anomalies, ending with the last available acquisition, or the beggining of a Bare ground period.
- **Invalid** : The pixel is invalid, there were not enough valid acquisitions to compute a harmonic model
A new column 'anomaly_intensity' is also added. Depending on *stress_index_mode*, it is either a mean, or a weighted mean of the difference between the calculated vegetation indices and their predicted value for the period. The weight is the number of the date within that period (1+2+3+...+ nb_dates). It is only calculated for 'Healthy', 'Stress' and 'Dieback' periods

if `update_masked_vi = True`, this function also updates the csv at 'masked_vi_path' with the following columns:
- **period_id** : id of the period the acquisition is associated with
- **state** : Status of of the associated period, can be 'Training', 'Healthy', 'Stress', 'Dieback' or 'Invalid'.
- **predicted_vi** : The prediction of the vegetation index using the harmonic model
- **diff_vi** : Difference between the vegetation and its prediction, in the expected direction of anomalies for the vegetation index
- **anomaly** : True if 'diff_vi' exceeds 'threshold_anomaly', else False

----------
## Running this step
----------

#### Using a script


```python
from fordead.validation.dieback_detection_from_dataframe import dieback_detection_from_dataframe

dieback_detection_from_dataframe(
				masked_vi_path = <masked_vi_path>,
                pixel_info_path = <pixel_info_path>,
                periods_path = <pixel_info_path>,
                name_column = "id",
                update_masked_vi = True)
```
