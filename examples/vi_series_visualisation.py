# -*- coding: utf-8 -*-
"""
Created on Thu Oct  1 14:56:23 2020

@author: raphael.dutrieux
"""
import matplotlib.pyplot as plt
import numpy as np
import datetime
import matplotlib.dates as mdates
import os
import random
# import rasterio
# import pickle

import xarray as xr
from fordead.ImportData import TileInfo, import_stackedmaskedVI, import_stacked_anomalies, import_coeff_model, import_forest_mask, import_last_training_date, import_decline_data
from fordead.ModelVegetationIndex import compute_HarmonicTerms
from fordead.masking_vi import import_soil_data
# PixelsToChoose = np.where(np.logical_and(np.logical_and(MaskForet==1,stackDetected[-1,:,:]),stackSolNu[-1,:,:]))
# PixelID=random.randint(0,PixelsToChoose[0].shape[0])

# X=PixelsToChoose[0][PixelID]
# Y=PixelsToChoose[1][PixelID]

# =============================================================================
#  IMPORT DES DONNEES CALCULEES
# =============================================================================
        
# for DateIndex,date in enumerate(Dates):
#     with rasterio.open(os.getcwd()+"/Out/Results/"+"V"+Version+"/Out/"+tuile+"/Atteint_"+date+".tif") as Atteint:
#         if DateIndex==0:
#             StackAtteint=np.empty((Dates.shape[0],Atteint.profile["width"],Atteint.profile["height"]),dtype=np.uint8)
#         StackAtteint[DateIndex,:,:]=Atteint.read(1)
# stackSolNu=StackAtteint>=2
# with rasterio.open(os.getcwd()+"/Data/Rasters/"+tuile+"/BDForet_"+tuile+".tif") as BDFORET: 
#     MaskForet = BDFORET.read(1).astype("bool")


data_directory = "G:/Deperissement/Out/PackageVersion/ZoneTest"
tile = TileInfo(data_directory)
tile = tile.import_info()

stack_vi, stack_masks = import_stackedmaskedVI(tile)
# masked_vi=xr.Dataset({"vegetation_index": stack_vi,
#                       "mask": stack_masks})
# stack_vi=stack_vi.where(~stack_masks)


coeff_model = import_coeff_model(tile.paths["coeff_model"])
last_training_date = import_last_training_date(tile.paths["last_training_date"])

tile.getdict_datepaths("Anomalies",tile.paths["AnomaliesDir"])

anomalies = import_stacked_anomalies(tile.paths["Anomalies"])

used_area_mask = import_forest_mask(tile.paths["used_area_mask"])
tile.add_dirpath("series", tile.data_directory / "SeriesTemporelles")

tile.add_path("state_soil", tile.data_directory / "DataSoil" / "state_soil.tif")
tile.add_path("first_date_soil", tile.data_directory / "DataSoil" / "first_date_soil.tif")
tile.add_path("count_soil", tile.data_directory / "DataSoil" / "count_soil.tif")
soil_data = import_soil_data(tile.paths)
###
decline_data = import_decline_data(tile.paths)

xx = np.array(range(int(stack_vi.DateNumber.min()), int(stack_vi.DateNumber.max())))
xxDate=[np.datetime64(datetime.datetime.strptime("2015-06-23", '%Y-%m-%d').date()+ datetime.timedelta(days=int(day)))  for day in xx]


harmonic_terms = np.array([compute_HarmonicTerms(DateAsNumber) for DateAsNumber in xx])
harmonic_terms = xr.DataArray(harmonic_terms, coords={"Time" : xxDate, "band" : [1,2,3,4,5]},dims=["Time","band"])

# =============================================================================
#  PLOTTING
# =============================================================================
PixelsToChoose = np.where(used_area_mask)
PixelID=random.randint(0,PixelsToChoose[0].shape[0])
X=PixelsToChoose[0][PixelID]
Y=PixelsToChoose[1][PixelID]
# print(X)
# print(Y)
while X!=0 and Y!=0:
    
    Y=input("X ? ")
    if Y=="":
        PixelsToChoose = np.where(used_area_mask)
        PixelID=random.randint(0,PixelsToChoose[0].shape[0])
        X=PixelsToChoose[0][PixelID]
        Y=PixelsToChoose[1][PixelID]
    elif Y=="0":
        break
    else:
        Y=int(Y)
        X=int(input("Y ? "))

    yy = (harmonic_terms * coeff_model[:,X,Y].compute()).sum(dim="band")

    fig=plt.figure(figsize=(10,7))
    ax = plt.gca()
    formatter = mdates.DateFormatter("%b %Y")
    ax.xaxis.set_major_formatter(formatter)
    
    plt.xticks(rotation=30)
    
    stack_vi.coords["Time"] = tile.dates.astype("datetime64[D]")

    stack_vi = stack_vi.assign_coords(training_date=("Time", [index <= int(last_training_date[X,Y]) for index in range(stack_vi.sizes["Time"])]))
    stack_vi = stack_vi.assign_coords(Soil = ("Time", [index >= int(soil_data["first_date"][X,Y]) if soil_data["state"][X,Y] else False for index in range(stack_vi.sizes["Time"])]))
    stack_vi = stack_vi.assign_coords(Anomaly = ("Time", [index >= int(soil_data["first_date"][X,Y]) if soil_data["state"][X,Y] else False for index in range(stack_vi.sizes["Time"])]))
    anomalies_time = anomalies.Time.where(anomalies[:,X,Y],drop=True).astype("datetime64").data.compute()
    stack_vi = stack_vi.assign_coords(Anomaly = ("Time", [time in anomalies_time for time in stack_vi.Time.data]))
    stack_vi = stack_vi.assign_coords(mask = ("Time", stack_masks[:,X,Y]))
    
    
    stack_vi[:,X,Y].where(stack_vi.training_date & ~stack_vi.mask,drop=True).plot.line("bo", label='Apprentissage')
    if (~stack_vi.training_date & ~stack_vi.Anomaly & ~stack_vi.mask).any() : stack_vi[:,X,Y].where(~stack_vi.training_date & ~stack_vi.Anomaly,drop=True).plot.line("o",color = '#1fca3b', label='Dates sans anomalies') 
    if (~stack_vi.training_date & stack_vi.Anomaly & ~stack_vi.mask).any() : stack_vi[:,X,Y].where(~stack_vi.training_date & stack_vi.Anomaly,drop=True).plot.line("r*", markersize=9, label='Dates avec anomalies') 
    if stack_vi.Soil.any() : stack_vi[:,X,Y].where(stack_vi.Soil,drop=True).plot.line('k^', label='Coupe') 
    
    #Plotting vegetation index model and anomaly threshold
    yy.plot.line("b", label='Modélisation du CRSWIR sur les dates d\'apprentissage')
    (yy+0.16).plot.line("b--", label='Seuil de détection des anomalies')
    
    #Plotting vertical lines delimiting years
    plt.axvline(x=datetime.datetime.strptime("2016-01-01", '%Y-%m-%d'),color="black")
    plt.axvline(x=datetime.datetime.strptime("2017-01-01", '%Y-%m-%d'),color="black")
    plt.axvline(x=datetime.datetime.strptime("2018-01-01", '%Y-%m-%d'),color="black")
    plt.axvline(x=datetime.datetime.strptime("2019-01-01", '%Y-%m-%d'),color="black")
    plt.axvline(x=datetime.datetime.strptime("2020-01-01", '%Y-%m-%d'),color="black")
    
    #ax.axvspan(datetime.datetime.strptime("2015-06-23", '%Y-%m-%d').date()+ datetime.timedelta(days=int(np.array(mydataTested.Day)[IndexStress[k]])),datetime.datetime.strptime("2015-06-23", '%Y-%m-%d').date()+ datetime.timedelta(days=int(np.array(mydataTested.Day)[IndexStress[k+1]])),color="orange",alpha=0.5)
    
    #Plotting vertical lines when decline or soil is detected
    if ~decline_data["state"][X,Y] & ~soil_data["state"][X,Y]:
        plt.title("X : " + str(Y)+"   Y : " + str(X)+"\nPixel sain",size=15)
    elif decline_data["state"][X,Y] & ~soil_data["state"][X,Y]:
        date_atteint = stack_vi.Time[int(decline_data["first_date"][X,Y])].data
        plt.axvline(x=date_atteint, color='red', linewidth=3, linestyle=":",label="Détection de déperissement")
        plt.title("X : " + str(Y)+"    Y : " + str(X)+"\nPixel atteint, première anomalie le " + str(date_atteint.astype("datetime64[D]")),size=15)
    elif decline_data["state"][X,Y] & soil_data["state"][X,Y]:
        date_atteint = stack_vi.Time[int(decline_data["first_date"][X,Y])].data
        date_coupe = stack_vi.Time[int(soil_data["first_date"][X,Y])].data
        plt.axvline(x=date_atteint, color="red", linewidth=3, linestyle=":")
        plt.axvline(x=date_coupe,color='black', linewidth=3, linestyle=":")
        plt.title("X : " + str(Y)+"   Y : " + str(X)+"\nPixel atteint, première anomalie le " + str(date_atteint.astype("datetime64[D]")) + ", coupé le " + str(date_coupe.astype("datetime64[D]")),size=15)
    else:
        date_coupe = stack_vi.Time[int(soil_data["first_date"][X,Y])].data
        plt.axvline(x=date_coupe, color='black', linewidth=3, linestyle=":",label="Détection de coupe")
        plt.title("X : " + str(Y)+"   Y : " + str(X)+"\nPixel coupé, détection le " + str(date_coupe.astype("datetime64[D]")),size=15)
    
    plt.legend()
    plt.ylim((0,2))
    plt.xlabel("Date",size=15)
    plt.ylabel("CRSWIR",size=15)
        
    # fig.savefig(os.getcwd()+"/Out/Results/V"+Version+"/SeriesTemporelles/X"+str(Y)+"_Y"+str(X)+"_"+"V"+str(Version)+".png")
    plt.show()
