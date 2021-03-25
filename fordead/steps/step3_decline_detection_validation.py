# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 09:25:23 2020

@author: Raphaël Dutrieux
"""


import click
# import numpy as np
from fordead.ImportData import import_coeff_model, import_decline_data, initialize_decline_data, import_masked_vi, import_first_detection_date_index, TileInfo, import_forest_mask, import_soil_data,import_resampled_sen_stack
from fordead.writing_data import write_tif
from fordead.decline_detection import detection_anomalies, detection_decline_validation
from fordead.ModelVegetationIndex import correct_vi_date, prediction_vegetation_index

import geopandas as gp
import json
import rasterio
import numpy as np
import pandas as pd
import xarray as xr
from numpy import nan

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
        
        rasterized_validation_data = rasterio.features.rasterize(ScolytesTerrain_jsonMask,out_shape = (raster_metadata["sizes"]["y"],raster_metadata["sizes"]["x"]) ,dtype="int16",transform=raster_metadata["attrs"]['transform'])  
                                      
    else:
        rasterized_validation_data = np.zeros((raster_metadata["sizes"]["y"],raster_metadata["sizes"]["x"]),dtype="uint8")
    
    return xr.DataArray(rasterized_validation_data,coords={"y" : raster_metadata["coords"]["y"],"x" : raster_metadata["coords"]["x"]}, dims=["y","x"])



@click.command(name='decline_detection')
@click.option("-d", "--data_directory",  type=str, help="Dossier avec les données")
@click.option("-s", "--threshold_anomaly",  type=float, default=0.16,
                    help="Seuil minimum pour détection d'anomalies", show_default=True)
@click.option("--vi",  type=str, default=None,
                    help="Chosen vegetation index, only useful if step1 was skipped", show_default=True)
@click.option("--path_dict_vi",  type=str, default=None,
                    help="Path of text file to add vegetation index formula, only useful if step1 was skipped", show_default=True)
@click.option("--ground_obs_path",  type=str, help = "Dossier contenant les shapefiles de données de validation")
def cli_decline_detection(
    data_directory,
    ground_obs_path,
    threshold_anomaly=0.16,
    vi = None,
    path_dict_vi = None,
    ):
    """
    Produce the anomaly detection from the model
    \f
    Parameters
    ----------
    data_directory
    threshold_anomaly
    vi
    path_dict_vi

    Returns
    -------

    """
    decline_detection(data_directory, threshold_anomaly, vi, path_dict_vi)


def decline_detection(
    data_directory,
    ground_obs_path,
    threshold_anomaly=0.16,
    vi = None,
    path_dict_vi = None
    ):
    """
    Produce the anomaly detection from the model
    \f
    Parameters
    ----------
    data_directory
    threshold_anomaly
    vi
    path_dict_vi

    Returns
    -------

    """

    tile = TileInfo(data_directory)
    tile = tile.import_info()
    tile.add_parameters({"threshold_anomaly" : threshold_anomaly})
    if tile.parameters["Overwrite"] : 
        tile.delete_dirs("AnomaliesDir","state_decline" ,"periodic_results_decline","result_files","timelapse","series", "validation") #Deleting previous detection results if they exist
        if hasattr(tile, "last_computed_anomaly"): delattr(tile, "last_computed_anomaly")
            
    if vi==None : vi = tile.parameters["vi"]
    if path_dict_vi==None : path_dict_vi = tile.parameters["path_dict_vi"] if "path_dict_vi" in tile.parameters else None
    
    tile.add_dirpath("AnomaliesDir", tile.data_directory / "DataAnomalies") #Choose anomalies directory
    tile.getdict_datepaths("Anomalies",tile.paths["AnomaliesDir"]) # Get paths and dates to previously calculated anomalies
    tile.search_new_dates() #Get list of all used dates
    
    tile.add_path("state_decline", tile.data_directory / "DataDecline" / "state_decline.tif")
    tile.add_path("first_date_decline", tile.data_directory / "DataDecline" / "first_date_decline.tif")
    tile.add_path("count_decline", tile.data_directory / "DataDecline" / "count_decline.tif")
    tile.add_dirpath("validation", tile.data_directory / "Validation")

    if tile.parameters["correct_vi"]:
        forest_mask = import_forest_mask(tile.paths["ForestMask"])
    # raster_id_validation_data=get_rasterized_validation_data(validation_data_directory / ("scolyte"+tile_name[1:]+".shp"), raster_metadata, False)
    valid_area_mask = import_forest_mask(tile.paths["valid_area_mask"])
    raster_id_validation_data=get_rasterized_validation_data(ground_obs_path, tile.raster_meta, False)
    # raster_binary_validation_data = (raster_id_validation_data!=0) & valid_area_mask
    raster_binary_validation_data = (raster_id_validation_data!=0)

    nb_pixels = int(np.sum(raster_binary_validation_data))

    if np.any(raster_binary_validation_data):
        #Verify if there are new SENTINEL dates
        new_dates = tile.dates[tile.dates > tile.last_computed_anomaly] if hasattr(tile, "last_computed_anomaly") else tile.dates[tile.dates >= tile.parameters["min_last_date_training"]]
        if  len(new_dates) == 0:
            print("Decline detection : no new dates")
        else:
            print("Decline detection : " + str(len(new_dates))+ " new dates")
            
            #IMPORTING DATA
            first_detection_date_index = import_first_detection_date_index(tile.paths["first_detection_date_index"])
            coeff_model = import_coeff_model(tile.paths["coeff_model"])
            
            if tile.paths["state_decline"].exists():
                decline_data = import_decline_data(tile.paths)
            else:
                decline_data = initialize_decline_data(first_detection_date_index.shape,first_detection_date_index.coords)
            soil_data = import_soil_data(tile.paths)
           
            #DECLINE DETECTION
            for date_index, date in enumerate(tile.dates):
                masked_vi = import_masked_vi(tile.paths, date)
                if tile.parameters["correct_vi"]:
                    masked_vi["vegetation_index"], tile.correction_vi = correct_vi_date(masked_vi,forest_mask, tile.large_scale_model, date, tile.correction_vi)

                soil = (soil_data["first_date"] <= date_index) & soil_data["state"]
                predicted_vi=prediction_vegetation_index(coeff_model,[date])
                B2 = import_resampled_sen_stack(tile.paths["Sentinel"][date], ["B2"], interpolation_order = 0, extent = tile.raster_meta["extent"])

                
                if date not in new_dates:
                    anomalies = xr.DataArray(np.zeros(first_detection_date_index.shape,dtype=bool),coords={"y" : tile.raster_meta["coords"]["y"],"x" : tile.raster_meta["coords"]["x"]}, dims=["y","x"])
                    changes = [nan]*nb_pixels
                else:
                    
                    anomalies = detection_anomalies(masked_vi["vegetation_index"], predicted_vi, threshold_anomaly, 
                                                    vi = vi, path_dict_vi = path_dict_vi).squeeze("Time")
                                    
                    decline_data, changes = detection_decline_validation(decline_data, anomalies, masked_vi["mask"] | (date_index < first_detection_date_index), date_index, raster_binary_validation_data)
                                   
                    write_tif(anomalies, first_detection_date_index.attrs, tile.paths["AnomaliesDir"] / str("Anomalies_" + date + ".tif"),nodata=0)
                    
                # affected= (detected+2*soil).data
                d1 = {'IdZone': raster_id_validation_data.data[raster_binary_validation_data],
                      "IdPixel" : range(nb_pixels),
                      "Date" : [date]*nb_pixels,
                      'State': soil.data[raster_binary_validation_data],
                      "vi" : (masked_vi["vegetation_index"].data)[raster_binary_validation_data],
                      "Mask" : (masked_vi["mask"].data)[raster_binary_validation_data],
                      "outside_swath" : B2.squeeze("band").data[raster_binary_validation_data]==-10000,
                      "Anomaly" : anomalies.data[raster_binary_validation_data],
                      "Predicted_vi" : predicted_vi.squeeze("Time").data[raster_binary_validation_data],
                      "Change" : [index if np.isnan(index) else tile.dates[int(index)] for index in changes]}
                      # "DiffSeuil" : stackDiff[dateIndex,:,:][raster_binary_validation_data],
                      # "EtatStress" : stackStress[dateIndex,:,:][raster_binary_validation_data]}
                
                Results = pd.DataFrame(data=d1)
                
                # print("to dataframe")
                Results.to_csv(tile.paths["validation"] / 'Evolution_data.csv', mode='a', index=False,header=not((tile.paths["validation"] / 'Evolution_data.csv').exists()))
                print('\r', date, " | ", len(tile.dates)-date_index-1, " remaining", sep='', end='', flush=True) if date_index != (len(tile.dates) -1) else print('\r', "                                              ", sep='', end='\r', flush=True) 

            tile.last_computed_anomaly = new_dates[-1]
                    
            #Writing decline data to rasters        
            write_tif(decline_data["state"], first_detection_date_index.attrs,tile.paths["state_decline"],nodata=0)
            write_tif(decline_data["first_date"], first_detection_date_index.attrs,tile.paths["first_date_decline"],nodata=0)
            write_tif(decline_data["count"], first_detection_date_index.attrs,tile.paths["count_decline"],nodata=0)
            
            d2 = {'IdZone': raster_id_validation_data.data[raster_binary_validation_data],
                  "IdPixel" : range(nb_pixels),
                  "coeff1" : coeff_model.sel(coeff = 1).data[raster_binary_validation_data],
                  "coeff2" : coeff_model.sel(coeff = 2).data[raster_binary_validation_data],
                  "coeff3" : coeff_model.sel(coeff = 3).data[raster_binary_validation_data],
                  "coeff4" : coeff_model.sel(coeff = 4).data[raster_binary_validation_data],
                  "coeff5" : coeff_model.sel(coeff = 5).data[raster_binary_validation_data],
                  "valid" : valid_area_mask.data[raster_binary_validation_data],
                  "first_detection_date" : tile.dates[first_detection_date_index.data[raster_binary_validation_data]],
                  "Vegetation_Index" : tile.parameters["vi"],
                  "threshold_anomaly" : tile.parameters["threshold_anomaly"]
                  }
            
            Results2 = pd.DataFrame(data=d2)
            Results2.to_csv(tile.paths["validation"] / 'Pixel_data.csv', mode='a', index=False,header=not((tile.paths["validation"] / 'Pixel_data.csv').exists()))
                    
            # print("Détection du déperissement")
        tile.save_info()



if __name__ == '__main__':
    # print(dictArgs)
    # start_time = time.time()
    cli_decline_detection()
    # print("Temps d execution : %s secondes ---" % (time.time() - start_time))
