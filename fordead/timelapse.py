# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 13:37:02 2020

@author: raphael.dutrieux
"""

import plotly.graph_objects as go
import geopandas as gp
import xarray as xr
import rasterio
from affine import Affine
import numpy as np
from shapely.geometry import Polygon

from fordead.ImportData import import_resampled_sen_stack, import_soil_data, import_decline_data, import_forest_mask


def get_stack_rgb(tile, extent, bands = ["B4","B3","B2"]):
    list_rgb = [import_resampled_sen_stack(tile.paths["Sentinel"][date], bands,extent = extent) for date in tile.dates]
    stack_rgb = xr.concat(list_rgb,dim="Time")
    stack_rgb=stack_rgb.assign_coords(Time=tile.dates)
    stack_rgb=stack_rgb.transpose("Time", 'y', 'x',"band")
    return stack_rgb

def polygon_from_coordinate_and_radius(coordinates, radius, crs):
    lon_point_list = [coordinates[0]-radius,coordinates[0]+radius,coordinates[0]+radius,coordinates[0]-radius,coordinates[0]-radius,coordinates[0]-radius]
    lat_point_list = [coordinates[1]+radius,coordinates[1]+radius,coordinates[1]-radius,coordinates[1]-radius,coordinates[1]+radius,coordinates[1]-radius]
    
    polygon_geom = Polygon(zip(lon_point_list, lat_point_list))
    polygon = gp.GeoDataFrame(index=[0], crs=crs, geometry=[polygon_geom])
    return polygon



def CreateTimelapse(shape,tile,DictCol, obs_terrain_path):
        NbData=4
        fig = go.Figure()
        
        
        #Récupération des données raster
        extent= shape.total_bounds
        stack_rgb = get_stack_rgb(tile, extent, bands = ["B4","B3","B2"])
        soil_data = import_soil_data(tile.paths)
        decline_data = import_decline_data(tile.paths)
        soil_data = soil_data.loc[dict(x=slice(extent[0], extent[2]),y = slice(extent[3],extent[1]))]
        decline_data = decline_data.loc[dict(x=slice(extent[0], extent[2]),y = slice(extent[3],extent[1]))]
        forest_mask = import_forest_mask(tile.paths["ForestMask"]).loc[dict(x=slice(extent[0], extent[2]),y = slice(extent[3],extent[1]))]
        
        

#         #Récupération des données observations
        if obs_terrain_path is not None:
            ScolytesObs=gp.read_file(obs_terrain_path,bbox=shape.envelope)
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
                
                
                # valid_area = 
                affected = affected.where(forest_mask,0)
                
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
        if obs_terrain_path is not None:
            Nb_ScolytesObs = ScolytesObs.shape[0]
            for ObsIndex in range(Nb_ScolytesObs):
                
                Obs=ScolytesObs.iloc[ObsIndex]
                coords=Obs['geometry'].exterior.coords.xy
                x1=(coords[0]-np.array(int(stack_rgb.x.min())-5))/10-0.5
                y1=(np.array(int(stack_rgb.y.max())+5)-coords[1])/10-0.5

                
                fig.add_trace(go.Scatter(
                x=x1,
                y=y1, 
                mode='lines',
                line_color=DictCol[Obs['scolyte1']],
                name=Obs['scolyte1'] + " | " + Obs['organisme'] + " : " + Obs['date'],
                hovertemplate=Obs['scolyte1'] + " | " + Obs['organisme'] + " : " + Obs['date']+ '<extra></extra>'
                ))
        else:
            Nb_ScolytesObs = 0
        
        
        #Slider  
        steps = []
        for i in range(nb_valid_dates):
            
            step = dict(
                label = tile.dates[valid_dates][i],
                method="restyle",
                args=["visible", [False] * nb_valid_dates*NbData+[True]*Nb_ScolytesObs])
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