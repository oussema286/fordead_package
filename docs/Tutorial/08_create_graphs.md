## Using built-in visualisation tools to explore detection results

The second built-in visualisation tool allows to visualize for a particular pixel the time series of the vegetation index with the associated model, the anomaly detection threshold and the associated detections.

### Creating graphs showing the time series evolution at pixel level

This tool will create plots showing the vegetation index value for each Sentinel-2 date, as well as the vegetation index prediction model, the threshold used for anomaly detection, the period used for training... This allows to better understand how anomaly detection went for pixels of interest.

![graph_example](user_guides/english/Diagrams/graph_example.png "graph_example")

It can be ran on a shapefile containing points if parameters **shape_path** and **name_column** are used. If those parameters are not used, the program will prompt the user to enter coordinates in the Sentinel-2 data CRS.  
In this example, we will use a shapefile provided in the fordead_data repository.

##### Running this step using a script

To run this step, simply add the following lines to the script :
```python
from fordead.visualisation.vi_series_visualisation import vi_series_visualisation
vi_series_visualisation(data_directory = data_directory, shape_path = "<MyWorkingDirectory>/vector/points_for_graphs.shp", name_column = "id", ymin = 0, ymax = 2, chunks = 100)
```
##### Running this step from the command invite

This step can also be used from the command invite with the command :
```bash
fordead graph_series  -o <output directory> --shape_path <MyWorkingDirectory>/vector/points_for_graphs.shp --name_column id --ymin 0 --ymax 2 --chunks 100
```

##### Outputs

The plots are saved in the folder data_directory/TimeSeries, with a .png file for each point with the value in the column **name_column** as file name. The y axis limits are set using **ymin** and **ymax** parameters.

Healthy pixel | Attacked pixel
:-------------------------:|:-------------------------:
![graph_healthy](Figures/graph_healthy.png "graph_healthy") | ![graph_dieback](Figures/graph_dieback.png "graph_dieback")

> **_NOTE :_** The **chunks** parameter is not really necessary in this case, since we're working on a small area, but it is needed to reduce computation time in large datasets.

[NEXT PAGE](https://fordead.gitlab.io/fordead_package/docs/Tutorial/09_updating_detection)