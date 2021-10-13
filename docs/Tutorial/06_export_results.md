#### Step 6 : Exporting results to shapefile for visualizing results with a time step defined by the user

This step aims at exporting results in a vector format with user defined time step and footpprint defined by the mask. 
The minimum time step corresponds to the periods between available SENTINEL-2 dates. 
The results can be exported as multiple files, in which case each file corresponds to the end of a period, and the resulting polygons contain the state of the area at the end of this period, as detected in previous steps. If results are exported as a single file, polygons contain the period during which the first anomaly was detected. 
Pixels with unconfirmed anomalies, and pixels identified as anomaly and back to normal are ignored.

If the confidence index was computed and the related option is chosen, the polygons also contain the anomaly intensity class as calculated in the [previous step](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/05_compute_confidence/). This class therefore contains the "final" state, calculated at the last available SENTINEL-2 date. 

Comprehensive documentation can be found [here](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/06_export_results/).

##### Running this step using a script

Run the following instructions to perform this processing step:

```python
from fordead.steps.step6_export_results import export_results

export_results(data_directory = data_directory, 
               frequency= "M", 
               multiple_files = False, 
               intersection_confidence_class = True)
```

##### Running this step from the command prompt

This processing step can also be performed from a terminal:

```bash
fordead export_results -o <output directory> --frequency M --intersection_confidence_class
```

##### Outputs

The output of this step, in the folder data_directory/Results, is the shapefile periodic_results_dieback, whose polygons contain the time period when the first anomaly was detected, as well as the confidence index class. 

Period of detection | Confidence class
:-------------------------:|:-------------------------:
![gif_results_original](Figures/gif_results_original.gif "gif_results_original") | ![gif_results_confidence](Figures/gif_results_confidence.gif "gif_results_confidence")


[NEXT PAGE](https://fordead.gitlab.io/fordead_package/docs/Tutorial/07_create_timelapse)
