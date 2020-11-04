# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 09:42:31 2020

@author: admin
"""

# import rasterio
# from glob import glob
# import os
# import numpy as np
import xarray as xr
import re



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

def getdict_paths(path_vi,path_masks,path_forestmask):
    DictPaths={"VegetationIndex" : getdict_datepaths(path_vi),
               "Masks" : getdict_datepaths(path_masks),
               "ForestMask" : path_forestmask
               }
    
    return DictPaths

# def getDates(DirectoryPath):
#     """
#     Prend en entrée un dossier avec des fichiers nommés sur le modèle ???????_YYYY-MM-JJ.???
#     Renvoie un array contenant l'ensemble des dates
#     """
#     AllPaths=glob(os.path.join(DirectoryPath,"*"))
#     Dates=[Path[-14:-4] for Path in AllPaths]
#     return np.array(Dates)
def ImportMaskForet(PathMaskForet):
    MaskForet = xr.open_rasterio(PathMaskForet)
    return MaskForet.astype(bool)


def import_stackedmaskedVI(dict_paths):
    """

    Parameters
    ----------
    dict_paths : dict
        Dictionnary containing paths of vegetation index and masks for each date

    Returns
    -------
    stack_vi : xarray.DataArray
        DataArray containing vegetation index value with dimension Time, x and y
    stack_masks : xarray.DataArray
        DataArray containing mask value with dimension Time, x and y

    """
    list_vi=[xr.open_rasterio(dict_paths["VegetationIndex"][date]) for date in dict_paths["VegetationIndex"]]
    stack_vi=xr.concat(list_vi,dim="Time")
    stack_vi=stack_vi.assign_coords(Time=list(dict_paths["VegetationIndex"].keys()))
    
    list_mask=[xr.open_rasterio(dict_paths["Masks"][date]) for date in dict_paths["Masks"]]
    stack_masks=xr.concat(list_mask,dim="Time")
    stack_masks=stack_masks.assign_coords(Time=list(dict_paths["Masks"].keys())).astype(bool)
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