# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 15:38:35 2020

@author: Raphaël Dutrieux
"""
import argparse
from pathlib import Path
from fordead.ImportData import TileInfo, import_masked_vi, get_raster_metadata, import_soil_data, import_decline_data, import_forest_mask
import geopandas as gp
import json
import rasterio
import numpy as np
import pandas as pd
# =============================================================================
# #
# =============================================================================


def get_rasterized_validation_data(path_shape, raster_metadata, ValidationObs):
    """
    Errode les vecteurs d'observations terrain de la tuile puis les transforme en raster avec comme valeur l'identifiant du polygone. 
    
    
    Parameters
    ----------
    
    tuile: str
        Nom de la tuile
    CRS_Tuile: int
        Système de projection de la tuile, numéro d'EPSG
    ValidationObs: bool
        Si True, garde les observations non validées et effectue une dilation plutôt qu'une érosion. Permet d'effectuer les calculs sur les observations non validées afin de créer les timelapses et les valider manuellement.
    MetaProfile: rasterio.profiles.Profile
        Metadata du raster pour écriture
        
    Returns
    -------
    numpy.ndarray
        Observations rasterisées
    """
    
        #Rasterize données terrain
    if path_shape.exists():
        ScolytesTerrain=gp.read_file(path_shape)
        ScolytesTerrain=ScolytesTerrain.to_crs(crs=raster_metadata["attrs"]["crs"])
        
        if ValidationObs:
            ScolytesTerrain['geometry']=ScolytesTerrain.geometry.buffer(10) #Buffer pour avoir au moins un pixel et que l'observation ne soit pas sautée
        else:
            ScolytesTerrain['geometry']=ScolytesTerrain.geometry.buffer(-10)
            ScolytesTerrain=ScolytesTerrain[~(ScolytesTerrain.is_empty)]
            ScolytesTerrain=ScolytesTerrain[ScolytesTerrain["IndSur"]==1]
            
        ScolytesTerrain_json_str = ScolytesTerrain.to_json()
        ScolytesTerrain_json_dict = json.loads(ScolytesTerrain_json_str)
        ScolytesTerrain_jsonMask = [(feature["geometry"],feature["properties"]["Id"]) for feature in ScolytesTerrain_json_dict["features"]]
        return rasterio.features.rasterize(ScolytesTerrain_jsonMask,out_shape = (raster_metadata["sizes"]["x"],raster_metadata["sizes"]["y"]) ,dtype="int16",transform=raster_metadata["attrs"]['transform'])
    else:
        return np.zeros((raster_metadata["sizes"]["x"],raster_metadata["sizes"]["y"]),dtype="uint8")


# =============================================================================
# 
# =============================================================================
def parse_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--main_directory", dest = "main_directory",type = str, default = "D:/Documents/Deperissement/Output_detection", help = "Dossier contenant les dossiers des tuiles")
    parser.add_argument("-d", "--validation_data_directory", dest = "validation_data_directory",default = "C:/Users/admin/Documents/Deperissement/fordead_data/Vecteurs/ObservationsTerrain",type = str, help = "Dossier contenant les shapefiles de données de validation")

    parser.add_argument('-t', '--tiles', nargs='+',default = ["T31UFQ"], help="Liste des tuiles à analyser ex : -t T31UGP T31UGQ")
    
    # parser.add_argument("-x", "--ExportAsShapefile", dest = "ExportAsShapefile", action="store_true",default = False, help = "Si activé, exporte les résultats sous la forme de shapefiles plutôt que de rasters")
    # parser.add_argument("-o", "--Overwrite", dest = "Overwrite", action="store_false",default = True, help = "Si vrai, recommence la détection du début. Sinon, reprends de la dernière date analysée")
    dictArgs={}
    for key, value in parser.parse_args()._get_kwargs():
    	dictArgs[key]=value
    return dictArgs

def validation(main_directory,validation_data_directory, tiles):
    
    main_directory = Path(main_directory)
    validation_data_directory = Path(validation_data_directory)
    
    if (main_directory / 'ResultsTable.csv').exists():
        (main_directory / 'ResultsTable.csv').unlink()
    for tile_name in tiles:
        # stackCRSWIR = 
        # stackPredictedCRSWIR = 
        # stackDiff = 
        # stackStress = 
        
        
        tile = TileInfo(main_directory / tile_name)
        tile = tile.import_info()
        valid_area_mask = import_forest_mask(tile.paths["valid_area_mask"])
        raster_metadata = get_raster_metadata(raster = valid_area_mask)

        raster_id_validation_data=get_rasterized_validation_data(validation_data_directory / ("scolyte"+tile_name[1:]+".shp"), raster_metadata, False)
        raster_binary_validation_data = (raster_id_validation_data!=0) & valid_area_mask.data
        nb_pixels = np.sum(raster_binary_validation_data)
        
        
        
        if np.any(raster_binary_validation_data):
            for dateIndex, date in enumerate(tile.dates):
                print(date)
                masked_vi = import_masked_vi(tile.paths, date)
                soil_data = import_soil_data(tile.paths)
                decline_data = import_decline_data(tile.paths)
                
                detected = (decline_data["first_date"] <= dateIndex) & decline_data["state"]
                soil = (soil_data["first_date"] <= dateIndex) & soil_data["state"]
                affected= (detected+2*soil).data
                    
                d1 = {'IdZone': raster_id_validation_data[raster_binary_validation_data],
                      "IdPixel" : range(nb_pixels),
                      "Date" : [date]*nb_pixels,
                      'Etat': affected[raster_binary_validation_data],
                      "CRSWIR" : (masked_vi["vegetation_index"].data)[raster_binary_validation_data],
                      "Mask" : (masked_vi["mask"].data)[raster_binary_validation_data]}
                      # "PredictedCRSWIR" : stackPredictedCRSWIR[dateIndex,:,:][raster_binary_validation_data],
                      # "DiffSeuil" : stackDiff[dateIndex,:,:][raster_binary_validation_data],
                      # "EtatStress" : stackStress[dateIndex,:,:][raster_binary_validation_data]}
                
                Results = pd.DataFrame(data=d1)
                Results.to_csv(main_directory / 'ResultsTable.csv', mode='a', index=False,header=not((main_directory / 'ResultsTable.csv').exists()))
           
            # d2 = {'IdZone': raster_id_validation_data[raster_binary_validation_data],
            #       "IdZoneXY" : [str(x)+str(y)]*nb_pixels,
            #       "IdPixel" : range(nb_pixels),
            #       "NbStressperiod" : NbStressPeriod[raster_binary_validation_data],
            #       "NbAnomalies" : NbAnomalies[raster_binary_validation_data]}
            
            # Results2 = pd.DataFrame(data=d2)
            # Results2.to_csv(os.getcwd()+"/Out/Results/"+'V'+Version+'/ResultsStress.csv', mode='a', index=False,header=not(os.path.exists(os.getcwd()+"/Out/Results/"+'V'+Version+'/ResultsStress.csv')))



if __name__ == '__main__':
    dictArgs=parse_command_line()
    # print(dictArgs)
    # start_time_debut = time.time()
    validation(**dictArgs)
    # print("Computing forest mask : %s secondes ---" % (time.time() - start_time_debut))

