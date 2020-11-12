# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 16:21:35 2020

@author: admin
"""
import xarray as xr
import numpy as np
from scipy.linalg import lstsq

def get_pixel_lastlearningdate(maskarray,forestmask,nb_min_date,min_date_index):
    if forestmask:
        S=0
        for index,value in enumerate(maskarray):
            S+=value
            if (index>=min_date_index) & (S>=nb_min_date):
                return index
    return 0
# find_lastlearningdate=np.vectorize(find_lastlearningdate,signature='(n),(),(),()->()')

def get_last_training_date(stack_masks,forest_mask,min_last_date_training,nb_min_date=10):
    """
    Returns the index of the last date which will be used for training from the masks.
    
    Parameters
    ----------
    stack_masks : xarray.DataArray (Time,x,y)
        Stack of masks with dimensions 
    min_last_date_training : str
        Earliest date at which the training will end and the detection begin
    nb_min_date : int, optional
        Minimum number of dates from which to train the model. The default is 10.

    Returns
    -------
    xarray.DataArray (x,y)
        Array containing the index of the last date which will be used for training, or 0 if there isn't enough valid data.

    """
    
    min_date_index=int(sum(stack_masks.Time<min_last_date_training))-1
    
    IndexLastDate=xr.apply_ufunc(get_pixel_lastlearningdate, (~stack_masks),forest_mask,
                                  kwargs={"nb_min_date" : nb_min_date, "min_date_index" : min_date_index},
                                  input_core_dims=[["Time"],[]],vectorize=True,dask="parallelized")
    return IndexLastDate



def compute_HarmonicTerms(DateAsNumber):
    return np.array([1,np.sin(2*np.pi*DateAsNumber/365.25), np.cos(2*np.pi*DateAsNumber/365.25),np.sin(2*2*np.pi*DateAsNumber/365.25),np.cos(2*2*np.pi*DateAsNumber/365.25)])

def model_pixel_vi(vi_array,mask_array,bool_usedarea,index_last_training_date, 
                    HarmonicTerms,threshold_min, remove_outliers):
    """
    

    Parameters
    ----------
    vi_array : 1-D array (float)
        Array of vegetation index
    mask_array : 1-D array (bool)
        Array of mask
    bool_usedarea : bool
        Boolean, if True, model is computed for the pixel (pixel is in the forest mask and has enough data to compute the model)
    index_last_training_date : int
        Index of the last date used for training
    HarmonicTerms : 1-D array
        Terms of the harmonic function used for the model, calculated from the dates.
    threshold_min : float
        Threshold used for removing outliers if remove_outliers==True
    remove_outliers : bool
        If True, outliers are removed if the difference between the predicted vegetation index and the real vegetation index is greater than threshold_min

    Returns
    -------
    array (5,)
        Returns the 5 coefficients of the model.

    """
    if bool_usedarea:
        valid_vi = vi_array[:index_last_training_date+1][~mask_array[:index_last_training_date+1]]
        Valid_HarmonicTerms = HarmonicTerms[:index_last_training_date+1][~mask_array[:index_last_training_date+1]]
        p, _, _, _ = lstsq(Valid_HarmonicTerms, valid_vi,
                           overwrite_a=True, overwrite_b = True, check_finite= False)
        
        diff=np.abs(valid_vi-np.sum(p*Valid_HarmonicTerms,axis=1))
        
        #POUR RETIRER OUTLIERS
        if remove_outliers:
            Inliers=diff<threshold_min
            Valid_HarmonicTerms=Valid_HarmonicTerms[Inliers,:]
            p, _, _, _ = lstsq(Valid_HarmonicTerms, valid_vi[Inliers],
                           overwrite_a=True, overwrite_b = True, check_finite= False)

        return p
    
    return np.array([0,0,0,0,0])


        
def model_vi(stack_vi, stack_masks,used_area_mask, last_training_date,
              threshold_min=0.16,
              remove_outliers=True):
    """
    Models periodic vegetation index for each pixel.  

    Parameters
    ----------
    stack_vi : array (Time,x,y)
        Array containing vegetation index data
    stack_masks : array (Time,x,y)
        Array (boolean) containing mask data.
    used_area_mask : array (x,y)
        Array (boolean), if pixel is True, model for the vegetation index will be calculated 
    last_training_date : array (x,y)
        Array (int) containing the index of the last date used for training
    threshold_min : float, optional
        Threshold used to identify and remove outliers if remove_outliers==True
    remove_outliers : bool, optional
        If True, outliers are removed.
        Outliers are dates where the difference between the predicted vegetation index and the real vegetation index is greater than threshold_min. The default is True.

    Returns
    -------
    coeff_model : array (5,x,y)
        Array containing the five coefficients of the vegetation index model for each pixel

    """
    
    
    HarmonicTerms = np.array([compute_HarmonicTerms(DateAsNumber) for DateAsNumber in stack_vi["DateNumber"]])

    coeff_model=xr.apply_ufunc(model_pixel_vi, stack_vi,stack_masks,used_area_mask,last_training_date,
                                  kwargs={"HarmonicTerms" : HarmonicTerms, "threshold_min" : threshold_min, "remove_outliers" : remove_outliers},
                                  input_core_dims=[["Time"],["Time"],[],[]],vectorize=True,dask="parallelized",
                                  output_dtypes=[float], output_core_dims=[['coeff']], output_sizes = {"coeff" : 5})
    
    return coeff_model



# def functionToFit(DateAsNumber,p):
#     """
#     Calcule la prédiction de l'indice de végétation à partir du numéro du jour 

#     Parameters
#     ----------
#     x: ndarray
#         Liste de numéros de jours (Nombre de jours entre le lancement du premier satellite et la date voulue)
#     p: ndarray
#         ndarray avec les 5 coefficients permettant de modéliser le CRSWIR

#     Returns
#     -------
#     ndarray
#         Liste du CRSWIR prédit pour chaque jour dans la liste en entrée
#     """
#     # y = p[0] + p[1]*np.sin(2*np.pi*x/365.25)+p[2]*np.cos(2*np.pi*x/365.25)+ p[3]*np.sin(2*2*np.pi*x/365.25)+p[4]*np.cos(2*2*np.pi*x/365.25)
#     y=p*compute_HarmonicTerms(DateAsNumber)
#     print(p)
#     print(compute_HarmonicTerms(DateAsNumber))
#     return y



# def model_pixel_vi(vi_array,mask_array,bool_usedarea,index_last_training_date, 
#                    HarmonicTerms,threshold_min, coeff_anomaly, remove_outliers):
#     if bool_usedarea:
#         valid_vi = vi_array[:index_last_training_date+1][~mask_array[:index_last_training_date+1]]
#         Valid_HarmonicTerms = HarmonicTerms[:index_last_training_date+1][~mask_array[:index_last_training_date+1]]
#         p, _, _, _ = lstsq(Valid_HarmonicTerms, valid_vi)
        
#         diffEarlier=np.abs(valid_vi-np.sum(p*Valid_HarmonicTerms,axis=1))
#         sigma=np.std(diffEarlier)
        
#         #POUR RETIRER OUTLIERS
#         if remove_outliers:
#             Outliers=diffEarlier<coeff_anomaly*max(threshold_min,sigma)
#             Valid_HarmonicTerms=Valid_HarmonicTerms[Outliers,:]
#             p, _, _, _ = lstsq(Valid_HarmonicTerms, valid_vi[Outliers])

#             diffEarlier=np.abs(valid_vi[Outliers]-np.sum(p*Valid_HarmonicTerms,axis=1))
#             sigma=np.std(diffEarlier)
#         print(sigma)
#         print(p)
#         return p,np.array(sigma)
    
#     return np.array([0.0,0.0,0.0,0.0,0.0]),np.array([0.0])
# model_pixel_vi=np.vectorize(model_pixel_vi,signature='(n),(n),(),(),(n),(),(),()->(k),()')



# def model_vi(stack_vi, stack_masks,used_area_mask, last_training_date,
#              threshold_min=0.04,
#              coeff_anomaly=4,
#              remove_outliers=True):
    
    
#     HarmonicTerms = np.array([compute_HarmonicTerms(DateAsNumber) for DateAsNumber in stack_vi["DateNumber"]])

#     coeff_model=xr.apply_ufunc(model_pixel_vi, stack_vi,stack_masks,used_area_mask,last_training_date,
#                                   kwargs={"HarmonicTerms" : HarmonicTerms, "threshold_min" : threshold_min, "coeff_anomaly" : coeff_anomaly, "remove_outliers" : remove_outliers},
#                                   input_core_dims=[["Time"],["Time"],[],[]],dask="parallelized",
#                                   output_dtypes=[float], output_core_dims=[['coeff'], ["sigma"]], output_sizes = {"coeff" : 5,"sigma": 1})
    
#     return coeff_model
