#### Step 3 : Detecting anomalies by comparing vegetation index to predicted value

The value of the vegetation index is compared to the vegetation index predicted from the periodic model calculated in the previous step, for each SENTINEL-2 acquisition available for the detection step.
An anomaly is identified when the difference exceeds a threshold (in the expected direction in case of anomaly). 
For example, the CRSWIR is sensitive to canopy water content and tends to increase with decreasing water content. 

Bark beetle outbreaks induce a decrease in canopy water content, therefore only CRSWIR values higher than expected values can be identified as anomalies. 
A pixel is detected as suffering from dieback when three successive anomalies are detected. 
This prevents false positive corresponding to one time events of anomalies due to an imperfect mask, or temporary climatic events. 

As an example, the following figure shows the time series of the vegetation index along with the threshold for anomaly detection, and the date of detection :

![anomaly_detection](Figures/anomaly_detection_X642135_Y5452255.png "anomaly_detection")

Once anomalies confirmed (after three successive anomalies), pixel can return to normal state if no anomaly is detected for three successive acquisitions. 
This reduces the risk of false positive corresponding to long drought periods resulting in more than three successive anomalies.
Also, information about those periods between false detection and return to normal, which we will call stress periods, can be stored.

A stress index can be computed for those stress periods, and for the final detection. It can be either the mean of the difference between the vegetation index and its prediction, or a weighted mean where the weight corresponds to the number of the date since the first anomaly of the period as illustrated in the following figure :

![graph_ind_conf](Diagrams/graph_ind_conf.png "graph_ind_conf")

This stress index is meant to describe the intensity of detected anomalies in the period, and can be used as a confidence index for the final detection.

Comprehensive documentation can be found [here](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/03_dieback_detection/).

##### Running this step using a script

Run the following instructions to perform this processing step:
```python
from fordead.steps.step3_dieback_detection import dieback_detection

dieback_detection(data_directory = data_directory, 
                  threshold_anomaly = 0.16,
				  stress_index_mode = "weighted_mean")
```

##### Running this step from the command prompt

This processing step can also be performed from a terminal:
```bash
fordead dieback_detection -o <output directory> --threshold_anomaly 0.16 --stress_index_mode weighted_mean
```
> **_NOTE :_** As always, if the model is already computed and no parameters were changed, the process is ignored. If parameters were changed, previous results from this step and subsequent steps are deleted and the model is computed anew.

##### Outputs

The outputs of this step, in the data_directory folder, are :
- In the **DataDieback** folder, three rasters:
    - **count_dieback** is the number of successive dates with anomalies
	- **first_date_unconfirmed_dieback** : The date index of latest potential state change of the pixels, first anomaly if pixel is not detected as dieback, first non-anomaly if pixel is detected as dieback, not necessarily confirmed.
    - **first_date_dieback**: The index of the first date with an anomaly in the last series of anomalies
    - **state_dieback** is a binary raster with pixel as suffering from dieback (at least three successive anomalies) identified as 1.
- In the **DataStress** folder, four rasters:
    - **dates_stress** : A raster with **max_nb_stress_periods***2+1 bands, containing the date indices of the first anomaly, and of return to normal for each stress period.
    - **nb_periods_stress**: A raster containing the total number of stress periods for each pixel 
    - **cum_diff_stress**: a raster with **max_nb_stress_periods**+1 bands containing containing for each stress period the sum of the difference between the vegetation index and its prediction, multiplied by the weight if stress_index_mode is "weighted_mean"
	- **nb_dates_stress** : a raster with **max_nb_stress_periods**+1 bands containing the number of unmasked dates of each stress period.
	- **stress_index** : a raster with **max_nb_stress_periods**+1 bands containing the stress index of each stress period, it is the mean or weighted mean of the difference between the vegetation index and its prediction depending on **stress_index_mode**, obtained from cum_diff_stress and nb_dates_stress
	The number of bands of these rasters is meant to account for each potential stress period, and another for a potential final dieback detection
- In the **DataAnomalies** folder, a raster for each date **Anomalies_YYYY-MM-DD.tif** whose value is 1 where anomalies are detected.



[PREVIOUS PAGE](https://fordead.gitlab.io/fordead_package/docs/Tutorial/02_train_model) [NEXT PAGE](https://fordead.gitlab.io/fordead_package/docs/Tutorial/04_compute_forest_mask)
