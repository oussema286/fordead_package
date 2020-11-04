# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 16:21:15 2020

@author: Raphaël Dutrieux
"""
#%% =============================================================================
#   LIBRAIRIES
# =============================================================================

import argparse
from pathlib import Path
from fordead.ImportData import getdict_paths, ImportMaskForet

def parse_command_line():
    # execute only if run as a script
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--SeuilMin", dest = "SeuilMin",type = float,default = 0.04, help = "Seuil minimum pour détection d'anomalies")
    parser.add_argument("-a", "--CoeffAnomalie", dest = "CoeffAnomalie",type = float,default = 4, help = "Coefficient multiplicateur du seuil de détection d'anomalies")
    parser.add_argument("-k", "--RemoveOutliers", dest = "RemoveOutliers", action="store_false",default = True, help = "Si activé, garde les outliers dans les deux premières années")
    parser.add_argument("-g", "--DateFinApprentissage", dest = "DateFinApprentissage",type = str,default = "2018-06-01", help = "Uniquement les dates antérieures à la date indiquée seront utilisées")
    parser.add_argument("-o", "--DataDirectory", dest = "DataDirectory",type = str,default = "C:/Users/admin/Documents/Deperissement/fordead_data/tests/OutputFordead/ZoneTest", help = "Dossier avec les indices de végétations et les masques")
    dictArgs={}
    for key, value in parser.parse_args()._get_kwargs():
    	dictArgs[key]=value
    
        
    return dictArgs

def TrainForDead(    
    SeuilMin=0.04,
    CoeffAnomalie=4,
    RemoveOutliers=True,
    DateFinApprentissage="2018-06-01",
    DataDirectory = "C:/Users/admin/Documents/Deperissement/fordead_data/tests/OutputFordead/ZoneTest"
    ):
    
    DataDirectory=Path(DataDirectory)
    #Creates a dictionnary containing all paths to vegetation index, masks and forest mask data :
    # VegetationIndex
        #Date : filepath
    # Mask
        #Date : filepath
    # Masque Foret : filepath
        
    DictPaths=getdict_paths(path_vi = DataDirectory / "VegetationIndex",
                            path_masks = DataDirectory / "Mask",
                            path_forestmask = list((DataDirectory / "MaskForet").glob("*.tif"))[0])

    forest_mask = ImportMaskForet(DictPaths["ForestMask"])

if __name__ == '__main__':
    dictArgs=parse_command_line()
    print(dictArgs)
    TrainForDead(**dictArgs)
    




#Import du masque forêt

# Import des index de végétations et des masques

# Pour chaque pixel dans le masque forêt :
    # Déterminer la date à partir de laquelle il y a suffisamment de données valides (si elle existe)
    # Retirer les outliers (optionnel)
    # Modéliser le CRSWIR
    # Mettre dans des rasters l'index de la dernière date utilisée, les coefficients, l'écart type
#Ecrire ces rasters 