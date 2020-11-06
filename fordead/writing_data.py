# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 17:32:26 2020

@author: admin
"""


def write_coeffmodel(coeff_model,attributes, path):
    coeff_model=coeff_model.transpose('coeff', 'y', 'x')
    coeff_model.attrs=attributes
    coeff_model.attrs["scales"]=coeff_model.attrs["scales"]*coeff_model.shape[0]
    coeff_model.attrs["offsets"]=coeff_model.attrs["offsets"]*coeff_model.shape[0]
    coeff_model.rio.to_raster(path)