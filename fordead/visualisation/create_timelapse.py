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
    parser.add_argument("-s", "--shape_path", dest = "shape_path",type = str, help = "Path of the shapefile of the area to convert to timelapse")
    parser.add_argument("--obs_terrain_path", dest = "obs_terrain_path",type = str, help = "Path of the shapefile with ground observations")
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

def create_timelapse(data_directory,shape_path, obs_terrain_path):
    
    
    tile = TileInfo(data_directory)
    tile = tile.import_info()
    tile.add_parameters({"shape_path" : shape_path})
    if tile.parameters["Overwrite"] : tile.delete_dirs("timelapse") #Deleting previous detection results if they exist
    
    tile.add_dirpath("timelapse", tile.data_directory / "Timelapses")

    tile.save_info()
    ShapeInteret=gp.read_file(shape_path)

    for ShapeIndex in range(ShapeInteret.shape[0]):
        Shape=ShapeInteret.iloc[ShapeIndex:(ShapeIndex+1)]
        if 'Id' in Shape.columns:
            NameFile=str(Shape["Id"].iloc[0])
        else:
            NameFile=str(ShapeIndex)
        print("Creating timelapse | Id : " + NameFile)
        
        # if not((tile.paths["timelapse"] / (NameFile + ".html")).exists()):
        fig = CreateTimelapse(Shape,tile,DictCol, obs_terrain_path)
        plot(fig,filename=str(tile.paths["timelapse"] / (NameFile + ".html")),auto_open=True)


if __name__ == '__main__':
    dictArgs=parse_command_line()
    # print(dictArgs)
    create_timelapse(**dictArgs)

