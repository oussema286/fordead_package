
Allows the testing of many parameter combinations, running three detection steps mask_vi_from_dataframe, train_model_from_dataframe and dieback_detection_from_dataframe using default parameters as well as user defined parameter combinations.

A 'test_info.csv' is written in 'testing_directory', where each test_id is associated with the value of all parameters used in the iteration.

![sensitivity_analysis](Figures/sensitivity_analysis.png "sensitivity_analysis")

----------
## INPUT PARAMETERS
----------

- testing_directory : *str* : Directory where the results will be exported.
- reflectance_path : *str* : Path of the csv file with extracted reflectance.
- args_to_test : *dict or str* : Either a dict where each key is any argument to functions mask_vi_from_dataframe, train_model_from_dataframe or dieback_detection_from_dataframe, and the values are list of values to test. All combinations will be tested.If a str is given, it is interpreted as the path to a text file where each line begins parameter name, then each value is separated with a space. See an example [here](https://gitlab.com/fordead/fordead_package/-/blob/master/docs/examples/ex_dict_vi.txt)
- cloudiness_path : *str*, optional : Path of a csv with the columns 'area_name','Date' and 'cloudiness' used to filter acquisitions, can be calculated by the [extract_cloudiness function](../03_dieback_detection.md). Not used if None.
- update_masked_vi : *bool*, optional : If True, updates the csv containing the vegetation for each acquisition with the columns 'period_id', 'state', 'predicted_vi', 'diff_vi' and 'anomaly'. Doesn't apply if 'overwrite = True'. The default is False.
- name_column : *str*, optional : The default is "id".

----------
## OUPUT
----------

Three csv files are written in *testing_directory* :
- *test_info.csv*, which contains the *fordead* parameter used in each test, with the following columns : 
	- *test_id* : A unique ID for the iteration
	- *lim_perc_cloud*, ..., *threshold_anomaly* : The value of each *fordead* parameter in a different column
- *merged_pixel_info.csv*, which contains information at the pixel level, with the following columns :
	- **epsg** : The CRS of the Sentinel-2 tile from which data was extracted
	- **area_name** : The name of the Sentinel-2 tile from which data was extracted
	- an ID column corresponding to the **name_column** parameter
	- **id_pixel** : The ID of the pixel
	- **last_training_date** : The last date used for training
	- **coeff1**, **coeff2**, ...,  **coeff5** : Value of the corresponding coefficient of the harmonic model
- *merged_periods.csv* : which contains the merged detected periods information for all iterations, with the following columns:
	- **area_name** : The name of the Sentinel-2 tile from which data was extracted
	- an ID column corresponding to the **name_column** parameter
	- **id_pixel** : The ID of the pixel
	- **period_id** : 
	- **state** : The period state, which can be :
		- **Training** : Period used in training the harmonic model
		- **Healthy** : Period detected as healthy, with no stress, dieback or bare ground detected
		- **Stress** : Period beginning with 3 successive anomalies, ending with the last anomaly before three successive non-anomalies of the beginning of a 'Healthy' period.
		- **Dieback** : Period beginning with 3 successive anomalies, ending with the last available acquisition, or the beggining of a Bare ground period.
		- **Invalid** : The pixel is invalid, there were not enough valid acquisitions to compute a harmonic model
	- **first_date** : The first date of the period
	- **last_date** : The first date of the period
	- **anomaly_intensity** : Depending on stress_index_mode, either a mean or a weighted mean of the difference between the calculated vegetation indices and their predicted value for the period. The weight is the number of the date within that period (1+2+3+...+ nb_dates). It is only calculated for 'Healthy', 'Stress' and 'Dieback' periods



----------
## Running this step
----------
#### Using a script

```python
from fordead.validation.sensitivity_analysis import sensitivity_analysis

sensitivity_analysis(testing_directory = <export_dir>,
		reflectance_path = <reflectance_csv_path>,
		name_column = 'id',
		update_masked_vi = False, #Computes faster
		args_to_test = args_to_test)
```
#### From the command invite

This step can also be ran from the command prompt. 
```bash
fordead sensitivity_analysis [OPTIONS]
```
See detailed documentation for the command line prompt [here](../../../../cli/#fordead-sensitivity_analysis)