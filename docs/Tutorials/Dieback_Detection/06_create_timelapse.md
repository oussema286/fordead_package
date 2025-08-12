## Using built-in visualisation tools to explore detection results

A timelapse can be generated to visualize the temporal evolution of anomaly detection for each SENTINEL-2 acquisition. 
A slider allows navigation between the different acquisitions. 

### Creating a timelapse

This tool produces a timelapse as illustrated by the following animated gif :

![gif_timelapse](Figures/gif_timelapse-optimized.gif "gif_timelapse")

It can be made using coordinates in the projection system of the SENTINEL-2 data using **x** and **y** parameters, or using a shapefile containing one or several polygons or points using the **shape_path** and **name_column** parameters. 
In this example, we will use coordinates.

##### Running this step using a script

Run the following instructions to perform this processing step:

```python
from fordead.visualisation.create_timelapse import create_timelapse

create_timelapse(data_directory = data_directory, 
                 x = 643069, 
                 y = 5452565, 
                 buffer = 1500)
```
##### Running this step from the command prompt

This processing step can also be performed from a terminal:

```bash
fordead timelapse -o <output directory> -x 643069 -y 5452565 --buffer 1500
```

##### Outputs

The resulting timelapse is saved in the **data_directory/Timelapses** directory with the name format x_y.html. 
Using the **zip_results** parameter, it is possible to automatically compress results in zip format. 

The timelapse area includes the coordinates as the center, and pixels within 1500 m, the length used as buffer. 
The slider allows browsing between SENTINEL-2 acquisitions.
The background image corresponds to the RGB bands of the SENTINEL-2 acquisition.
Bark beetle attacks are displayed as white polygons at the date of the first anomaly, if confirmed with three successive anomalies, and if there is no return to a normal behaviour with three successive acquisitions without anomalies afterwards. 
False detections related to temporary water stress which are subsequently corrected are not displayed.
Also, in the last acquisitions, anomalies may not appear yet due to the lack of future data to confirm the detection.

A legend is included, and clicking on a legend item toggles its visibility, double clicking makes it the sole visible item on the graph.

It is possible to zoom in on the desired area by holding down the click while delimiting an area. It is then possible to zoom out by double clicking on the image. Passing the mouse over a pixel also allows you to obtain its information:

- x : coordinates in x
- y : coordinates in y
- z : `[<reflectance B04>,<reflectance B03>,<reflectance B02>]` corresponding to SENTINEL-2 RGB data.

> **_NOTE :_** It is also possible to have detected pixels appear as their confidence class using **show_confidence_class** parameter, or have points, lines or polygons from a custom shapefile appear on the timelapse using **vector_display_path** and **hover_column_list** parameters. The resulting html files can also be automatically zipped using the **zip_results** parameter.

[PREVIOUS PAGE](https://fordead.gitlab.io/fordead_package/docs/Tutorial/05_export_results) [NEXT PAGE](https://fordead.gitlab.io/fordead_package/docs/Tutorial/07_create_graphs)
