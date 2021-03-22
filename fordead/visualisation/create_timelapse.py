# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 10:30:53 2020

@author: Raphael Dutrieux


Crée un timelapse à partir des résultats calculés


"""

#%% =============================================================================
#   LIBRAIRIES
# =============================================================================

# from glob import glob
import geopandas as gp
import argparse
# import time
from plotly.offline import plot
    
# %%=============================================================================
#  IMPORT LIBRAIRIES PERSO
# =============================================================================

from fordead.timelapse import CreateTimelapse
from fordead.ImportData import TileInfo

# =============================================================================
#  CHOIX PARAMETRES
# =============================================================================

def parse_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data_directory", dest = "data_directory",type = str, help = "Directory with the computed results of decline detection")
    parser.add_argument("--obs_terrain_path", dest = "obs_terrain_path",type = str, help = "Path of the shapefile with ground observations")
    parser.add_argument("--shape_path", dest = "shape_path",type = str, help = "Path of the shapefile of the area to convert to timelapse")
    parser.add_argument("--coordinates", dest = "coordinates",type = tuple, help = "Tuple of coordinates in the crs of the Sentinel-2 tile. Format : (x,y)")
    parser.add_argument("--buffer", dest = "buffer",type = int, default = 100, help = "Buffer around polygons or points for the extent of the timelapse")
    parser.add_argument("--name_column", dest = "name_column",type = str, default = "id", help = "Name of the column containing the name of the export. Not used if timelapse made from coordinates")
    dictArgs={}
    for key, value in parser.parse_args()._get_kwargs():
    	dictArgs[key]=value
    return dictArgs

#%% =============================================================================
#   MAIN CODE
# =============================================================================
       
DictCol={'C' : "white",
         'V' : "lawngreen",
         "R" : "red",
         'S' : "black",
         'I' : "darkgreen",
         'G' : "darkgray",
         'X' : "indianred"}

#DictColAtteint={1 : "yellow",
#         2 : "black",
#         3 : "blue"}

def create_timelapse(data_directory, obs_terrain_path = None, shape_path = None, coordinates = None, buffer = 100, name_column = "id"):
    
    
    tile = TileInfo(data_directory)
    tile = tile.import_info()
    # tile.add_parameters({"shape_path" : shape_path})
    # if tile.parameters["Overwrite"] : tile.delete_dirs("timelapse") #Deleting previous detection results if they exist
    tile.add_dirpath("timelapse", tile.data_directory / "Timelapses")
    tile.save_info()
    
    if coordinates is not None:
        print("Timelapse created from coordinates")
        ShapeInteret = gp.GeoDataFrame({"id" : [str(coordinates[0])+"_"+str(coordinates[1])]},geometry = gp.points_from_xy([coordinates[0]], [coordinates[1]]))
        name_column = "id"
    elif shape_path is not None:
        print("Timelapse(s) created from " + shape_path)
        ShapeInteret=gp.read_file(shape_path)
        ShapeInteret=ShapeInteret.to_crs(crs = tile.raster_meta["attrs"]["crs"])
    else:
        raise Exception("No shape_path or coordinates")

    for ShapeIndex in range(ShapeInteret.shape[0]):
        Shape=ShapeInteret.iloc[ShapeIndex:(ShapeIndex+1)]
        try:
            NameFile = str(Shape[name_column].iloc[0])
        except KeyError:
            raise Exception("No column "+name_column+" in " + shape_path)
        
        # if not((tile.paths["timelapse"] / (NameFile + ".html")).exists()):
        print("Creating timelapse | Id : " + NameFile)
        fig = CreateTimelapse(Shape.geometry.buffer(buffer),tile,DictCol, obs_terrain_path)
        plot(fig,filename=str(tile.paths["timelapse"] / (NameFile + ".html")),auto_open=False)


if __name__ == '__main__':
    dictArgs=parse_command_line()
    # print(dictArgs)
    create_timelapse(**dictArgs)

