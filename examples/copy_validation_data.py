# -*- coding: utf-8 -*-
"""
Created on Mon Mar  1 11:10:17 2021

@author: admin
"""
import pandas as pd
from pathlib import Path
from fordead.ImportData import TileInfo
import argparse

def parse_command_line():
    # execute only if run as a script
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--main_directory", dest = "main_directory",type = str, help = "Dossier contenant les dossiers des tuiles")
    parser.add_argument('-t', '--tuiles', nargs='+',default = ["ZoneEtude"], help="Liste des tuiles à analyser ex : -t T31UGP T31UGQ")

    dictArgs={}
    for key, value in parser.parse_args()._get_kwargs():
    	dictArgs[key]=value
    return dictArgs

def copy_validation_data(main_directory, tuiles): #Decline_detection argument

    # sentinel_directory = "D:/Documents/Deperissement/FORMATION_SANTE_FORETS/A_DATA/RASTER/SERIES_SENTINEL"
    # main_directory = "D:/Documents/Deperissement/Output"    
    main_directory = Path(main_directory)
    
    for tuile_index, tuile in enumerate(tuiles):
        tile = TileInfo(main_directory / tuile)
        tile = tile.import_info()
        if tuile == tuiles[0]:
            tile.add_path("pixel_data", main_directory / "All_Results" / 'Pixel_data.csv')
            tile.delete_dirs("pixel_data")
            tile.add_path("pixel_data", main_directory / "All_Results" / 'Pixel_data.csv')
            
            del tile.parameters["list_forest_type"]
            print(tile.parameters)
            parameters = pd.DataFrame(data=tile.parameters)
            parameters = parameters.transpose()
            parameters.insert(0,"parameter",parameters.index)
            parameters=parameters.rename(columns={0: "value"})
            parameters.to_csv(main_directory / "All_Results" / 'parameters.csv', mode='w', index=False,header=True)

        Evolution_data = pd.read_csv(tile.paths["validation"] / 'Evolution_data.csv')
        Pixel_data = pd.read_csv(tile.paths["validation"] / 'Pixel_data.csv')
        Pixel_data.insert(Pixel_data.shape[-1],"Tile", tuile)

        Pixel_data.to_csv(main_directory / "All_Results" / 'Pixel_data.csv', mode='a', index=False,header=not((main_directory / "All_Results" / 'Pixel_data.csv').exists()))
        Evolution_data.to_csv(main_directory / "All_Results" / 'Evolution_data.csv', mode='a', index=False,header=not((main_directory / "All_Results" / 'Evolution_data.csv').exists()))
                

        print('\r', tuile, " | ", len(tuiles)-tuile_index-1, " remaining", sep='', end='', flush=True) if tuile_index != (len(tuiles) -1) else print('\r', "                                              ", sep='', end='\r', flush=True) 

    
    
if __name__ == '__main__':
    dictArgs=parse_command_line()
    # print(dictArgs)
    copy_validation_data(**dictArgs)