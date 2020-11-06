# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 16:21:35 2020

@author: admin
"""
import xarray as xr
# import numpy as np


def find_lastlearningdate(maskarray,forestmask,nb_min_date,min_date_index):
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
    
    IndexLastDate=xr.apply_ufunc(find_lastlearningdate, (~stack_masks),forest_mask,
                                  kwargs={"nb_min_date" : nb_min_date, "min_date_index" : min_date_index},
                                  input_core_dims=[["Time"],["Mask"]],vectorize=True,dask="parallelized")
    return IndexLastDate