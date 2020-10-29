# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 17:32:34 2020

@author: raphael.dutrieux
"""
import os, time
from glob import glob
import rasterio
import geopandas as gp ; import pandas as pd
import numpy as np
import json
from scipy import ndimage
from shapely.geometry import Polygon

def getRasterizedBDForet(DataDirectory,tuile):
    
    """
    Importe le raster de BDFORET, ou le rasterize à partir des vecteurs de la BDFORET et le sauvegarde.

    Parameters
    ----------
    PathBand: str
        Chemin d'une bande de données SENTINEL-2 qui sert d'exemple pour l'écriture de la BD FORET en raster
    tuile: str
        Nom de la tuile concernée

    Returns
    -------
    RasterizedBDFORET: numpy.ndarray
        (x,y) ndarray de type bool avec True si pixel dans les peuplements concernés
    profile:  rasterio.profiles.Profile
        Métadonnées du raster
    CRS_Tuile: int
        Système de projection de la tuile (Numéro de l'EPSG)
    """
    
    if os.path.exists(os.getcwd()+"/Data/Rasters/"+tuile+"/BDForet_"+tuile+".tif"):
        with rasterio.open(os.getcwd()+"/Data/Rasters/"+tuile+"/BDForet_"+tuile+".tif") as BDFORET: 
            RasterizedBDFORET = BDFORET.read(1).astype("bool")
            profile = BDFORET.profile
            CRS_Tuile = int(str(profile["crs"])[5:])
        print("Import du raster BDFORET")
    else:
        
        if not(os.path.exists(os.getcwd()+"/Data/Rasters")):
            os.mkdir(os.getcwd()+"/Data/Rasters")
        if not(os.path.exists(os.getcwd()+"/Data/Rasters/"+tuile)):
            os.mkdir(os.getcwd()+"/Data/Rasters/"+tuile)
            
        BD_ForetPath=glob(os.getcwd()+"/Data/Vecteurs/BDFORET/BD_Foret*/BD*.shp")
        DepPath=os.getcwd()+"/Data/Vecteurs/Departements/departements-20140306-100m.shp"
#        TuilePath=os.getcwd()+"/Data/Vecteurs/TilesSentinel.shp"
        with rasterio.open(glob(DataDirectory+"/VegetationIndex/"+tuile+"/*.tif")[0]) as exampleRaster:
            CRS_Tuile=int(str(exampleRaster.profile["crs"])[5:])

#            Tuile=gp.read_file(TuilePath)
#            Tuile=Tuile.to_crs(epsg=CRS_Tuile)
#            Tuile=Tuile[Tuile['Name']==tuile[1:]]
#            

            lon_point_list = [B2.profile["transform"][2], B2.profile["transform"][2]+B2.profile["width"]*10, B2.profile["transform"][2]+B2.profile["width"]*10, B2.profile["transform"][2], B2.profile["transform"][2]]
            lat_point_list = [B2.profile["transform"][5], B2.profile["transform"][5], B2.profile["transform"][5]-10*B2.profile["height"], B2.profile["transform"][5]-10*B2.profile["height"],B2.profile["transform"][5]]
            
            polygon_geom = Polygon(zip(lon_point_list, lat_point_list))
            crs = {'init': 'epsg:'+str(CRS_Tuile)}
            Tuile = gp.GeoDataFrame(index=[0], crs=crs, geometry=[polygon_geom])       
#            Tuile.to_file(filename=os.getcwd()+'/Data/Vecteurs/polygon.shp', driver="ESRI Shapefile")
            Departements=gp.read_file(DepPath)
            Departements=Departements.to_crs(epsg=CRS_Tuile) #Changing crs
            DepInZone=gp.overlay(Tuile,Departements)
        
            #Charge la BD FORET des départements concernés et filtre selon le peuplement
            BD_Foret_PathList=[DirDep for DirDep in BD_ForetPath if DirDep.split("_")[-2][-2:] in np.array(DepInZone.code_insee)]
            
            BDList=[(gp.read_file(BDpath,bbox=Tuile)) for BDpath in BD_Foret_PathList]
            BD_Foret = gp.GeoDataFrame( pd.concat( BDList, ignore_index=True), crs=BDList[0].crs )
            BD_Foret=BD_Foret[BD_Foret['CODE_TFV'].isin(["FF2-00-00", "FF2-90-90", "FF2-91-91", "FF2G61-61"])]
            BD_Foret=BD_Foret.to_crs(epsg=CRS_Tuile) #Changing crs
            BD_Foret=BD_Foret["geometry"]
            
            
            # print("BD FORET")
            # print(BD_Foret)
            # BD_Foret.to_file(os.getcwd()+"/Data/Vecteurs/FailedBDFORET.shp")
            #Crop la BD FORET pour retirer les parties hors de la tuile
            # bounding_box = Tuile.envelope
            # gp_bounding_box = gp.GeoDataFrame(gp.GeoSeries(bounding_box), columns=['geometry'],crs=Tuile.crs)
            # BD_Foret=gp.overlay(gp_bounding_box,BD_Foret)
        
            #Transforme le geopanda en json pour rasterisation
            BD_Foret_json_str = BD_Foret.to_json()
            BD_Foret_json_dict = json.loads(BD_Foret_json_str)
            BD_Foret_jsonMask = [feature["geometry"] for feature in BD_Foret_json_dict["features"]]
            
            #Rasterisation de la BDFORET pour créer le masque
        
            RasterizedBDFORET=rasterio.features.rasterize(BD_Foret_jsonMask,out_shape =B2.read(1).shape,default_value =1,fill=0,transform =B2.profile["transform"])
            RasterizedBDFORET=RasterizedBDFORET.astype("bool")
            profile=B2.profile
            
            profile["dtype"]=np.uint8
            with rasterio.open(os.getcwd()+"/Data/Rasters/"+tuile+"/BDForet_"+tuile+".tif", 'w', nbits=1, **profile) as dst:
                dst.write(RasterizedBDFORET.astype("uint8"),indexes=1)
                
            profile=B2.profile
            print("Rasterisation et écriture de la BDFORET")
    return RasterizedBDFORET,profile,CRS_Tuile


# def getNuages(stackBands,stackAtteint,HorsFauche):
#     """
#     Deprecated, use getNuages2
#     """
#     stackNG=stackBands[:,:,:,1]/(stackBands[:,:,:,3]+stackBands[:,:,:,2]+stackBands[:,:,:,1])
#     # stackNG=stackBands[:,:,:,1][StackMaskForetZone]/(stackBands[:,:,:,3][StackMaskForetZone]+stackBands[:,:,:,2][StackMaskForetZone]+stackBands[:,:,:,1][StackMaskForetZone])
#     cond1=stackNG>0.15
#     cond2=stackBands[:,:,:,0]>400
#     cond3=stackBands[:,:,:,0]>700
#     cond4=stackAtteint!=2 #Hors sol nu
#     Nuages2=np.logical_and(np.logical_or(np.logical_and(np.logical_and(HorsFauche,cond1),cond2),cond3),cond4)
    
#     #Dilation nuages AJOUTER MASQUE FORET
#     struct=ndimage.generate_binary_structure(3, 1)
#     struct[0,:,:]=False
#     struct[2,:,:]=False
#     return ndimage.binary_dilation(Nuages2,iterations=3,structure=struct)

def getNuages2(stackBands,DictBandPosition,HorsFauche,BoolSolNu,SolNu):
    
    """
    Calcule le masque de nuages à partir des valeurs des bandes et d'une dilation de 3 pixels

    Parameters
    ----------
    stackBands: numpy.ndarray
        (date,x,y, bande) ndarray avec les 6 bandes utilisées (Bleu,Vert,Rouge,NIR,SWIR1,SWIR2) pour chaque date
    stackSolNu: numpy.ndarray
        (date,x,y) ndarray de type bool avec True si pixel détecté comme sol nu à cette date
    HorsFauche: numpy.ndarray
        (date,x,y) ndarray de type bool avec True si pixel hors de la fauchée du satellite
        
    Returns
    -------
    numpy.ndarray
        (date,x,y) ndarray de type bool avec True si pixel détecté comme nuage
    """
    stackNG=stackBands[:,:,DictBandPosition["B3"]]/(stackBands[:,:,DictBandPosition["B8A"]]+stackBands[:,:,DictBandPosition["B4"]]+stackBands[:,:,DictBandPosition["B3"]])
    # stackNG=stackBands[:,:,:,1]/(stackBands[:,:,:,3]+stackBands[:,:,:,2]+stackBands[:,:,:,1])
    # stackNG=stackBands[:,:,:,1][StackMaskForetZone]/(stackBands[:,:,:,3][StackMaskForetZone]+stackBands[:,:,:,2][StackMaskForetZone]+stackBands[:,:,:,1][StackMaskForetZone])
    cond1=stackNG>0.15
    cond2=stackBands[:,:,DictBandPosition["B2"]]>400
    cond3=stackBands[:,:,DictBandPosition["B2"]]>700
    cond4=np.logical_and(~BoolSolNu,~SolNu) #Hors sol nu
    # cond4=~stackSolNu
    Nuages2=np.logical_and(np.logical_or(np.logical_and(np.logical_and(~HorsFauche,cond1),cond2),cond3),cond4)
    
    #Dilation nuages AJOUTER MASQUE FORET
    struct=ndimage.generate_binary_structure(2, 1)
    return ndimage.binary_dilation(Nuages2,iterations=3,structure=struct)



# def getSolNu(stackBands,SolNu,Invalid):
    
#     """
#     Deprecated, use getSolNu2
#     """
    
#     structSolNu=np.zeros((3,3,3),dtype='bool')
#     structSolNu[1:3,1,1]=True

#     stackAtteint=np.zeros((stackBands.shape[0],stackBands.shape[1],stackBands.shape[2]), dtype='int8')
#     CompteurSolNu= np.zeros((stackBands.shape[1],stackBands.shape[2]),dtype=np.uint8) #np.int8 possible ?
    
#     for date in range(stackBands.shape[0]):
#         CompteurSolNu[np.logical_and(SolNu[date,:,:],~Invalid[date,:,:])]+=1
#         CompteurSolNu[np.logical_and(~SolNu[date,:,:],~Invalid[date,:,:])]=0

#         stackAtteint[date,:,:][CompteurSolNu==1]=4
#         stackAtteint[:,CompteurSolNu==0] = np.where(stackAtteint[:,CompteurSolNu==0] == 4 , 0 , stackAtteint[:,CompteurSolNu==0]) #Les pixels avec CompteurSolNu==0 retournent à 0 là où il y avait des 4
#         stackAtteint[:,CompteurSolNu==3] = np.where(stackAtteint[:,CompteurSolNu==3] == 4 , 2 , stackAtteint[:,CompteurSolNu==3]) #Les pixels avec CompteurSolNu==3 vont à 2 là où il y avait des 4

#     stackAtteint[stackAtteint==4]=0
#     stackAtteint=ndimage.binary_dilation(stackAtteint,iterations=stackAtteint.shape[0],structure=structSolNu).astype("int8")
#     stackAtteint[stackAtteint==1]=2
#     return stackAtteint

def getSolNu2(BoolSolNu,CompteurSolNu,DateFirstSol,SolNu,Invalid,DateIndex):
    
    CompteurSolNu[np.logical_and(SolNu,~Invalid)]+=1
    CompteurSolNu[np.logical_and(~SolNu,~Invalid)]=0
    
    BoolSolNu[CompteurSolNu==3]=True
    DateFirstSol[np.logical_and(np.logical_and(CompteurSolNu==1,~BoolSolNu),~Invalid)]=DateIndex #Garde la première date de détection de sol nu sauf si déjà détécté comme sol nu
        
    # stackSolNu[DateFirstSol,np.arange(stackSolNu.shape[1])[:,None],np.arange(stackSolNu.shape[1])[None,:]]=True #Met True à la date de détection comme sol nu
    # stackSolNu[:,~BoolSolNu]=False #Remet à 0 tous les pixels dont le compteur n'est pas arrivé à 3

    # stackSolNu=ndimage.binary_dilation(stackSolNu,iterations=-1,structure=structSolNu) #Itération pour mettre des TRUE à partir du premier TRUE
    return BoolSolNu, CompteurSolNu, DateFirstSol



def getPreMasks(stackBands, DictBandPosition, MaskTheia, ApplyMaskTheia):
    
    """
    Calcule les pré-masques pour la détection de sol nu

    Parameters
    ----------
    stackBands: numpy.ndarray
        (date,x,y, bande) ndarray avec les 6 bandes utilisées (Bleu,Vert,Rouge,NIR,SWIR1,SWIR2) pour chaque date
    MaskTheia: numpy.ndarray ou []
        (date,x,y) ndarray de type bool, True si pixel masqué par THEIA à cette date. [] si ApplyMaskTheia == False
    ApplyMaskTheia: bool
        Si True, applique le masque THEIA

        
    Returns
    -------
    SolNu: numpy.ndarray
        Pré-masque (date,x,y) ndarray de type bool avec True si pixel est potientiellement sol nu.
    Ombres : numpy.ndarray
        (date,x,y) ndarray de type bool avec True si pixel détecté comme ombre à cette date
    HorsFauche: numpy.ndarray
        (date,x,y) ndarray de type bool avec True si pixel hors de la fauchée du satellite à cette date
    Invalid: numpy.ndarray
        (date,x,y) ndarray de type bool avec True si pixel invalide à cette date (Ombre ou Hors Fauche ou réflectance bleue trop élevée)
    """
    
    # cond1=stackBands[:,:,:,4]>999999 #SWIR haut
    cond1=stackBands[:,:,DictBandPosition["B11"]]>1250 #SWIR haut
    cond2=stackBands[:,:,DictBandPosition["B2"]]<600 #Bleu bas
    cond3=(stackBands[:,:,DictBandPosition["B3"]]+stackBands[:,:,DictBandPosition["B4"]])>800 #900 #Reflectance haute dans le rouge et vert
    # cond4=(stackRGB[:,:,:,1]+stackRGB[:,:,:,2])>800 #900
    SolNu=np.logical_and(cond1,np.logical_and(cond2,cond3))
    Ombres=np.any(stackBands==0,axis=2) #Reflectance d'une des bandes à 0
    Nuages=stackBands[:,:,DictBandPosition["B2"]]>=600 #Reflectance élevée dans le bleu
    HorsFauche=stackBands[:,:,DictBandPosition["B12"]]<0 #<0 -> -10000 Peut retirer aussi des soucis dûs à l'interpolation
    
    if ApplyMaskTheia : Invalid=np.logical_or(np.logical_or(Ombres, Nuages),np.logical_or(MaskTheia,HorsFauche))
    else : Invalid=np.logical_or(np.logical_or(Ombres, Nuages),HorsFauche)
    return SolNu,Ombres,HorsFauche,Invalid



