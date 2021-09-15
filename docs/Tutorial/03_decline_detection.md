#### Step 3 : Detecting anomalies by comparing the vegetation index and its predicted value

For each SENTINEL date not used for training, the actual vegetation index is compared to the vegetation index predicted from the model calculated in the previous step. If the difference exceeds a threshold, in the expected direction in case of anomaly, an anomaly is detected. For example, the CRSWIR goes up as stands suffer bark beetle attacks, so only high CRSWIR anomalies are registered. The pixel's state is only considered changed if three successive anomalies are detected, confirming them. This allows to ignore one time events of anomalies due to an imperfect mask, or temporary climatic events. If after anomalies have been confirmed, the pixel has three successive dates without anomalies, it returns to normal state. This allows the algorithm to auto-correct false detections based on new Sentinel-2 data, for example in the case of a drought period lasting long enough to get more than three successive anomalies.

This step's complete guide can be found [here](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/03_decline_detection/).

##### Running this step using a script

To run this step, simply add the following lines to the script :
```python
from fordead.steps.step3_decline_detection import decline_detection
decline_detection(data_directory = data_directory, threshold_anomaly = 0.16)
```

##### Outputs

The outputs of this step, in the data_directory folder, are :
- In the **DataDecline** folder, three rasters:
    - **count_decline** : the number of successive dates with anomalies
    - **first_date_decline**: The index of the first date with an anomaly in the last series of anomalies
    - **state_decline**: A binary raster whose value is 1 if the pixel is detected as declining (at least three successive anomalies)
- In the **DataAnomalies** folder, a raster for each date **Anomalies_YYYY-MM-DD.tif** whose value is 1 where anomalies are detected.

##### Running this step from the command invite

This step can also be used from the command invite with the command :
```bash
fordead decline_detection -o <output directory> --threshold_anomaly 0.17
```
As always, if the model is already computed and no parameters were changed, the process is ignored. If parameters were changed, previous results from this step and subsequent steps are deleted and the model is computed anew.

[NEXT PAGE](https://fordead.gitlab.io/fordead_package/docs/Tutorial/04_compute_forest_mask)