# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 09:42:31 2020

@author: admin
"""

import numpy as np
import xarray as xr
import re
import datetime
from pathlib import Path
import pickle
import shutil
from scipy import ndimage


import rioxarray
import geopandas as gp

def get_band_paths(dict_sen_paths):
    DictSentinelPaths={}
    for date in dict_sen_paths:
        AllPaths = dict_sen_paths[date].glob("**/*.tif")
        DictSentinelPaths[date]={}
        for path in AllPaths:
            path=str(path)
            if "B2" in path or "B02" in path:
                DictSentinelPaths[date]["B2"]=Path(path)
            if "B3" in path or "B03" in path:
                DictSentinelPaths[date]["B3"]=Path(path)
            if "B4" in path or "B04" in path:
                DictSentinelPaths[date]["B4"]=Path(path)
            if "B5" in path or "B05" in path:
                DictSentinelPaths[date]["B5"]=Path(path)
            if "B6" in path or "B06" in path:
                DictSentinelPaths[date]["B6"]=Path(path)
            if "B7" in path or "B07" in path:
                DictSentinelPaths[date]["B7"]=Path(path)
            if ("B8" in path or "B08" in path) and not("B8A" in path):
                DictSentinelPaths[date]["B8"]=Path(path)
            if "B8A" in path:
                DictSentinelPaths[date]["B8A"]=Path(path)
            if "B11" in path:
                DictSentinelPaths[date]["B11"]=Path(path)
            if "B12" in path:
                DictSentinelPaths[date]["B12"]=Path(path)
                
            if "_CLM_" in path or "SCL" in path:
                DictSentinelPaths[date]["Mask"]=Path(path)
   
    return DictSentinelPaths


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
    else:
        return None
            
    return formatted_date

class TileInfo:
    def __init__(self, data_directory):
        """
        Initialize TileInfo object, deletes previous results if they exist.
        """
        self.data_directory = Path(data_directory)
        self.data_directory.mkdir(parents=True, exist_ok=True)   
        self.paths={}
        
        # print(globals())


    def import_info(self, path= None):
        """ Imports TileInfo object in the data_directory, or the one at path if the parameter is given"""
        
        if path == None:
            path = self.data_directory / "TileInfo"
        if path.exists():
            with open(path, 'rb') as f:
                tuile = pickle.load(f)
                return tuile
        else:
            return self

    def save_info(self, path= None):
        """
        Saves the TileInfo object in its data_directory by default or in specified location
        """
        if path==None:
            path=self.data_directory / "TileInfo"
        with open(path, 'wb') as f:
            pickle.dump(self, f)
    

    def delete_dirs(self,*key_paths):
        """
        Using keys to paths (usually added through add_path or add_dirpath), deletes directory containing the file, or the directory if the path already links to a directory. 

        Parameters
        ----------
        key_path : str
            Key in the dictionnary containing paths

        Returns
        -------
        None.

        """
        for key_path in key_paths:
            if key_path in self.paths:
                if self.paths[key_path].is_dir():
                    shutil.rmtree(self.paths[key_path])
                elif self.paths[key_path].is_file():
                    shutil.rmtree(self.paths[key_path].parent)
   
    def delete_files(self,*key_paths):
        """
        Using keys to paths (usually added through add_path), deletes file 

        Parameters
        ----------
        key_path : str
            Key in the dictionnary containing paths

        Returns
        -------
        None.

        """
        for key_path in key_paths:
            print(key_paths)
            if key_path in self.paths:
                if self.paths[key_path].is_file():
                    self.paths[key_path].unlink()
                    
    def getdict_datepaths(self, key, path_dir):
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
        path_dir=Path(path_dir)
        dict_datepaths={}
        for path in path_dir.glob("*"):
            if not(".xml" in str(path)): #To ignore temporary files
                formatted_date=retrieve_date_from_string(path.stem)
                if formatted_date != None: #To ignore files or directories with no dates which might be in the same directory
                    dict_datepaths[formatted_date] = path
            
        sorted_dict_datepaths = dict(sorted(dict_datepaths.items(), key=lambda key_value: key_value[0]))
        self.paths[key] = sorted_dict_datepaths
        
    def getdict_paths(self,
                      path_vi, path_masks):
        
        self.getdict_datepaths("VegetationIndex",path_vi)
        self.getdict_datepaths("Masks",path_masks)
        self.dates = np.array(list(self.paths["VegetationIndex"].keys()))
            
    def add_path(self, key, path):
        #Transform to WindowsPath if not done already
        path=Path(path)
        #Creates missing directories
        path.parent.mkdir(parents=True, exist_ok=True)    
        #Saves paths in the object
        self.paths[key] = path
        
    def add_parameters(self, parameters):
        """
        Adds attribute 'parameters' to TileInfo object which contains dictionnary of parameters and their values.
        If attribute parameters already exists, checks for conflicts then updates parameters
        In case of conflicts, meaning if parameter was unknown or changed, the parameter 'Overwrite' is set to True and it is advised to remove previous results.

        Parameters
        ----------
        parameters : dict
            Dictionnary containing parameters and their values


        """
        if not(hasattr(self, 'parameters')):
            self.parameters = parameters
            self.parameters["Overwrite"]=False
        else:
            self.parameters["Overwrite"]=False
            for parameter in parameters:
                if parameter in self.parameters:
                    if self.parameters[parameter]!=parameters[parameter]: #If parameter was changed
                        self.parameters["Overwrite"]=True
                else:#If unknown parameters
                    self.parameters["Overwrite"]=True
            self.parameters.update(parameters)
        
    def add_dirpath(self, key, path):
        #Transform to WindowsPath if not done already
        path=Path(path)
        #Creates missing directories
        path.mkdir(parents=True, exist_ok=True)    
        #Saves paths in the object
        self.paths[key] = path


    def search_new_dates(self):
        path_vi=self.paths["VegetationIndex"][self.dates[0]].parent
        path_masks=self.paths["Masks"][self.dates[0]].parent
        self.getdict_datepaths("VegetationIndex",path_vi)
        self.getdict_datepaths("Masks",path_masks)
        self.dates = np.array(list(self.paths["VegetationIndex"].keys()))
        
def get_cloudiness(path_cloudiness, dict_path_bands, sentinel_source):
    """
    For every date in dict_path_bands (which is meant to contain each date available in the sentinel data directory), computes the cloudiness percentage from the mask at path dict_path_bands[date]["Mask"] if it was not already computed and stored at path_cloudiness in a TileInfo object.
    Returns a dictionnary where the key is the date and the value is the cloudiness percentage.

    """
    path_cloudiness= Path(path_cloudiness)
    cloudiness = TileInfo(path_cloudiness.parent)
    if path_cloudiness.exists():
        cloudiness=cloudiness.import_info(path_cloudiness)
    if not(hasattr(cloudiness, 'perc_cloud')):
        cloudiness.perc_cloud={}
    for date in dict_path_bands:
        if not(date in cloudiness.perc_cloud):
            cloudiness.perc_cloud[date] = get_date_cloudiness_perc(dict_path_bands[date], sentinel_source)
            
    cloudiness.save_info(path_cloudiness)
    return cloudiness

def get_date_cloudiness_perc(date_paths, sentinel_source):
    """
    Computes cloudiness percentage of a Sentinel-2 date from the source mask (THEIA CLM or PEPS, scihub SCL)
    """

    if sentinel_source=="THEIA":
        tile_mask_info = xr.Dataset({"mask": xr.open_rasterio(date_paths["Mask"]),
                                     "swath_cover": xr.open_rasterio(date_paths["B11"])})
        NbPixels = (tile_mask_info["swath_cover"]!=-10000).sum()
        NbCloudyPixels = (tile_mask_info["mask"]>0).sum()

    elif sentinel_source=="Scihub" or sentinel_source=="PEPS":
        cloud_mask = xr.open_rasterio(date_paths["Mask"])
        NbPixels = (cloud_mask!=0).sum()
        NbCloudyPixels = (~cloud_mask.isin([4,5])).sum()
    
    if NbPixels==0: #If outside of satellite swath
        return 2.0
    else:
        return float(NbCloudyPixels/NbPixels) #Number of cloudy pixels divided by number of pixels in the satellite swath

def get_raster_metadata(raster_path = None,raster = None, extent = None):
    if raster_path != None:
        raster = xr.open_rasterio(raster_path)
    if extent is not None:
        raster = raster.loc[dict(x=slice(extent[0], extent[2]),y = slice(extent[3],extent[1]))]
    raster_meta = {"dims" : raster.dims,
                   "coords" : raster.coords,
                   "attrs" : raster.attrs,
                   "sizes" : raster.sizes,
                   "shape" : raster.shape}
    return raster_meta
    

# def get_extent(shape = None, shape_path = None):
    
#     if shape_path == None and shape == None:
#         return None
#     else:
#         if shape_path != None:
#             shape = gp.read_file(shape_path)
#         extent = shape.total_bounds
#         extent[2] = extent[2] + 20 - (extent[2]-extent[0]) % 20
#         extent[1] = extent[1] + 20 - (extent[1]-extent[3]) % 20

#         return extent



def import_resampled_sen_stack(band_paths, list_bands, InterpolationOrder = 0, extent = None):
    #Importing data from files
    
    if extent is None:
            stack_bands = [xr.open_rasterio(band_paths[band]) for band in list_bands]
    else:
        stack_bands = [xr.open_rasterio(band_paths[band],chunks = 1280).loc[dict(x=slice(extent[0]-20, extent[2]+20),y = slice(extent[3]+20,extent[1]-20))].compute() for band in list_bands]
    
    #Resampling at 10m resolution
    for band_index in range(len(stack_bands)):
        if stack_bands[band_index].attrs["res"]==(20.0,20.0):            
            # stack_bands[band_index] = xr.DataArray(ndimage.zoom(stack_bands[band_index],zoom=[1,2.0,2.0],order=InterpolationOrder), 
            #                                        coords=stack_bands[0].coords)
            stack_bands[band_index] = xr.DataArray(ndimage.zoom(stack_bands[band_index],zoom=[1,2.0,2.0],order=InterpolationOrder), 
                                                   coords={"band" : [1], 
                                                           "y" : np.linspace(stack_bands[band_index].isel(x=0,y=0).y+5, stack_bands[band_index].isel(x=0,y=stack_bands[band_index].sizes["y"]-1).y-5, num=stack_bands[band_index].sizes["y"]*2),
                                                           "x" : np.linspace(stack_bands[band_index].isel(x=0,y=0).x-5, stack_bands[band_index].isel(x=stack_bands[band_index].sizes["x"]-1,y=0).x+5, num=stack_bands[band_index].sizes["x"]*2)},
                                                   dims=["band","y","x"])
        if extent is not None:
            stack_bands[band_index] = stack_bands[band_index].loc[dict(x=slice(extent[0], extent[2]),y = slice(extent[3],extent[1]))]

    concatenated_stack_bands= xr.concat(stack_bands,dim="band")
    concatenated_stack_bands.coords["band"] = list_bands
    # concatenated_stack_bands=concatenated_stack_bands.chunk({"band": 1,"x" : -1,"y" : 100})
    concatenated_stack_bands.attrs["nodata"] = 0
    concatenated_stack_bands.attrs["crs"]=concatenated_stack_bands.crs.replace("+init=","")
    return concatenated_stack_bands


        
def import_forest_mask(forest_mask_path,chunks = None):
    forest_mask = xr.open_rasterio(forest_mask_path,chunks = chunks)
    forest_mask=forest_mask[0,:,:]
    # forest_mask=forest_mask.rename({"band" : "Mask"})
    return forest_mask.astype(bool)


def import_stackedmaskedVI(tuile,date_lim_training=None,chunks = None):
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
    if date_lim_training==None:
        filter_dates=False
        date_lim_training=""
    else:
        filter_dates=True
        
    list_vi=[xr.open_rasterio(tuile.paths["VegetationIndex"][date],chunks =chunks) for date in tuile.paths["VegetationIndex"] if date <= date_lim_training or not(filter_dates)]
    stack_vi=xr.concat(list_vi,dim="Time")
    stack_vi=stack_vi.assign_coords(Time=[date for date in tuile.paths["VegetationIndex"].keys() if date <= date_lim_training or not(filter_dates)])
    stack_vi=stack_vi.squeeze("band")
    stack_vi=stack_vi.chunk({"Time": -1,"x" : chunks,"y" : chunks})    
    stack_vi["DateNumber"] = ("Time", np.array([(datetime.datetime.strptime(date, '%Y-%m-%d')-datetime.datetime.strptime('2015-06-23', '%Y-%m-%d')).days for date in np.array(stack_vi["Time"])]))

    
    list_mask=[xr.open_rasterio(tuile.paths["Masks"][date],chunks =chunks) for date in tuile.paths["Masks"] if date <= date_lim_training or not(filter_dates)]
    stack_masks=xr.concat(list_mask,dim="Time")
    stack_masks=stack_masks.assign_coords(Time=[date for date in tuile.paths["Masks"].keys() if date <= date_lim_training or not(filter_dates)]).astype(bool)
    stack_masks=stack_masks.squeeze("band")
    stack_masks=stack_masks.chunk({"Time": -1,"x" : chunks,"y" : chunks})
    stack_masks["DateNumber"] = ("Time", np.array([(datetime.datetime.strptime(date, '%Y-%m-%d')-datetime.datetime.strptime('2015-06-23', '%Y-%m-%d')).days for date in np.array(stack_masks["Time"])]))

    return stack_vi, stack_masks

    
def import_coeff_model(path, chunks = None):
    coeff_model = xr.open_rasterio(path,chunks = chunks)
    coeff_model = coeff_model.rename({"band": "coeff"})
    return coeff_model

def import_first_detection_date_index(path,chunks = None):
    first_detection_date_index=xr.open_rasterio(path,chunks = chunks)
    first_detection_date_index=first_detection_date_index.squeeze("band")
    return first_detection_date_index

def import_decline_data(dict_paths, chunks = None):
    state_decline = xr.open_rasterio(dict_paths["state_decline"],chunks = chunks).astype(bool)
    first_date_decline = xr.open_rasterio(dict_paths["first_date_decline"],chunks = chunks)
    count_decline = xr.open_rasterio(dict_paths["count_decline"],chunks = chunks)
    
    decline_data=xr.Dataset({"state": state_decline,
                     "first_date": first_date_decline,
                     "count" : count_decline})
    decline_data=decline_data.squeeze("band")

    return decline_data
        
def initialize_decline_data(shape,coords):
    
    count_decline= np.zeros(shape,dtype=np.uint8) #np.int8 possible ?
    first_date_decline=np.zeros(shape,dtype=np.uint16) #np.int8 possible ?
    state_decline=np.zeros(shape,dtype=bool)
    
    decline_data=xr.Dataset({"state": xr.DataArray(state_decline, coords=coords),
                         "first_date": xr.DataArray(first_date_decline, coords=coords),
                         "count" : xr.DataArray(count_decline, coords=coords)})
    
    return decline_data


def import_soil_data(dict_paths, chunks = None):
    state_soil = xr.open_rasterio(dict_paths["state_soil"], chunks = chunks).astype(bool)
    first_date_soil = xr.open_rasterio(dict_paths["first_date_soil"], chunks = chunks)
    count_soil = xr.open_rasterio(dict_paths["count_soil"], chunks = chunks)
    
    soil_data=xr.Dataset({"state": state_soil,
                     "first_date": first_date_soil,
                     "count" : count_soil})
    soil_data=soil_data.squeeze("band")

    return soil_data

def initialize_soil_data(shape,coords):
    state_soil=np.zeros(shape,dtype=bool)
    first_date_soil=np.zeros(shape,dtype=np.uint16) #np.int8 possible ?
    count_soil= np.zeros(shape,dtype=np.uint8) #np.int8 possible ?
    
    soil_data=xr.Dataset({"state": xr.DataArray(state_soil, coords=coords),
                         "first_date": xr.DataArray(first_date_soil, coords=coords),
                         "count" : xr.DataArray(count_soil, coords=coords)})
    
    return soil_data

def import_masked_vi(dict_paths, date, chunks = None):
    vegetation_index = xr.open_rasterio(dict_paths["VegetationIndex"][date],chunks = chunks)
    mask=xr.open_rasterio(dict_paths["Masks"][date],chunks = chunks).astype(bool)
    
    masked_vi=xr.Dataset({"vegetation_index": vegetation_index,
                             "mask": mask})
    masked_vi=masked_vi.squeeze("band")

    return masked_vi



def import_stacked_anomalies(paths_anomalies, chunks = None):
    list_anomalies=[xr.open_rasterio(paths_anomalies[date], chunks = chunks) for date in paths_anomalies]
    stack_anomalies=xr.concat(list_anomalies,dim="Time")
    stack_anomalies=stack_anomalies.assign_coords(Time=[date for date in paths_anomalies.keys()])
    stack_anomalies=stack_anomalies.squeeze("band")
    stack_anomalies=stack_anomalies.chunk({"Time": -1,"x" : chunks,"y" : chunks})
    # stack_anomalies["DateNumber"] = ("Time", np.array([(datetime.datetime.strptime(date, '%Y-%m-%d')-datetime.datetime.strptime('2015-06-23', '%Y-%m-%d')).days for date in np.array(stack_anomalies["Time"])]))
    return stack_anomalies.astype(bool)