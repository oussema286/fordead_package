# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 16:21:35 2020

@author: Raphael Dutrieux
"""
import xarray as xr
import numpy as np
import dask.array as da
import datetime

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


def model_vi(stack_vi, stack_masks):      

    """
    Models periodic vegetation index for each pixel.  

    Parameters
    ----------
    stack_vi : array (Time,x,y)
        Array containing vegetation index data, must contain coordinates 'Time' with format '%Y-%m-%d'
    stack_masks : array (Time,x,y)
        Array (boolean) containing mask data.

    Returns
    -------
    coeff_model : array (5,x,y)
        Array containing the five coefficients of the vegetation index model for each pixel

    """
    
    DatesNumbers = [(datetime.datetime.strptime(date, '%Y-%m-%d')-datetime.datetime.strptime('2015-06-23', '%Y-%m-%d')).days for date in np.array(stack_vi["Time"])]
    
    HarmonicTerms = np.array([compute_HarmonicTerms(DateAsNumber) for DateAsNumber in DatesNumbers])
        
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
