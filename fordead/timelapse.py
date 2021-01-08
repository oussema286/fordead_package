# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 13:37:02 2020

@author: raphael.dutrieux
"""

import plotly.graph_objects as go
# import os
# #from glob import glob
# import earthpy.spatial as es
# import numpy as np
# import rasterio
import geopandas as gp
# import pandas as pd
# from shapely.geometry import mapping
import rioxarray
import xarray as xr
import rasterio
from affine import Affine
import numpy as np

from fordead.ImportData import import_resampled_sen_stack, import_soil_data, import_decline_data


def clip_array_with_shape(shape, array):
    extent = shape.total_bounds
    
    clipped_array = array.rio.clip_box(minx=min(min(array.x),extent[0]),
                               miny=min(min(array.y),extent[1]),
                               maxx=max(max(array.x),extent[2]),
                               maxy=max(max(array.y),extent[3]))
    # clipped_array = array.rio.clip_box(minx=extent[0],
    #                            miny=extent[1],
    #                            maxx=extent[2],
    #                            maxy=extent[3])
    clipped_array.attrs = array.attrs
    
    return array

def get_stack_rgb(shape,tile, bands = ["B4","B3","B2"]):
    # date = tile.dates[0]
    # stack_rgb = import_resampled_sen_stack(tile.paths["Sentinel"][date], bands)
    # clipped_stack_rgb = clip_array_with_shape(shape, stack_rgb)
    
    list_rgb = [clip_array_with_shape(shape, import_resampled_sen_stack(tile.paths["Sentinel"][date], bands)) for date in tile.dates]
    # list_rgb=[]
    # for date in tile.dates:
    #     rgb = import_resampled_sen_stack(tile.paths["Sentinel"][date], bands)
    #     print("imported")
    #     clipped_rgb = clip_array_with_shape(shape, rgb)
    #     print("clipped")
    #     list_rgb+=[clipped_rgb]
    #     print("added")
        
    stack_rgb = xr.concat(list_rgb,dim="Time")
    
    
    
    stack_rgb=stack_rgb.assign_coords(Time=tile.dates)

    
    # clipped_stack_rgb = clip_array_with_shape(shape, stack_rgb)
    stack_rgb=stack_rgb.transpose("Time", 'y', 'x',"band")
    return stack_rgb


    
def CreateTimelapse(shape,tile,DictCol, obs_terrain_path):
        NbData=4
        shape_buffer=shape.geometry.buffer(100)
        fig = go.Figure()
        
        #Récupération des données raster
        stack_rgb = get_stack_rgb(shape_buffer,tile, bands = ["B4","B3","B2"])
        soil_data = import_soil_data(tile.paths)
        decline_data = import_decline_data(tile.paths)
        soil_data = clip_array_with_shape(shape_buffer, soil_data)
        decline_data = clip_array_with_shape(shape_buffer, decline_data)

#         #Récupération des données observations
        ScolytesObs=gp.read_file(obs_terrain_path,bbox=shape_buffer.envelope)
        ScolytesObs=ScolytesObs.to_crs(crs=stack_rgb.crs)
        # CountInvalid=0
        valid_dates = xr.where(stack_rgb == -10000,True,False).sum(dim="x").sum(dim="y").sum(dim="band")/(stack_rgb.size / stack_rgb.sizes["Time"]) < 0.90
        nb_valid_dates = int(valid_dates.sum())
        for dateIndex, date in enumerate(tile.dates):
            if valid_dates.sel(Time = date) == True:
                fig.add_trace(
                    go.Image(
                        visible=False,
                        z=stack_rgb.sel(Time = date).data,
                        name=date,
                        zmin=[0, 0, 0, 0], zmax=[600,600,600,600]))
                
                # Labels+=[date]
                
                DictCoordX={1 : [], 2 : [], 3 : []}
                DictCoordY={1 : [], 2 : [], 3 : []}
                

                detected = (decline_data["first_date"] <= dateIndex) & decline_data["state"]
                soil = (soil_data["first_date"] <= dateIndex) & soil_data["state"]
                affected=detected+2*soil
                
                # forest_mask = import_forest_mask(tile.paths["ForestMask"])
                # valid_area = 
                # affected.where()
                
                results_affected = (
                            {'properties': {'Etat': v}, 'geometry': s}
                            for i, (s, v) 
                            in enumerate(
                                rasterio.features.shapes(affected.data.astype("uint8"), transform=Affine(*stack_rgb.attrs["transform"]))))
                
                geomsaffected = list(results_affected)
                for geom in geomsaffected:
                    if geom["properties"]["Etat"] in [1,2,3]:
#                            print(geom["geometry"]["coordinates"])
                        for poly in geom["geometry"]["coordinates"]:
                            xList=np.array([coord[0] for coord in poly])
                            yList=np.array([coord[1] for coord in poly])
                            
                            DictCoordX[int(geom["properties"]["Etat"])]+=list((xList-np.array(stack_rgb.attrs["transform"][2]))/10-0.5)+[None]
                            DictCoordY[int(geom["properties"]["Etat"])]+=list((np.array(stack_rgb.attrs["transform"][5])-yList)/10-0.5)+[None]
                
                                
                fig.add_trace(go.Scatter(
                    x=DictCoordX[2],
                    y=DictCoordY[2],
                    line_color="black",
                    hoverinfo="skip",
                    name='Sol nu / Coupe rase',
                ))
                

                fig.add_trace(go.Scatter(
                    x=DictCoordX[3],
                    y=DictCoordY[3],
                    line_color="blue",
                    line_width=3,
                    hoverinfo="skip",
                    name='Coupe sanitaire',
                ))
                
                fig.add_trace(go.Scatter(
                    x=DictCoordX[1],
                    y=DictCoordY[1],
                    line_color="yellow",
                    hoverinfo="skip",
                    name='Scolytes détectés',
                ))
                
                
                
            # else:
            #     CountInvalid+=1
        fig.data[0].visible = True
        
    
        
        # Visualisation données terrain
        for ObsIndex in range(ScolytesObs.shape[0]):
            Obs=ScolytesObs.iloc[ObsIndex]
            coords=Obs['geometry'].exterior.coords.xy
            x1=(coords[0]-np.array(stack_rgb.attrs["transform"][2]))/10-0.5
            y1=(np.array(stack_rgb.attrs["transform"][5])-coords[1])/10-0.5
            
            fig.add_trace(go.Scatter(
            x=x1,
            y=y1, 
            mode='lines',
            line_color=DictCol[Obs['scolyte1']],
            name=Obs['scolyte1'] + " | " + Obs['organisme'] + " : " + Obs['date'],
            hovertemplate=Obs['scolyte1'] + " | " + Obs['organisme'] + " : " + Obs['date']+ '<extra></extra>'
            ))
    
        
        #Slider  
        steps = []
        for i in range(nb_valid_dates):
            
            step = dict(
                label = tile.dates[valid_dates][i],
                method="restyle",
                args=["visible", [False] * nb_valid_dates*NbData+[True]*ScolytesObs.shape[0]])
                # args=["visible", [False] * (len(Day)+stackAtteint.shape[0]*3) + [True] * scolytes.shape[0] + [False] * stackMask.shape[0]] ,
            
            step["args"][1][i*NbData] = True  # Toggle i'th trace to "visible"
            step["args"][1][i*NbData+1] = True  # Affiche les scolytes détectés
            step["args"][1][i*NbData+2] = True  # Affiche les scolytes détectés
            step["args"][1][i*NbData+3] = True  # Affiche les scolytes détectés
            # step["args"][1][IndexDay+stackAtteint.shape[0]*3] = True  # Affiche le sol nu
            # step["args"][1][IndexDay+stackAtteint.shape[0]*2] = True  # Affiche les coupes de scolytes
            # step["args"][1][IndexDay+stackAtteint.shape[0]*3+scolytes.shape[0]+stackMask.shape[0]] = True  # Affiche les nuages
            # step["args"][1][IndexDay+stackAtteint.shape[0]*3+scolytes.shape[0]+stackMask.shape[0]*2] = True  # Affiche les ombres
            steps.append(step)
            
        
        sliders = [dict(
            active=1,
            currentvalue={"prefix": "Date : "},
            pad={"t": 50},
            steps=steps
        )]
        
        fig.update_layout(
            sliders=sliders
        )
        
        fig.update_xaxes(range=[0, stack_rgb.shape[1]])
        fig.update_yaxes(range=[stack_rgb.shape[2],0])
        fig.update_layout(showlegend=False)
        
    
        return fig


# def DetermineTuiles(shapeInteret):
#     Tuiles=gp.read_file(os.getcwd()+"/Data/Vecteurs/TilesSentinel.shp")
#     shapeInteret=shapeInteret.to_crs(Tuiles.crs)
#     TuilesOverlay=gp.overlay(shapeInteret,Tuiles)
#     # TuilesOverlay[TuilesOverlay["Name"]=="31UFQ"]
#     CountOverlay=TuilesOverlay["Name"].value_counts().sort_values(ascending=False)
#     TuilesOverlay['Name']=pd.Categorical(TuilesOverlay['Name'], list(CountOverlay.index)) #Donne l'ordre des tuiles selon le nombre d'observations à l'intérieur
#     TuilesOverlay=TuilesOverlay.sort_values(['Id','Name'],ascending=False).groupby("Id").last() #Trie selon l'ordre et prend le premier
#     # TuilesOverlay=TuilesOverlay.groupby("Id").first()
#     return list("T"+np.unique(TuilesOverlay['Name']))