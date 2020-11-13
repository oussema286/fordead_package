# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 09:42:31 2020

@author: admin
"""

# import rasterio
# from glob import glob
# import os
import numpy as np
import xarray as xr
import re
import datetime
from pathlib import Path
import pickle


    



def retrieve_date_from_string(string):
    """
    From a string containing a date in the format YYYY-MM-DD, YYYY_MM_DD, YYYYMMDD, DD-MM-YYYY, DD_MM_YYYY or DDMMYYYY, retrieves the date in the format YYYY-MM-DD.
    Works only for 20th and 21st centuries (years beginning with 19 or 20)

    Parameters
    ----------
    string : str
        String containing a date

    Returns
    -------
    formatted_date : str
        Date in the format YYYY-MM-DD

    """
    matchDMY = re.search(r'[0-3]\d-[0-1]\d-(19|20)\d{2}|[0-3]\d_[0-1]\d_(19|20)\d{2}|[0-3]\d[0-1]\d(19|20)\d{2}', string)
    matchYMD = re.search(r'(19|20)\d{2}-[0-1]\d-[0-3]\d|(19|20)\d{2}_[0-1]\d_[0-3]\d|(19|20)\d{2}[0-1]\d[0-3]\d', string)
    if matchDMY!=None:
        raw_date=matchDMY.group()
        if len(raw_date)==10:
            formatted_date=raw_date[-4:]+"-"+raw_date[3:5]+"-"+raw_date[:2]
        elif len(raw_date)==8:
            formatted_date=raw_date[-4:]+"-"+raw_date[2:4]+"-"+raw_date[:2]
    elif matchYMD!=None:
        raw_date=matchYMD.group()
        if len(raw_date)==10:
            formatted_date=raw_date[:4]+"-"+raw_date[5:7]+"-"+raw_date[-2:]
        elif len(raw_date)==8:
            formatted_date=raw_date[:4]+"-"+raw_date[4:6]+"-"+raw_date[-2:]
            
    return formatted_date

def getdict_datepaths(path_dir):
    """
    Parameters
    ----------
    path_dir : pathlib.WindowsPath
        Directory containing files with filenames containing dates in the format YYYY-MM-DD, YYYY_MM_DD, YYYYMMDD, DD-MM-YYYY, DD_MM_YYYY or DDMMYYYY

    Returns
    -------
    dict_datepaths : dict
        Dictionnary linking formatted dates with the paths of the files from which the dates where extracted

    """
    dict_datepaths={}
    for path in path_dir.glob("*"):
        dict_datepaths[retrieve_date_from_string(path.stem)] = path
    
    return dict_datepaths

class TileInfo:
    def __init__(self, data_directory):
        self.data_directory = Path(data_directory)
        
    def getdict_paths(self,
                      path_vi, path_masks, path_forestmask = None, 
                      path_data_directory = None):
        self.paths={}
        self.paths["VegetationIndex"]=getdict_datepaths(path_vi)
        self.paths["Masks"]=getdict_datepaths(path_masks)
        self.paths["ForestMask"]=path_forestmask
        
        # self.Dates = np.array(list(self.path_vegetationindex.keys()))
        # dict_paths["DatesAsNumber"]=np.array([(datetime.datetime.strptime(date, '%Y-%m-%d')-datetime.datetime.strptime('2015-06-23', '%Y-%m-%d')).days for date in dict_paths["Dates"]]) #Numéro des jours
    
    def add_path(self, key, path):
        #Transform to WindowsPath if not done already
        path=Path(path)
        #Creates missing directories
        path.parent.mkdir(parents=True, exist_ok=True)    
        #Saves paths in the object
        self.paths[key] = path
        
    def save_info(self, path= None):
        if path==None:
            path=self.data_directory / "PathsInfo"
        with open(path, 'wb') as f:
            pickle.dump(self, f)
        
# def getdict_paths(path_vi, path_masks, path_forestmask = None, 
#                   path_data_directory = None):
    
#     dict_paths={"VegetationIndex" : getdict_datepaths(path_vi),
#                "Masks" : getdict_datepaths(path_masks),
#                "ForestMask" : path_forestmask
#                }
    
#     dict_paths["Dates"]=np.array(list(dict_paths["VegetationIndex"].keys()))
#     dict_paths["path_data_directory"]=path_data_directory
#     # dict_paths["DatesAsNumber"]=np.array([(datetime.datetime.strptime(date, '%Y-%m-%d')-datetime.datetime.strptime('2015-06-23', '%Y-%m-%d')).days for date in dict_paths["Dates"]]) #Numéro des jours
    
#     return dict_paths

def ImportMaskForet(PathMaskForet):
    forest_mask = xr.open_rasterio(PathMaskForet,chunks =1000)
    forest_mask=forest_mask[0,:,:]
    # forest_mask=forest_mask.rename({"band" : "Mask"})
    return forest_mask.astype(bool)


def import_stackedmaskedVI(tuile,date_lim_learning=None):
    """

    Parameters
    ----------
    tuile : Object of class TileInfo
        Object containing paths of vegetation index and masks for each date

    Returns
    -------
    stack_vi : xarray.DataArray
        DataArray containing vegetation index value with dimension Time, x and y
    stack_masks : xarray.DataArray
        DataArray containing mask value with dimension Time, x and y

    """
    if date_lim_learning==None:
        filter_dates=False
        date_lim_learning=""
    else:
        filter_dates=True
        
    list_vi=[xr.open_rasterio(tuile.paths["VegetationIndex"][date],chunks =1000) for date in tuile.paths["VegetationIndex"] if date <= date_lim_learning or not(filter_dates)]
    stack_vi=xr.concat(list_vi,dim="Time")
    stack_vi=stack_vi.assign_coords(Time=[date for date in tuile.paths["VegetationIndex"].keys() if date <= date_lim_learning or not(filter_dates)])
    stack_vi=stack_vi.sel(band=1)
    stack_vi=stack_vi.chunk({"Time": -1,"x" : 1000,"y" : 1000})    
    stack_vi["DateNumber"] = ("Time", np.array([(datetime.datetime.strptime(date, '%Y-%m-%d')-datetime.datetime.strptime('2015-06-23', '%Y-%m-%d')).days for date in np.array(stack_vi["Time"])]))

    
    list_mask=[xr.open_rasterio(tuile.paths["Masks"][date],chunks =1000) for date in tuile.paths["Masks"] if date <= date_lim_learning or not(filter_dates)]
    stack_masks=xr.concat(list_mask,dim="Time")
    stack_masks=stack_masks.assign_coords(Time=[date for date in tuile.paths["Masks"].keys() if date <= date_lim_learning or not(filter_dates)]).astype(bool)
    stack_masks=stack_masks.sel(band=1)
    stack_masks=stack_masks.chunk({"Time": -1,"x" : 1000,"y" : 1000})
    stack_masks["DateNumber"] = ("Time", np.array([(datetime.datetime.strptime(date, '%Y-%m-%d')-datetime.datetime.strptime('2015-06-23', '%Y-%m-%d')).days for date in np.array(stack_masks["Time"])]))
    return stack_vi, stack_masks




# def ImportMaskedVI(DataDirectory,tuile,date):
#     VegetationIndex = xr.open_rasterio(DataDirectory+"/VegetationIndex/"+tuile+"/VegetationIndex_"+date+".tif")
#     Mask=xr.open_rasterio(DataDirectory+"/Mask/"+tuile+"/Mask_"+date+".tif").astype(bool)
#     return VegetationIndex, Mask
    
# def ImportModel(tuile,DataDirectory):
#     StackP = xr.open_rasterio(DataDirectory+"/DataModel/"+tuile+"/StackP.tif")
#     rasterSigma = xr.open_rasterio(DataDirectory+"/DataModel/"+tuile+"/rasterSigma.tif")
#     return StackP,rasterSigma

# def ImportDataScolytes(tuile,DataDirectory):
#     BoolEtat = xr.open_rasterio(DataDirectory+"/DataUpdate/"+tuile+"/EtatChange.tif")
#     DateFirstScolyte = xr.open_rasterio(DataDirectory+"/DataUpdate/"+tuile+"/DateFirstScolyte.tif")
#     CompteurScolyte = xr.open_rasterio(DataDirectory+"/DataUpdate/"+tuile+"/CompteurScolyte.tif")
    
#     return BoolEtat, DateFirstScolyte, CompteurScolyte
        
# def InitializeDataScolytes(tuile,DataDirectory,Shape):
#     CompteurScolyte= np.zeros(Shape,dtype=np.uint8) #np.int8 possible ?
#     DateFirstScolyte=np.zeros(Shape,dtype=np.uint16) #np.int8 possible ?
#     EtatChange=np.zeros(Shape,dtype=bool)
    
#     return EtatChange,DateFirstScolyte,CompteurScolyte





# def ImportMaskForet(PathMaskForet):
#     MaskForet = xr.open_rasterio(PathMaskForet)
#     with rasterio.open(PathMaskForet) as BDFORET: 
#         RasterizedBDFORET = BDFORET.read(1).astype("bool")
#         profile = BDFORET.profile
#         CRS_Tuile = int(str(profile["crs"])[5:])
#     return RasterizedBDFORET,profile,CRS_Tuile