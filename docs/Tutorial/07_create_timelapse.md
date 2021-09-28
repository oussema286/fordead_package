## Using built-in visualisation tools to explore detection results

The first visualisation tool allows to make a timelapse to visualize the results at each Sentinel-2 date used, with the Sentinel-2 data in RGB in the background and a slider to navigate between the different dates. 

### Creating a timelapse

This tool will create a timelapse such as shown in the following animated gif :

![gif_timelapse](Figures/gif_timelapse.gif "gif_timelapse")

It can be made using coordinates in the projection system of the Sentinel-2 data using **x** and **y** parameters, or using a shapefile containing one or several polygons or points using the **shape_path** and **name_column** parameters. In this example, we will use coordinates.

##### Running this step using a script

To run this step, simply add the following lines to the script :
```python
from fordead.visualisation.create_timelapse import create_timelapse
create_timelapse(data_directory = data_directory, x = 643069, y = 5452565, buffer = 1500)
```
##### Running this step from the command invite

This step can also be used from the command invite with the command :
```bash
fordead timelapse -o <output directory> -x 643069 -y 5452565 --buffer 1500
```

##### Outputs

The resulting timelapse is saved in the data_directory/Timelapses directory with the name format x_y.html. Using the **zip_results** parameter, it is possible to automatically zip results to compress them. 

The timelapse area includes the coordinates as the center, and pixels within 1500m, the length used as buffer. 
The slider allows you to move temporally from SENTINEL date to SENTINEL date.
The image corresponds to the RGB bands of the SENTINEL data.
Bark beetle attacks appear as white polygons at the date of the first anomaly, if confirmed with 3 successive anomalies, and if there is no return to normal with 3 successive dates without anomalies afterwards. So false detections related to temporary water stress which are subsequently corrected do not appear. Also, in the last dates, there may be anomalies not appearing yet due to the lack of future data to confirm the detection.

A legend is included, and clicking on a legend item toggles its visibility, double clicking makes it the sole visible item on the graph.

It is possible to zoom in on the desired area by holding down the click while delimiting an area. It is then possible to zoom out by double clicking on the image. Passing the mouse over a pixel also allows you to obtain its information:

- x : coordinates in x
- y : coordinates in y
- z : `[<reflectance in red>,<reflectance in green>,<reflectance in blue>]`, that is to say the value of the corresponding SENTINEL band at the given date.

> **_NOTE :_** It is also possible to have detected pixels appear as their confidence class using **show_confidence_class** parameter, or have points, lines or polygons from a custom shapefile appear on the timelapse using **vector_display_path** and **hover_column_list** parameters. The resulting html files can also be automatically zipped using the **zip_results** parameter.

[NEXT PAGE](https://fordead.gitlab.io/fordead_package/docs/Tutorial/08_create_graphs)