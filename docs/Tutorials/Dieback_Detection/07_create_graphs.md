## Using built-in visualisation tools to explore detection results

The second built-in visualisation tool allows to visualize the time series of the vegetation index with the associated model, the anomaly detection threshold and the associated detections, for a given pixel.

### Creating graphs of time series evolution at pixel level

This tool creates figures including : 
- the vegetation index value for each SENTINEL-2 acquisition
- the corresponding harmonic model
- the threshold used for anomaly detection
- the period used for training.

This allows illustration of the dynamic related to anomaly detection for pixels of interest.
The following illustration displays time series for a healthy pixel, and for a pixel experiencing bark beetle outbreak :

Healthy pixel | Attacked pixel
:-------------------------:|:-------------------------:
![graph_healthy](Figures/graph_healthy.png "graph_healthy") | ![graph_dieback](Figures/graph_dieback.png "graph_dieback")

This process can be performed using a shapefile containing points if parameters **shape_path** and **name_column** are used, or with parameters **x** and **y** to plot a single pixel chosen from coordinates in the SENTINEL-2 data CRS.
If none of those parameters are used, the program will prompt the user in a loop to enter coordinates.

In this example, we used a shapefile provided in the fordead_data repository. 

Comprehensive documentation can be found [here](../../user_guides/english/Results_visualisation.md#create-graphs-showing-the-evolution-of-the-time-series).

##### Running this step using a script

Run the following instructions to perform this processing step:

```python
from fordead.visualisation.vi_series_visualisation import vi_series_visualisation

vi_series_visualisation(data_directory = data_directory, 
                        shape_path = "<MyWorkingDirectory>/vector/points_for_graphs.shp", 
                        name_column = "id", 
                        ymin = 0, 
                        ymax = 2, 
                        chunks = 1280)
```
##### Running this step from the command prompt

This processing step can also be performed from a terminal:
```bash
fordead graph_series  -o <output directory> --shape_path <MyWorkingDirectory>/vector/points_for_graphs.shp --name_column id --ymin 0 --ymax 2 --chunks 1280
```

##### Outputs

The plots are saved as .png files in **data_directory/TimeSeries**. One file is stored for each point with the value in the column **name_column** as file name. 
The y axis limits are set using **ymin** and **ymax** parameters.

> **_NOTE :_** The **chunks** parameter is not necessary in this case, since the process is applied on limited surfaces. However, it is needed to reduce computation time in large datasets.

