# -*- coding: utf-8 -*-
"""
Created on Thu Oct  1 14:56:23 2020

@author: raphael.dutrieux

"""


import numpy as np
import datetime
import random
import geopandas as gp
import xarray as xr
import click
import matplotlib.pyplot as plt

from fordead.ImportData import TileInfo, import_stackedmaskedVI, import_stacked_anomalies, import_coeff_model, import_forest_mask, import_first_detection_date_index, import_decline_data, import_soil_data
from fordead.ModelVegetationIndex import compute_HarmonicTerms
from fordead.results_visualisation import select_pixel_from_coordinates, select_pixel_from_indices, plot_temporal_series

@click.group()
def graph_series():
    """Main entrypoint."""
    
@graph_series.command(name='graph_series')
@click.option("-o", "--data_directory", type = str, help = "Path of the directory containing results from the region of interest")
@click.option("--shape_path", type = str, help = "Path to shapefile containing points whose data will be plotted. If None, indexes or coordinates for x and y can be given")
@click.option("--name_column", type = str, default = "id", help = "Name of the column containing the name of the point, used to name the exported image. Not used if pixel is selected from indexes or coordinates")
@click.option("--ymin", type = float, default = 0, help = "ymin limit of graph")
@click.option("--ymax", type = float, default = 2, help = "ymax limit of graph")
@click.option("--chunks", type = int, default = None, help = "Chunk length to import data as dask arrays and save RAM, advised if computed area in data_directory is large")
def cli_vi_series_visualisation(data_directory, shape_path = None, name_column = "id", ymin = 0, ymax = 2, chunks = None):
    """
    From previously computed results, graphs the results for specific pixels showing the vegetation index for each dates, the model and the detection.
    By specifying 'shape_path' and 'name_column' parameters, it can be used with a shapefile containing points with a column containing a unique ID used to name the exported image.
    If shape_path is not specified, the user will be prompted to give coordinates in the system of projection of the tile. Graphs can also be plotted for random pixels inside the forest mask.
    The user can also choose to specify pixels by their indices from the top left hand corner of the computed area (If only a small region of interest was computed (for example by using extent_shape_path parameter in the step 01_compute_masked_vegetationindex (https://fordead.gitlab.io/fordead_package/docs/user_guides/01_compute_masked_vegetationindex/)), then create a timelapse on this whole region of interest (https://fordead.gitlab.io/fordead_package/docs/user_guides/Results_visualization/#creer-des-timelapses), then these indices correspond to the indices in the timelapse) 
    The graphs are exported in the data_directory/TimeSeries directory as png files.
    See details here : https://fordead.gitlab.io/fordead_package/docs/user_guides/Results_visualization/
    \f
    Parameters
    ----------
    data_directory
    shape_path
    name_column
    ymin
    ymax
    chunks

    Returns
    -------

    """
    vi_series_visualisation(data_directory, shape_path, name_column, ymin, ymax, chunks)



def vi_series_visualisation(data_directory, shape_path = None, name_column = "id", ymin = 0, ymax = 2, chunks = None):
    
    """
    From previously computed results, graphs the results for specific pixels showing the vegetation index for each dates, the model and the detection.
    By specifying 'shape_path' and 'name_column' parameters, it can be used with a shapefile containing points with a column containing a unique ID used to name the exported image.
    If shape_path is not specified, the user will be prompted to give coordinates in the system of projection of the tile. Graphs can also be plotted for random pixels inside the forest mask.
    The user can also choose to specify pixels by their indices from the top left hand corner of the computed area (If only a small region of interest was computed (for example by using extent_shape_path parameter in the step 01_compute_masked_vegetationindex (https://fordead.gitlab.io/fordead_package/docs/user_guides/01_compute_masked_vegetationindex/)), then create a timelapse on this whole region of interest (https://fordead.gitlab.io/fordead_package/docs/user_guides/Results_visualization/#creer-des-timelapses), then these indices correspond to the indices in the timelapse) 
    The graphs are exported in the data_directory/TimeSeries directory as png files.
    See details here : https://fordead.gitlab.io/fordead_package/docs/user_guides/Results_visualization/
    
    Parameters
    ----------
    data_directory : str
        Path of the directory containing results from the region of interest
    shape_path: str
        Path to shapefile containing points whose data will be plotted. If None, indexes or coordinates for x and y can be given
    name_column: str
        Name of the column containing the name of the point, used to name the exported image. Not used if pixel is selected from indexes or coordinates
    ymin: float
        ymin limit of graph
    ymax: float
        ymax limit of graph
    chunks: int
        Chunk length to import data as dask arrays and save RAM, advised if computed area in data_directory is large

    """
    tile = TileInfo(data_directory)
    tile = tile.import_info()
    
    # IMPORTING ALL DATA
    stack_vi, stack_masks = import_stackedmaskedVI(tile,chunks = chunks)
    stack_vi["DateNumber"] = ("Time", np.array([(datetime.datetime.strptime(date, '%Y-%m-%d')-datetime.datetime.strptime('2015-06-23', '%Y-%m-%d')).days for date in np.array(stack_vi["Time"])]))
    coeff_model = import_coeff_model(tile.paths["coeff_model"],chunks = chunks)
    first_detection_date_index = import_first_detection_date_index(tile.paths["first_detection_date_index"],chunks = chunks)
    soil_data = import_soil_data(tile.paths,chunks = chunks)
    decline_data = import_decline_data(tile.paths,chunks = chunks)
    forest_mask = import_forest_mask(tile.paths["ForestMask"],chunks = chunks)
    tile.getdict_datepaths("Anomalies",tile.paths["AnomaliesDir"])
    anomalies = import_stacked_anomalies(tile.paths["Anomalies"],chunks = chunks)
    
    tile.add_dirpath("series", tile.data_directory / "TimeSeries")
    tile.save_info()
    xx = np.array(range(int(stack_vi.DateNumber.min()), int(stack_vi.DateNumber.max())))
    xxDate=[np.datetime64(datetime.datetime.strptime("2015-06-23", '%Y-%m-%d').date()+ datetime.timedelta(days=int(day)))  for day in xx]
    
    harmonic_terms = np.array([compute_HarmonicTerms(DateAsNumber) for DateAsNumber in xx])
    harmonic_terms = xr.DataArray(harmonic_terms, coords={"Time" : xxDate, "coeff" : [1,2,3,4,5]},dims=["Time","coeff"])
    stack_vi.coords["Time"] = tile.dates.astype("datetime64[D]")
    
    if tile.parameters["correct_vi"]:
        stack_vi = stack_vi + tile.correction_vi
    

    if shape_path is not None:
        shape = gp.read_file(shape_path)
        shape = shape.to_crs(crs = tile.raster_meta["attrs"]["crs"])
        
        for point_index in range(len(shape)):
            id_point = shape.iloc[point_index][name_column]
            geometry_point = shape.iloc[point_index]["geometry"]
            print(id_point)
            
            if forest_mask.sel(x = geometry_point.x, y = geometry_point.y,method = "nearest"):
                pixel_series, yy,  xy_soil_data, xy_decline_data, xy_first_detection_date_index = select_pixel_from_coordinates(geometry_point.x,geometry_point.y, harmonic_terms, coeff_model, first_detection_date_index, soil_data, decline_data, stack_masks, stack_vi, anomalies)
                fig = plot_temporal_series(pixel_series, xy_soil_data, xy_decline_data, xy_first_detection_date_index, int(geometry_point.x), int(geometry_point.y), yy, tile.parameters["threshold_anomaly"],tile.parameters["vi"],tile.parameters["path_dict_vi"], ymin,ymax)
                fig.savefig(tile.paths["series"] / (str(id_point) + ".png"))
                plt.close()
            else:
                print("Pixel outside forest mask")
    else:
        #Initialiser X,Y
        PixelsToChoose = np.where(forest_mask)
        PixelID=random.randint(0,PixelsToChoose[0].shape[0])
        X=PixelsToChoose[0][PixelID]
        Y=PixelsToChoose[1][PixelID]
        
        mode = input("Type 'c' to input coordinates as coordinates in the system of projection of the tile\nType 'i' to input coordinates by positional indexing as using the pixel index from the top left hand corner\n[c/i]?")
        
        while X!=-1:
            
            X=input("X ? ")
            if X=="":
                #PIXEL ALEATOIRE DANS LE MASQUE FORET
                PixelID=random.randint(0,PixelsToChoose[0].shape[0])
                X=PixelsToChoose[1][PixelID]
                Y=PixelsToChoose[0][PixelID]
                pixel_series, yy,  xy_soil_data, xy_decline_data, xy_first_detection_date_index = select_pixel_from_indices(X,Y, harmonic_terms, coeff_model, first_detection_date_index, soil_data, decline_data, stack_masks, stack_vi, anomalies)
                fig = plot_temporal_series(pixel_series, xy_soil_data, xy_decline_data, xy_first_detection_date_index, X, Y, yy, tile.parameters["threshold_anomaly"],tile.parameters["vi"],tile.parameters["path_dict_vi"],ymin,ymax)
                fig.savefig(tile.paths["series"] / ("X"+str(int(pixel_series.x))+"_Y"+str(int(pixel_series.y))+".png"))
                plt.show()
                plt.close()
            elif X=="-1":
                #ARRET SI X = -1
                break
            else:
                #CHOIX DU PIXEL
                if mode == "c":
                    #A PARTIR DES COORDONNEES
                    X=int(X)
                    Y=int(input("Y ? "))
                    pixel_series, yy,  xy_soil_data, xy_decline_data, xy_first_detection_date_index = select_pixel_from_coordinates(X,Y, harmonic_terms, coeff_model, first_detection_date_index, soil_data, decline_data, stack_masks, stack_vi, anomalies)
                    xy_forest_mask = forest_mask.sel(x = X, y = Y,method = "nearest")
                elif mode == "i":
                    #A PARTIR DE L'INDICE
                    X=int(X)
                    Y=int(input("Y ? "))
                    pixel_series, yy,  xy_soil_data, xy_decline_data, xy_first_detection_date_index = select_pixel_from_indices(X,Y, harmonic_terms, coeff_model, first_detection_date_index, soil_data, decline_data, stack_masks, stack_vi, anomalies)
                    xy_forest_mask = forest_mask.isel(x = X, y = Y)
                else:
                    raise Exception("Index or coordinate mode incorrect. Type 'c' for coordinate mode, 'i' for index mode")
                    
                #PLOTTING
                if xy_forest_mask:
                    fig = plot_temporal_series(pixel_series, xy_soil_data, xy_decline_data, xy_first_detection_date_index, X, Y, yy, tile.parameters["threshold_anomaly"],tile.parameters["vi"],tile.parameters["path_dict_vi"],ymin,ymax)
                    fig.savefig(tile.paths["series"] / ("X"+str(int(pixel_series.x))+"_Y"+str(int(pixel_series.y))+".png"))
                    plt.show()
                    plt.close()
                else:
                    print("Pixel outside forest mask")
    
if __name__ == '__main__':
    # print(dictArgs)
    cli_vi_series_visualisation()