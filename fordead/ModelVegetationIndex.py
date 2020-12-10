# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 16:21:35 2020

@author: admin
"""
import xarray as xr
import numpy as np
from scipy.linalg import lstsq
import dask.array as da

def get_detection_dates(stack_masks,min_last_date_training,nb_min_date=10):
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
    
    indexes = xr.DataArray(da.ones(stack_masks.shape,dtype=np.uint16, chunks=stack_masks.chunks), stack_masks.coords) * xr.DataArray(range(stack_masks.sizes["Time"]), coords={"Time" : stack_masks.Time},dims=["Time"])   
    cumsum=(~stack_masks).cumsum(dim="Time",dtype=np.uint16)
    
    detection_dates = ((indexes > min_date_index) & (cumsum > nb_min_date))
    first_detection_date_index = detection_dates.argmax(dim="Time").astype(np.uint16)
    
    return detection_dates, first_detection_date_index


def compute_HarmonicTerms(DateAsNumber):
    return np.array([1,np.sin(2*np.pi*DateAsNumber/365.25), np.cos(2*np.pi*DateAsNumber/365.25),np.sin(2*2*np.pi*DateAsNumber/365.25),np.cos(2*2*np.pi*DateAsNumber/365.25)])

def model_pixel_vi(vi_array,mask_array,bool_usedarea,index_last_training_date, 
                    HarmonicTerms,threshold_outliers, remove_outliers):
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
    threshold_outliers : float
        Threshold used for removing outliers if remove_outliers==True
    remove_outliers : bool
        If True, outliers are removed if the difference between the predicted vegetation index and the real vegetation index is greater than threshold_outliers

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
        
        diff=np.abs(valid_vi-np.sum(p*Valid_HarmonicTerms,axis=1)) #Différence entre prédiction et valeur réel pour chaque date 
        
        #POUR RETIRER OUTLIERS
        if remove_outliers:
            Inliers=diff<threshold_outliers
            Valid_HarmonicTerms=Valid_HarmonicTerms[Inliers,:]
            p, _, _, _ = lstsq(Valid_HarmonicTerms, valid_vi[Inliers],
                            overwrite_a=True, overwrite_b = True, check_finite= False)
        return p
    
    return np.array([0,0,0,0,0])


def model_vi(stack_vi, stack_masks):      
# def model_vi(stack_vi, stack_masks,used_area_mask, last_training_date,
#               threshold_outliers=0.16,
#               remove_outliers=True):
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
    threshold_outliers : float, optional
        Threshold used to identify and remove outliers if remove_outliers==True
    remove_outliers : bool, optional
        If True, outliers are removed.
        Outliers are dates where the difference between the predicted vegetation index and the real vegetation index is greater than threshold_outliers. The default is True.

    Returns
    -------
    coeff_model : array (5,x,y)
        Array containing the five coefficients of the vegetation index model for each pixel

    """
    HarmonicTerms = np.array([compute_HarmonicTerms(DateAsNumber) for DateAsNumber in stack_vi["DateNumber"]])

    # coeff_model=xr.apply_ufunc(model_pixel_vi, 
    #                             stack_vi,stack_masks,used_area_mask,last_training_date,
    #                               kwargs={"HarmonicTerms" : HarmonicTerms, "threshold_outliers" : threshold_outliers, "remove_outliers" : remove_outliers},
    #                               input_core_dims=[["Time"],["Time"],[],[]],vectorize=True,dask="parallelized",
    #                               output_dtypes=[float], output_core_dims=[['coeff']],
    #                               dask_gufunc_kwargs = {"output_sizes" : {"coeff" : 5}})
    coeff_model = da.blockwise(censored_lstsq, 'kmn', stack_vi.data, 'tmn',~stack_masks.data, 'tmn', new_axes={'k':5}, dtype=HarmonicTerms.dtype, A=HarmonicTerms, meta=np.ndarray(()))
    coeff_model = xr.DataArray(coeff_model, dims=['coeff', stack_vi.dims[1], stack_vi.dims[2]], coords=[('coeff', np.arange(5)), stack_vi.coords[stack_vi.dims[1]], stack_vi.coords[stack_vi.dims[2]]])

    return coeff_model

def censored_lstsq(B, M, A):
    """Solves least squares problem subject to missing data, compatible with numpy, dask and xarray.

    Code inspired from http://alexhwilliams.info/itsneuronalblog/2018/02/26/censored-lstsq

    Parameters
    ----------
    B : (N, ...) numpy.ndarray or xarray.DataArray
    M : (N, ...) boolean numpy.ndarray or xarray.DataArray
        Mask giving the missing data (when False the data is not used in computation).
        It must have the same size/chunks as B.
    A : (N, P) numpy.array


    Returns
    -------
    X : (P, ...) numpy.ndarray that minimizes norm(M*(AX - B))

    Notes
    -----
    If `B` is two-dimensional (e.g. (N, K)), the least-squares solution is calculated for each of column
    of `B`, returning X with dimension (P, K)

    If B is more than 2D, the computation is made with a reduced to 2D keeping the first dimension to its original size. Same for M.

    It should be used with xr.map_blocks (only full A is needed, B et M can be processed by blocks).

    It uses a broadcasted solve for speed.

        Examples
    --------

    # with numpy array

    # with xarray
    import xarray as xr
    import numpy as np
    xysize = 1098
    tsize = 10
    chunksxy = 100
    chunks3D = {'x':chunksxy, 'y':chunksxy, 'Time':10}
    chunks2D = {'x':chunksxy, 'y':chunksxy}

    B = xr.DataArray(np.arange(np.prod([tsize,xysize,xysize])).reshape((tsize,xysize,xysize)), dims=('Time', "x", "y"),
                            coords=[('Time', np.arange(tsize)), ('x', np.arange(xysize)), ('y', np.arange(xysize))]).chunk(chunks=chunks3D)

    M = xr.DataArray(np.random.rand(tsize,xysize,xysize), dims=('Time', "x", "y"),
                            coords=[('Time', np.arange(tsize)), ('x', np.arange(xysize)), ('y', np.arange(xysize))]).chunk(chunks=chunks3D)>0.05

    A = np.random.rand(tsize, 5)

    # The following are 3 different ways for the same result
    ## xarray
    res = xr.map_blocks(censored_lstsq, B, args=[M], kwargs={'A':A})

    ## dask array blockwise
    res = da.array.blockwise(censored_lstsq, 'kmn', B.data, 'tmn', M.data, 'tmn', new_axes={'k':5}, dtype=A.dtype, A=A, meta=np.ndarray(()))
    res = xr.DataArray(res, dims=['coeff', B.dims[1], B.dims[2]],
                       coords=[('coeff', np.arange(A.shape[1])), B.coords[B.dims[1]],
                               B.coords[B.dims[2]]])

    ## dask map_blockss
    res = da.array.map_blocks(censored_lstsq, B.data, M.data, A=A,
                              chunks=((A.shape[1],), B.chunks[1], B.chunks[2]),
                              meta=np.ndarray(()), dtype=np.float_)
    res = xr.DataArray(res, dims=['coeff', B.dims[1], B.dims[2]],
                       coords=[('coeff', np.arange(A.shape[1])), B.coords[B.dims[1]],
                               B.coords[B.dims[2]]])

    """

    # compatibility with xarray
    if isinstance(B, xr.DataArray):
        if np.sum(B.shape) == 0:  # helps xr.map_blocks finding the template on its own
            res = np.empty((A.shape[1], 0, 0))
        else:
            res = censored_lstsq(B.data, M.data, A)

        out = xr.DataArray(res, dims=['coeff', B.dims[1], B.dims[2]],
                           coords=[('coeff', np.arange(res.shape[0])), B.coords[B.dims[1]],
                                   B.coords[B.dims[2]]])
        return out

    # compatibility with dask.array.blockwise
    if isinstance(B, list):
        B = B[0]
        M = M[0]

    # Note: we should check A is full rank but we won't bother...
    shape = B.shape
    B = B.reshape((shape[0], -1))
    M = M.reshape(shape[0], -1)

    # if B is a vector, simply drop out corresponding rows in A
    if B.ndim == 1 or B.shape[1] == 1:
        return np.linalg.lstsq(A[M], B[M])[0]

    out = np.empty((A.shape[1], M.shape[1]), dtype=A.dtype)
    out[:] = np.nan
    valid_index = (M.sum(axis=0) > A.shape[1])
    B = B[:, valid_index]
    M = M[:, valid_index]

    # else solve via tensor representation
    rhs = np.dot(A.T, M * B).T[:, :, None]  # n x r x 1 tensor
    T = np.matmul(A.T[None, :, :], M.T[:, :, None] * A[None, :, :])  # n x r x r tensor
    out[:, valid_index] = np.squeeze(np.linalg.solve(T, rhs)).T  # transpose to get r x n
    out = out.reshape([A.shape[1]] + list(shape[1:]))
    # del B, M, rhs, T
    return out




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
#                    HarmonicTerms,threshold_outliers, coeff_anomaly, remove_outliers):
#     if bool_usedarea:
#         valid_vi = vi_array[:index_last_training_date+1][~mask_array[:index_last_training_date+1]]
#         Valid_HarmonicTerms = HarmonicTerms[:index_last_training_date+1][~mask_array[:index_last_training_date+1]]
#         p, _, _, _ = lstsq(Valid_HarmonicTerms, valid_vi)
        
#         diffEarlier=np.abs(valid_vi-np.sum(p*Valid_HarmonicTerms,axis=1))
#         sigma=np.std(diffEarlier)
        
#         #POUR RETIRER OUTLIERS
#         if remove_outliers:
#             Outliers=diffEarlier<coeff_anomaly*max(threshold_outliers,sigma)
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
#              threshold_outliers=0.04,
#              coeff_anomaly=4,
#              remove_outliers=True):
    
    
#     HarmonicTerms = np.array([compute_HarmonicTerms(DateAsNumber) for DateAsNumber in stack_vi["DateNumber"]])

#     coeff_model=xr.apply_ufunc(model_pixel_vi, stack_vi,stack_masks,used_area_mask,last_training_date,
#                                   kwargs={"HarmonicTerms" : HarmonicTerms, "threshold_outliers" : threshold_outliers, "coeff_anomaly" : coeff_anomaly, "remove_outliers" : remove_outliers},
#                                   input_core_dims=[["Time"],["Time"],[],[]],dask="parallelized",
#                                   output_dtypes=[float], output_core_dims=[['coeff'], ["sigma"]], output_sizes = {"coeff" : 5,"sigma": 1})
    
#     return coeff_model
