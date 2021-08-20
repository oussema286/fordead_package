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
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

from fordead.masking_vi import get_dict_vi
from fordead.import_data import import_resampled_sen_stack, import_soil_data, import_decline_data, import_forest_mask


def get_stack_rgb(tile, extent, bands = ["B4","B3","B2"], dates = None):
    """
    Imports stack of bands, clipped with extent

    Parameters
    ----------
    tile : TileInfo object
        TileInfo objects with paths attribute which is a dictionnary containing file paths to SENTINEL (tile.paths["Sentinel"][YYYY-MM-DD] returns a dictionnary where keys are band names and values are the paths to the files)
    extent : list or 1D array, optional
        Extent used for cropping [xmin,ymin, xmax,ymax]. If None, there is no cropping. The default is None.
    bands : list, optional
        List of bands. The default is ["B4","B3","B2"].
    dates : 1D array or list
        List of dates to import, if None, all dates saved in "tile" TileInfo object are used
    Returns
    -------
    stack_rgb : xarray DataArray
        DataArray with dimensions (x,y,Time,band)

    """
    
    if dates is None:
        dates = tile.dates
    list_rgb = [import_resampled_sen_stack(tile.paths["Sentinel"][date], bands,extent = extent) for date in dates]
    stack_rgb = xr.concat(list_rgb,dim="Time")
    stack_rgb=stack_rgb.assign_coords(Time=dates)
    stack_rgb=stack_rgb.transpose("Time", 'y', 'x',"band")
    return stack_rgb

def polygon_from_coordinate_and_radius(coordinates, radius, crs):
    """
    Creates rectangular polygon from coordinates and a radius

    Parameters
    ----------
    coordinates : list or tuple
        [x,y] list
    radius : int
    crs : str
        crs as understood by geopandas.GeoDataFrame

    Returns
    -------
    polygon : geopandas.GeoDataFrame

    """
    
    lon_point_list = [coordinates[0]-radius,coordinates[0]+radius,coordinates[0]+radius,coordinates[0]-radius,coordinates[0]-radius,coordinates[0]-radius]
    lat_point_list = [coordinates[1]+radius,coordinates[1]+radius,coordinates[1]-radius,coordinates[1]-radius,coordinates[1]+radius,coordinates[1]-radius]
    
    polygon_geom = Polygon(zip(lon_point_list, lat_point_list))
    polygon = gp.GeoDataFrame(index=[0], crs=crs, geometry=[polygon_geom])
    return polygon



def CreateTimelapse(shape,tile,DictCol, obs_terrain_path, max_date):
        NbData=4
        fig = go.Figure()
        
        
        #Récupération des données raster
        extent = shape.total_bounds
        
        if tile.parameters["soil_detection"]:
            soil_data = import_soil_data(tile.paths)
            soil_data = soil_data.loc[dict(x=slice(extent[0], extent[2]),y = slice(extent[3],extent[1]))]

        decline_data = import_decline_data(tile.paths)
        decline_data = decline_data.loc[dict(x=slice(extent[0], extent[2]),y = slice(extent[3],extent[1]))]
        forest_mask = import_forest_mask(tile.paths["ForestMask"]).loc[dict(x=slice(extent[0], extent[2]),y = slice(extent[3],extent[1]))]
        
        #Correcting extent if computed area is smaller than Sentinel-2 data area
        extent = np.array([float(forest_mask[dict(x=0,y=0)].coords["x"])-forest_mask.attrs["transform"][0]/2,
                                                float(forest_mask[dict(x=-1,y=-1)].coords["y"])-forest_mask.attrs["transform"][0]/2,
                                                float(forest_mask[dict(x=-1,y=-1)].coords["x"])+forest_mask.attrs["transform"][0]/2,
                                                float(forest_mask[dict(x=0,y=0)].coords["y"])+forest_mask.attrs["transform"][0]/2])
        
        dates = tile.dates[tile.dates <= max_date] if max_date is not None else tile.dates
        stack_rgb = get_stack_rgb(tile, extent, bands = ["B4","B3","B2"], dates = dates)

#         #Récupération des données observations
        if obs_terrain_path is not None:
            ScolytesObs=gp.read_file(obs_terrain_path,bbox=shape.envelope)
            ScolytesObs=ScolytesObs.to_crs(crs=stack_rgb.crs)
        # CountInvalid=0
        valid_dates = xr.where(stack_rgb == -10000,True,False).sum(dim="x").sum(dim="y").sum(dim="band")/(stack_rgb.size / stack_rgb.sizes["Time"]) < 0.90
        nb_valid_dates = int(valid_dates.sum())
        for dateIndex, date in enumerate(dates):
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
                if tile.parameters["soil_detection"]:
                    soil = (soil_data["first_date"] <= dateIndex) & soil_data["state"]
                    affected=detected+2*soil
                else:
                    affected=detected
                
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
                label = dates[valid_dates][i],
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



def plot_temporal_series(pixel_series, xy_soil_data, xy_decline_data, xy_first_detection_date_index, X,Y, yy, threshold_anomaly, vi, path_dict_vi,ymin,ymax):
    """
    Creates figure from all data

    """

    fig=plt.figure(figsize=(10,7))
    ax = plt.gca()
    formatter = mdates.DateFormatter("%b %Y")
    ax.xaxis.set_major_formatter(formatter)
    
    plt.xticks(rotation=30)
    if pixel_series.Soil.any() : pixel_series.where(pixel_series.Soil,drop=True).plot.line('k^', label='Coupe') 
    
    if xy_first_detection_date_index !=0:
        pixel_series.where(pixel_series.training_date & ~pixel_series.mask,drop=True).plot.line("bo", label='Apprentissage')
        if (~pixel_series.training_date & ~pixel_series.Anomaly & ~pixel_series.mask).any() : pixel_series.where(~pixel_series.training_date & ~pixel_series.Anomaly & ~pixel_series.mask,drop=True).plot.line("o",color = '#1fca3b', label='Dates sans anomalies') 
        if (~pixel_series.training_date & pixel_series.Anomaly & ~pixel_series.mask).any() : pixel_series.where(~pixel_series.training_date & pixel_series.Anomaly & ~pixel_series.mask & ~pixel_series.Soil,drop=True).plot.line("r*", markersize=9, label='Dates avec anomalies') 
  
        #Plotting vegetation index model and anomaly threshold
        yy.plot.line("b", label='Modélisation du '+vi+' sur les dates d\'apprentissage')
        
        dict_vi = get_dict_vi(path_dict_vi)
        if dict_vi[vi]["decline_change_direction"] == "+":
            (yy+threshold_anomaly).plot.line("b--", label='Seuil de détection des anomalies')
        elif dict_vi[vi]["decline_change_direction"] == "-":
            (yy-threshold_anomaly).plot.line("b--", label='Seuil de détection des anomalies')
        
        
        #Plotting vertical lines when decline or soil is detected
        if ~xy_decline_data["state"] & ~xy_soil_data["state"]:
            plt.title("X : " + str(int(pixel_series.x))+"   Y : " + str(int(pixel_series.y))+"\nPixel sain",size=15)
        elif xy_decline_data["state"] & ~xy_soil_data["state"]:
            date_atteint = pixel_series.Time[int(xy_decline_data["first_date"])].data
            plt.axvline(x=date_atteint, color='red', linewidth=3, linestyle=":",label="Détection de déperissement")
            plt.title("X : " + str(int(pixel_series.x))+"    Y : " + str(int(pixel_series.y))+"\nPixel atteint, première anomalie le " + str(date_atteint.astype("datetime64[D]")),size=15)
        elif xy_decline_data["state"] & xy_soil_data["state"]:
            date_atteint = pixel_series.Time[int(xy_decline_data["first_date"])].data
            date_coupe = pixel_series.Time[int(xy_soil_data["first_date"])].data
            plt.axvline(x=date_atteint, color="red", linewidth=3, linestyle=":")
            plt.axvline(x=date_coupe,color='black', linewidth=3, linestyle=":")
            plt.title("X : " + str(int(pixel_series.x))+"   Y : " + str(int(pixel_series.y))+"\nPixel atteint, première anomalie le " + str(date_atteint.astype("datetime64[D]")) + ", coupé le " + str(date_coupe.astype("datetime64[D]")),size=15)
        else:
            date_coupe = pixel_series.Time[int(xy_soil_data["first_date"])].data
            plt.axvline(x=date_coupe, color='black', linewidth=3, linestyle=":",label="Détection de coupe")
            plt.title("X : " + str(int(pixel_series.x))+"   Y : " + str(int(pixel_series.y))+"\nPixel coupé, détection le " + str(date_coupe.astype("datetime64[D]")),size=15)
    else:
        if (~pixel_series.mask).any(): pixel_series.where(~pixel_series.mask,drop=True).plot.line("bo")
        plt.title("X : " + str(int(pixel_series.x))+"   Y : " + str(int(pixel_series.y))+"\n Not enough dates to compute a model",size=15)
         
    [plt.axvline(x=datetime.datetime.strptime(str(year)+"-01-01", '%Y-%m-%d'),color="black") for year in np.arange(pixel_series.isel(Time = 0).Time.data.astype('datetime64[Y]'), (pixel_series.isel(Time = -1).Time.data + np.timedelta64(35,'D')).astype('datetime64[Y]')+1) if str(year)!="2015"]

    plt.legend()
    plt.ylim((ymin,ymax))
    plt.xlabel("Date",size=15)
    plt.ylabel(vi,size=15)
        
    return fig

def select_pixel_from_coordinates(X,Y, harmonic_terms, coeff_model, first_detection_date_index, soil_data, decline_data, stack_masks, stack_vi, anomalies):
    
    xy_first_detection_date_index = int(first_detection_date_index.sel(x = X, y = Y,method = "nearest"))
    xy_soil_data = soil_data.sel(x = X, y = Y,method = "nearest")
    xy_stack_masks = stack_masks.sel(x = X, y = Y,method = "nearest")
    pixel_series = stack_vi.sel(x = X, y = Y,method = "nearest")
    if xy_first_detection_date_index!=0:
        xy_anomalies = anomalies.sel(x = X, y = Y,method = "nearest")
        xy_decline_data = decline_data.sel(x = X, y = Y,method = "nearest")
        anomalies_time = xy_anomalies.Time.where(xy_anomalies,drop=True).astype("datetime64").data.compute()
        pixel_series = pixel_series.assign_coords(Anomaly = ("Time", [time in anomalies_time for time in stack_vi.Time.data]))
        pixel_series = pixel_series.assign_coords(training_date=("Time", [index < xy_first_detection_date_index for index in range(pixel_series.sizes["Time"])]))
        yy = (harmonic_terms * coeff_model.sel(x = X, y = Y,method = "nearest").compute()).sum(dim="coeff")
    else:
        xy_decline_data=None
        xy_anomalies = None
        yy = None
    pixel_series = pixel_series.assign_coords(Soil = ("Time", [index >= int(xy_soil_data["first_date"]) if xy_soil_data["state"] else False for index in range(pixel_series.sizes["Time"])]))
    pixel_series = pixel_series.assign_coords(mask = ("Time", xy_stack_masks))
        
    return pixel_series, yy,  xy_soil_data, xy_decline_data, xy_first_detection_date_index
    
def select_pixel_from_indices(X,Y, harmonic_terms, coeff_model, first_detection_date_index, soil_data, decline_data, stack_masks, stack_vi, anomalies):
    yy = (harmonic_terms * coeff_model.isel(x = X, y = Y).compute()).sum(dim="coeff")
    
    xy_first_detection_date_index = int(first_detection_date_index.isel(x = X, y = Y))
    xy_soil_data = soil_data.isel(x = X, y = Y)
    xy_stack_masks = stack_masks.isel(x = X, y = Y)
    pixel_series = stack_vi.isel(x = X, y = Y)
    if xy_first_detection_date_index!=0:
        xy_anomalies = anomalies.isel(x = X, y = Y)
        xy_decline_data = decline_data.isel(x = X, y = Y)
    else:
        xy_decline_data=None
        xy_anomalies = None
    pixel_series = pixel_series.assign_coords(Soil = ("Time", [index >= int(xy_soil_data["first_date"]) if xy_soil_data["state"] else False for index in range(pixel_series.sizes["Time"])]))
    pixel_series = pixel_series.assign_coords(mask = ("Time", xy_stack_masks))
    if xy_first_detection_date_index!=0:
        anomalies_time = xy_anomalies.Time.where(xy_anomalies,drop=True).astype("datetime64").data.compute()
        pixel_series = pixel_series.assign_coords(Anomaly = ("Time", [time in anomalies_time for time in stack_vi.Time.data]))
        pixel_series = pixel_series.assign_coords(training_date=("Time", [index < xy_first_detection_date_index for index in range(pixel_series.sizes["Time"])]))
    return pixel_series, yy,  xy_soil_data, xy_decline_data, xy_first_detection_date_index
    





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