#### Step 5 : Exporting results as a shapefile

This step aims at exporting results in a vector format with user defined time step and a footprint defined by the mask. 
The minimum time step corresponds to the periods between available SENTINEL-2 acquisitions. 
The results can be exported as multiple files, in which case each file corresponds to the end of a calendar year.
The polygons include the state of the area at the end of the calendar year, as detected in previous steps. 
If results are exported as a single file, polygons contain the period during which the first anomaly was detected. 
Pixels with unconfirmed anomalies, and pixels identified as anomaly and back to normal are ignored.

If the confidence index was computed in [step 3](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/03_dieback_detection/) and the parameters **conf_threshold_list** and **conf_classes_list** are provided, the confidence index is discretized, vectorized and intersected with the results.
Polygons then also contain a confidence class, giving information on the intensity of anomalies since detection. 
By construction, this class contains the "final" state, calculated at the last available SENTINEL-2 acquisition. 

Comprehensive documentation can be found [here](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/05_export_results/).

##### Running this step using a script

Run the following instructions to perform this processing step:

```python
from fordead.steps.step5_export_results import export_results

export_results(data_directory = data_directory, 
               frequency= "M", 
               multiple_files = False, 
			   conf_threshold_list = [0.265],
			   conf_classes_list = ["Low anomaly","Severe anomaly"])
```

##### Running this step from the command prompt

This processing step can also be performed from a terminal:

```bash
fordead export_results -o <output directory> --frequency M -t 0.265 -c "Low anomaly" -c "Severe anomaly"
```

##### Outputs

The outputs of this step are stored in the folder **data_directory/Results**. 
These outputs include the shapefile `periodic_results_dieback`, where polygons contain the time period when the first anomaly was detected, as well as the confidence index class. 

Period of detection | Confidence class
:-------------------------:|:-------------------------:
![gif_results_original](Figures/gif_results_original.gif "gif_results_original") | ![gif_results_confidence](Figures/gif_results_confidence.gif "gif_results_confidence")


