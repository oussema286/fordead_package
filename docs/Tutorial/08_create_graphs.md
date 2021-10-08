## Using built-in visualisation tools to explore detection results

The second built-in visualisation tool allows to visualize for a particular pixel the time series of the vegetation index with the associated model, the anomaly detection threshold and the associated detections.

### Creating graphs showing the time series evolution at pixel level

This tool creates figures showing: 
- the vegetation index value for each SENTINEL-2 acquisition
- the corresponding seasonal model
- the threshold used for anomaly detection
- the period used for training.

This allows better understanding of the dynamic related to anomaly detection for pixels of interest.
The following illustration displays time series for a healthy pixel, and for a pixel corresponding to bark beetle outbreak :


Healthy pixel | Attacked pixel
:-------------------------:|:-------------------------:
![graph_healthy](Figures/graph_healthy.png "graph_healthy") | ![graph_dieback](Figures/graph_dieback.png "graph_dieback")

This process can be performed using a shapefile containing points if parameters **shape_path** and **name_column** are used, or with parameters **x** and **y** to plot a single pixel chosen from coordinates in the SENTINEL-2 data CRS.
If none of those parameters are used, the program will prompt the user in a loop to enter coordinates.

In this example, we used a shapefile provided in the fordead_data repository. 

Comprehensive documentation can be found [here](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/Results_visualisation/#create-graphs-showing-the-evolution-of-the-time-series).

##### Running this step using a script

Run the following instructions to perform this processing step :

```python
from fordead.visualisation.vi_series_visualisation import vi_series_visualisation

vi_series_visualisation(data_directory = data_directory, 
                        shape_path = "<MyWorkingDirectory>/vector/points_for_graphs.shp", 
                        name_column = "id", 
                        ymin = 0, 
                        ymax = 2, 
                        chunks = 100)
```
##### Running this step from the command invite

This processing step can also be performed from a terminal :
```bash
fordead graph_series  -o <output directory> --shape_path <MyWorkingDirectory>/vector/points_for_graphs.shp --name_column id --ymin 0 --ymax 2 --chunks 100
```

##### Outputs

The plots are saved as .png files in **data_directory/TimeSeries**, one file for each point with the value in the column **name_column** as file name. 
The y axis limits are set using **ymin** and **ymax** parameters.

> **_NOTE :_** The **chunks** parameter is not really necessary in this case, since we're working on a small area, but it is needed to reduce computation time in large datasets.

[NEXT PAGE](https://fordead.gitlab.io/fordead_package/docs/Tutorial/09_updating_detection)
