# -*- coding: utf-8 -*-
"""
Created on Thu Oct  1 14:56:23 2020

@author: raphael.dutrieux
"""
import matplotlib.pyplot as plt
import numpy as np
import datetime
import matplotlib.dates as mdates
import random
import geopandas as gp
import argparse
import xarray as xr

from fordead.ImportData import TileInfo, import_stackedmaskedVI, import_stacked_anomalies, import_coeff_model, import_forest_mask, import_first_detection_date_index, import_decline_data, import_soil_data
from fordead.ModelVegetationIndex import compute_HarmonicTerms

# =============================================================================
#  IMPORT DES DONNEES CALCULEES
# =============================================================================
def parse_command_line():
    # execute only if run as a script
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--data_directory", dest = "data_directory", type = str, help = "Dossier contenant les données calculées")
    parser.add_argument("--shape_path", dest = "shape_path",type = str, help = "Path to shapefile containing points whose data will be plotted. They must contain an 'id' field. If None, indexes for x and y can be given")
    

    dictArgs={}
    for key, value in parser.parse_args()._get_kwargs():
    	dictArgs[key]=value
    return dictArgs

# =============================================================================
# # IMPORT ALL DATA
# =============================================================================
def plot_temporal_series(pixel_series, xy_soil_data, xy_decline_data, xy_first_detection_date_index, X,Y, yy, threshold_anomaly):
        fig=plt.figure(figsize=(10,7))
        ax = plt.gca()
        formatter = mdates.DateFormatter("%b %Y")
        ax.xaxis.set_major_formatter(formatter)
        
        plt.xticks(rotation=30)
        if pixel_series.Soil.any() : pixel_series.where(pixel_series.Soil,drop=True).plot.line('k^', label='Coupe') 
        if xy_first_detection_date_index !=0:
            pixel_series.where(pixel_series.training_date & ~pixel_series.mask,drop=True).plot.line("bo", label='Apprentissage')
            if (~pixel_series.training_date & ~pixel_series.Anomaly & ~pixel_series.mask).any() : pixel_series.where(~pixel_series.training_date & ~pixel_series.Anomaly & ~pixel_series.mask,drop=True).plot.line("o",color = '#1fca3b', label='Dates sans anomalies') 
            if (~pixel_series.training_date & pixel_series.Anomaly & ~pixel_series.mask).any() : pixel_series.where(~pixel_series.training_date & pixel_series.Anomaly,drop=True).plot.line("r*", markersize=9, label='Dates avec anomalies') 
  
            #Plotting vegetation index model and anomaly threshold
            yy.plot.line("b", label='Modélisation du CRSWIR sur les dates d\'apprentissage')
            (yy+threshold_anomaly).plot.line("b--", label='Seuil de détection des anomalies')
            
            #Plotting vertical lines when decline or soil is detected
            if ~xy_decline_data["state"] & ~xy_soil_data["state"]:
                plt.title("X : " + str(X)+"   Y : " + str(Y)+"\nPixel sain",size=15)
            elif xy_decline_data["state"] & ~xy_soil_data["state"]:
                date_atteint = pixel_series.Time[int(xy_decline_data["first_date"])].data
                plt.axvline(x=date_atteint, color='red', linewidth=3, linestyle=":",label="Détection de déperissement")
                plt.title("X : " + str(X)+"    Y : " + str(Y)+"\nPixel atteint, première anomalie le " + str(date_atteint.astype("datetime64[D]")),size=15)
            elif xy_decline_data["state"] & xy_soil_data["state"]:
                date_atteint = pixel_series.Time[int(xy_decline_data["first_date"])].data
                date_coupe = pixel_series.Time[int(xy_soil_data["first_date"])].data
                plt.axvline(x=date_atteint, color="red", linewidth=3, linestyle=":")
                plt.axvline(x=date_coupe,color='black', linewidth=3, linestyle=":")
                plt.title("X : " + str(X)+"   Y : " + str(Y)+"\nPixel atteint, première anomalie le " + str(date_atteint.astype("datetime64[D]")) + ", coupé le " + str(date_coupe.astype("datetime64[D]")),size=15)
            else:
                date_coupe = pixel_series.Time[int(xy_soil_data["first_date"])].data
                plt.axvline(x=date_coupe, color='black', linewidth=3, linestyle=":",label="Détection de coupe")
                plt.title("X : " + str(X)+"   Y : " + str(Y)+"\nPixel coupé, détection le " + str(date_coupe.astype("datetime64[D]")),size=15)
        else:
            pixel_series.where(~pixel_series.mask,drop=True).plot.line("bo")
            plt.title("X : " + str(X)+"   Y : " + str(Y)+"\n Not enough dates to compute a model",size=15)
            

        #Plotting vertical lines delimiting years
        plt.axvline(x=datetime.datetime.strptime("2016-01-01", '%Y-%m-%d'),color="black")
        plt.axvline(x=datetime.datetime.strptime("2017-01-01", '%Y-%m-%d'),color="black")
        plt.axvline(x=datetime.datetime.strptime("2018-01-01", '%Y-%m-%d'),color="black")
        plt.axvline(x=datetime.datetime.strptime("2019-01-01", '%Y-%m-%d'),color="black")
        plt.axvline(x=datetime.datetime.strptime("2020-01-01", '%Y-%m-%d'),color="black")
        
        plt.legend()
        plt.ylim((0,2))
        plt.xlabel("Date",size=15)
        plt.ylabel("Vegetation index",size=15)
            
        plt.show()
        return fig


def vi_series_visualisation(data_directory, shape_path):
    
    
    data_directory = "C:/Users/admin/Documents/Deperissement/fordead_data/output_detection/ROI8"
    shape_path = None
    
    tile = TileInfo(data_directory)
    tile = tile.import_info()
    chunks = None
    
    stack_vi, stack_masks = import_stackedmaskedVI(tile,chunks = chunks)
    coeff_model = import_coeff_model(tile.paths["coeff_model"],chunks = chunks)
    first_detection_date_index = import_first_detection_date_index(tile.paths["first_detection_date_index"],chunks = chunks)
    soil_data = import_soil_data(tile.paths,chunks = chunks)
    decline_data = import_decline_data(tile.paths,chunks = chunks)
    used_area_mask = import_forest_mask(tile.paths["valid_area_mask"],chunks = chunks)
    tile.getdict_datepaths("Anomalies",tile.paths["AnomaliesDir"])
    anomalies = import_stacked_anomalies(tile.paths["Anomalies"],chunks = chunks)
    
    
    
    tile.add_dirpath("series", tile.data_directory / "SeriesTemporelles")
    
    xx = np.array(range(int(stack_vi.DateNumber.min()), int(stack_vi.DateNumber.max())))
    xxDate=[np.datetime64(datetime.datetime.strptime("2015-06-23", '%Y-%m-%d').date()+ datetime.timedelta(days=int(day)))  for day in xx]
    
    harmonic_terms = np.array([compute_HarmonicTerms(DateAsNumber) for DateAsNumber in xx])
    harmonic_terms = xr.DataArray(harmonic_terms, coords={"Time" : xxDate, "coeff" : [1,2,3,4,5]},dims=["Time","coeff"])
    stack_vi.coords["Time"] = tile.dates.astype("datetime64[D]")


    if shape_path != None:
        shape = gp.read_file(shape_path)
        shape = shape.to_crs(crs = stack_vi.crs)
        
        for point_index in range(len(shape)):
            id_point = shape.iloc[point_index]["id"]
            geometry_point = shape.iloc[point_index]["geometry"]
            
            xy_first_detection_date_index = int(first_detection_date_index.sel(x = geometry_point.x, y = geometry_point.y,method = "nearest"))
            xy_soil_data = soil_data.sel(x = geometry_point.x, y = geometry_point.y,method = "nearest")
            xy_stack_masks = stack_masks.sel(x = geometry_point.x, y = geometry_point.y,method = "nearest")
            pixel_series = stack_vi.sel(x = geometry_point.x, y = geometry_point.y,method = "nearest")
            if xy_first_detection_date_index!=0:
                xy_anomalies = anomalies.sel(x = geometry_point.x, y = geometry_point.y,method = "nearest")
                xy_decline_data = decline_data.sel(x = geometry_point.x, y = geometry_point.y,method = "nearest")
                
                
            pixel_series = pixel_series.assign_coords(Soil = ("Time", [index >= int(xy_soil_data["first_date"]) if xy_soil_data["state"] else False for index in range(pixel_series.sizes["Time"])]))
            pixel_series = pixel_series.assign_coords(mask = ("Time", xy_stack_masks))
            if xy_first_detection_date_index!=0:
                anomalies_time = xy_anomalies.Time.where(xy_anomalies,drop=True).astype("datetime64").data.compute()
                pixel_series = pixel_series.assign_coords(Anomaly = ("Time", [time in anomalies_time for time in stack_vi.Time.data]))
                pixel_series = pixel_series.assign_coords(training_date=("Time", [index < xy_first_detection_date_index for index in range(pixel_series.sizes["Time"])]))
                yy = (harmonic_terms * coeff_model.sel(x = geometry_point.x, y = geometry_point.y,method = "nearest").compute()).sum(dim="band")
            
            fig = plot_temporal_series(pixel_series, xy_soil_data, xy_decline_data, xy_first_detection_date_index, int(geometry_point.x), int(geometry_point.y), yy, tile.parameters["threshold_anomaly"])
            fig.savefig(tile.paths["series"] / ("id_" + str(id_point) + ".png"))
    
    else:
    
        PixelsToChoose = np.where(used_area_mask)
        PixelID=random.randint(0,PixelsToChoose[0].shape[0])
        X=PixelsToChoose[0][PixelID]
        Y=PixelsToChoose[1][PixelID]
    
        while X!=-1:
            
            X=input("X ? ")
            if X=="":
                PixelsToChoose = np.where(used_area_mask)
                PixelID=random.randint(0,PixelsToChoose[0].shape[0])
                X=PixelsToChoose[1][PixelID]
                Y=PixelsToChoose[0][PixelID]
            elif X=="-1":
                break
            else:
                X=int(X)
                Y=int(input("Y ? "))
        
            yy = (harmonic_terms * coeff_model.isel(x = X, y = Y).compute()).sum(dim="coeff")
            
            xy_first_detection_date_index = int(first_detection_date_index.isel(x = X, y = Y))
            xy_soil_data = soil_data.isel(x = X, y = Y)
            xy_stack_masks = stack_masks.isel(x = X, y = Y)
            pixel_series = stack_vi.isel(x = X, y = Y)
            if xy_first_detection_date_index!=0:
                xy_anomalies = anomalies.isel(x = X, y = Y)
                xy_decline_data = decline_data.isel(x = X, y = Y)
    
            pixel_series = pixel_series.assign_coords(Soil = ("Time", [index >= int(xy_soil_data["first_date"]) if xy_soil_data["state"] else False for index in range(pixel_series.sizes["Time"])]))
            pixel_series = pixel_series.assign_coords(mask = ("Time", xy_stack_masks))
            if xy_first_detection_date_index!=0:
                anomalies_time = xy_anomalies.Time.where(xy_anomalies,drop=True).astype("datetime64").data.compute()
                pixel_series = pixel_series.assign_coords(Anomaly = ("Time", [time in anomalies_time for time in stack_vi.Time.data]))
                pixel_series = pixel_series.assign_coords(training_date=("Time", [index < xy_first_detection_date_index for index in range(pixel_series.sizes["Time"])]))
            # stack_vi = stack_vi.assign_coords(training_date=("Time", [index < int(first_detection_date_index[X,Y]) for index in range(stack_vi.sizes["Time"])]))
            # stack_vi = stack_vi.assign_coords(Soil = ("Time", [index >= int(soil_data["first_date"][X,Y]) if soil_data["state"][X,Y] else False for index in range(stack_vi.sizes["Time"])]))
            # stack_vi = stack_vi.assign_coords(Anomaly = ("Time", [index >= int(soil_data["first_date"][X,Y]) if soil_data["state"][X,Y] else False for index in range(stack_vi.sizes["Time"])]))
            # stack_vi = stack_vi.assign_coords(mask = ("Time", stack_masks[:,X,Y]))
    
            #ax.axvspan(datetime.datetime.strptime("2015-06-23", '%Y-%m-%d').date()+ datetime.timedelta(days=int(np.array(mydataTested.Day)[IndexStress[k]])),datetime.datetime.strptime("2015-06-23", '%Y-%m-%d').date()+ datetime.timedelta(days=int(np.array(mydataTested.Day)[IndexStress[k+1]])),color="orange",alpha=0.5)
            
            fig = plot_temporal_series(pixel_series, xy_soil_data, xy_decline_data, xy_first_detection_date_index, X, Y, yy, tile.parameters["threshold_anomaly"])
            fig.savefig(tile.paths["series"] / ("X"+str(X)+"_Y"+str(Y)+".png"))
    
if __name__ == '__main__':
    dictArgs=parse_command_line()
    # print(dictArgs)
    vi_series_visualisation(**dictArgs)