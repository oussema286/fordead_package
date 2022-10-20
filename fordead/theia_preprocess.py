# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 13:53:50 2021

@author: Raphael Dutrieux
"""
from pathlib import Path
import os
from zipfile import ZipFile, BadZipfile
import numpy as np
import rasterio
import shutil

from fordead.import_data import retrieve_date_from_string, TileInfo

import glob
import json
import time
import os.path
import sys
# from datetime import date, datetime
if sys.version_info[0] == 2:
    from urllib import urlencode
elif sys.version_info[0] > 2:
    from urllib.parse import urlencode
    

        
def missing_theia_acquisitions(tile, start_date, end_date, write_dir, lim_perc_cloud, login_theia, password_theia, level):
    """
    Checks if there are undownloaded Sentinel-2 acquisitions available

    Parameters
    ----------
    tile : str
        Name of the Sentinel-2 tile (format : "T31UFQ").
    start_date : str
        Acquisitions before this date are ignored (format : "YYYY-MM-DD") 
    end_date : str
        Acquisitions after this date are ignored (format : "YYYY-MM-DD") 
    write_dir : str
        Directory where THEIA data is downloaded
    lim_perc_cloud : int
        Maximum cloud cover (%)
    login_theia : str
        Login of your theia account
    password_theia : str
        Password of your theia account
    level : str
        Product level for reflectance products, can be 'LEVEL1C', 'LEVEL2A' or 'LEVEL3A'

    Returns
    -------
    bool
        True if there are undownloaded acquisitions available, False if not

    """
    

    dict_query = {'location': tile,
                  "startDate" : start_date,
                  'completionDate': end_date, 
                  'maxRecords': 1500, 
                  'processingLevel': level}
    
    config = {'serveur': 'https://theia.cnes.fr/atdistrib', 
              'resto': 'resto2', 
              'token_type': 'text', 
              'login_theia': login_theia, 
              'password_theia': password_theia}

    print("Get theia single sign on token")
    get_token = 'curl -k -s -X POST %s --data-urlencode "ident=%s" --data-urlencode "pass=%s" %s/services/authenticate/>token.json' % (
        "", config["login_theia"], config["password_theia"], config["serveur"])
    
    # print get_token
    
    os.system(get_token)

    query = "%s/%s/api/collections/%s/search.json?" % (
        config["serveur"], config["resto"], "SENTINEL2")+urlencode(dict_query)
    print(query)
    search_catalog = 'curl -k %s -o search.json "%s"' % ("", query)
    print(search_catalog)
    os.system(search_catalog)
    time.sleep(5)
    
    with open('search.json') as data_file:
        data = json.load(data_file)
    
    try:
        for i in range(len(data["features"])):
            prod = data["features"][i]["properties"]["productIdentifier"]
            cloudtemp = data["features"][i]["properties"]["cloudCover"]
            if cloudtemp != None:
                cloudCover = int(cloudtemp)
            else:
                cloudCover = 0
            file_exists = os.path.exists("%s/%s.zip" % (write_dir, prod))
            if not(file_exists) and (cloudCover <= lim_perc_cloud):
                # download only if cloudCover below maxcloud
                return True
    
    except KeyError:
        print("No undownloaded product corresponds to selection criteria")
    return False
        
        
def theia_download(tile, start_date, end_date, write_dir, lim_perc_cloud, login_theia, password_theia, level):
    """
    Downloads Sentinel-2 acquisitions of the specified tile from THEIA from start_date to end_date under a cloudiness threshold

    Parameters
    ----------
    tile : str
        Name of the Sentinel-2 tile (format : "T31UFQ").
    start_date : str
        Acquisitions before this date are ignored (format : "YYYY-MM-DD") 
    end_date : str
        Acquisitions after this date are ignored (format : "YYYY-MM-DD") 
    write_dir : str
        Directory where THEIA data is downloaded
    lim_perc_cloud : int
        Maximum cloud cover (%)
    login_theia : str
        Login of your theia account
    password_theia : str
        Password of your theia account
    level : str
        Product level for reflectance products, can be 'LEVEL1C', 'LEVEL2A' or 'LEVEL3A'

    """

    dict_query = {'location': tile,
                  "startDate" : start_date,
                  'completionDate': end_date, 
                  'maxRecords': 1500, 
                  'processingLevel': level}
    
    config = {'serveur': 'https://theia.cnes.fr/atdistrib', 
              'resto': 'resto2', 
              'token_type': 'text', 
              'login_theia': login_theia, 
              'password_theia': password_theia}

    print("Get theia single sign on token")
    get_token = 'curl -k -s -X POST %s --data-urlencode "ident=%s" --data-urlencode "pass=%s" %s/services/authenticate/>token.json' % (
        "", config["login_theia"], config["password_theia"], config["serveur"])
        
    os.system(get_token)
    print("Done")
    with open('token.json') as data_file:
        token = data_file.readline()
    
    query = "%s/%s/api/collections/%s/search.json?" % (
        config["serveur"], config["resto"], "SENTINEL2")+urlencode(dict_query)
    print(query)
    search_catalog = 'curl -k %s -o search.json "%s"' % ("", query)
    print(search_catalog)
    os.system(search_catalog)
    time.sleep(5)
    
    # ====================
    # Download
    # ====================
    
    with open('search.json') as data_file:
        data = json.load(data_file)
    
    try:
        for i in range(len(data["features"])):
            prod = data["features"][i]["properties"]["productIdentifier"]
            feature_id = data["features"][i]["id"]
            cloudtemp = data["features"][i]["properties"]["cloudCover"]
            if cloudtemp != None:
                cloudCover = int(cloudtemp)
            else:
                cloudCover = 0
            acqDate = data["features"][i]["properties"]["startDate"]
            prodDate = data["features"][i]["properties"]["productionDate"]
            pubDate = data["features"][i]["properties"]["published"]
            print ('------------------------------------------------------')
            print(prod, feature_id)
            print("cloudCover:", cloudCover)
            print("acq date", acqDate[0:14], "prod date", prodDate[0:14], "pub date", pubDate[0:14])
    
            if write_dir == None:
                write_dir = os.getcwd()
            file_exists = os.path.exists("%s/%s.zip" % (write_dir, prod))
            rac_file = '_'.join(prod.split('_')[0: -1])
            print((">>>>>>>", rac_file))
            fic_unzip = glob.glob("%s/%s*" % (write_dir, rac_file))
            if len(fic_unzip) > 0:
                unzip_exists = True
            else:
                unzip_exists = False
            tmpfile = "%s/%s.tmp" % (write_dir, prod)
            get_product = 'curl %s -o "%s" -k -H "Authorization: Bearer %s" %s/%s/collections/%s/%s/download/?issuerId=theia' % (
                "", tmpfile, token, config["serveur"], config["resto"], "SENTINEL2", feature_id)
            print(get_product)
            if not(file_exists) and not(unzip_exists):
                # download only if cloudCover below maxcloud
                if cloudCover <= lim_perc_cloud:
                    os.system(get_product)
    
                    # check if binary product
    
                    with open(tmpfile) as f_tmp:
                        try:
                            tmp_data = json.load(f_tmp)
                            print("Result is a text file")
                            print(tmp_data)
                        except ValueError:
                            pass
    
                    os.rename("%s" % tmpfile, "%s/%s.zip" % (write_dir, prod))
                    print("product saved as : %s/%s.zip" % (write_dir, prod))
                else:
                    print("cloud cover too high : %s" % (cloudCover))
            elif file_exists:
                print("%s already exists" % prod)
    
    except KeyError:
        print(">>>no product corresponds to selection criteria")


def s2_unzip(s2zipfile, out_dir, bands, correction_type):
    """
    Unzips Flat REflectance data from zipped theia data, then empties the zip file

    Parameters
    ----------
    s2zipfile : str
        Path of the zip file containing a Sentinel-2 acquisition downloaded from theia.
    out_dir : str
        Directory where data is extracted
    bands : list of str
        List of bands to extracted (B2, B3, B4, B5, B6, B7, B8, B8A, B11, B12, as well as CLMR2, CLMR2, EDGR1, EDGR2, SATR1, SATR2 for LEVEL2A data, and DTS1, DTS2, FLG1, FLG2, WGT1, WGT2 for LEVEL3A)
    correction_type : str
        Chosen correction type (SRE or FRE for LEVEL2A data, FRC for LEVEL3A)

    Returns
    -------
    None.

    """
    
    corrBand = dict(zip(['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12'] + ['CLMR1', 'CLMR2', 'EDGR1', 'EDGR2', 'SATR1', 'SATR2',"DTS1","DTS2","FLG1","FLG2","WGT1","WGT2"],
         ["_"+correction_type+"_"+band for band in ['B2.tif', 'B3.tif', 'B4.tif', 'B5.tif', 'B6.tif', 'B7.tif', 'B8.tif', 'B8A.tif', 'B11.tif', 'B12.tif']] + ['_CLM_R1.tif', '_CLM_R2.tif', '_EDG_R1.tif', '_EDG_R2.tif', '_SAT_R1.tif', '_SAT_R2.tif',"_FLG_R1.tif","_FLG_R2.tif","_WGT_R1.tif","_WGT_R2.tif"]))
    

    
    # corrBand = {'B2':'_FRE_B2.tif', 'B3':'_FRE_B3.tif', 'B4':'_FRE_B4.tif', 'B5':'_FRE_B5.tif',
    #             'B6':'_FRE_B6.tif', 'B7':'_FRE_B7.tif', 'B8':'_FRE_B8.tif',
    #             'B8A':'_FRE_B8A.tif', 'B11':'_FRE_B11.tif', 'B12':'_FRE_B12.tif',
    #             'CLMR1': '_CLM_R1.tif', 'CLMR2':'_CLM_R2.tif',
    #             'EDGR1': '_EDG_R1.tif', 'EDGR2':'_EDG_R2.tif',
    #             'SATR1': '_SAT_R1.tif', 'SATR2':'_SAT_R2.tif'}

    try:
        os.mkdir(out_dir) #Create directory
    except FileExistsError:
        #directory already exists
        pass
    try:
        with ZipFile(s2zipfile, 'r') as zipObj:
            listOfFileNames = zipObj.namelist()
            for fileName in listOfFileNames:
                    for i in bands:
                        if fileName.endswith(corrBand[i]): #Si le nom de fichier finit par ce qui correspond à la bande
                            if not os.path.exists(os.path.join(out_dir,fileName)):
                                print('Extraction of {}'.format(fileName))
                                zipObj.extract(fileName, out_dir)
                            else:
                                print('File already extracted: {}'.format(os.path.basename(fileName)))
    except BadZipfile:
        print("Bad zip file, removing file")
        os.remove(s2zipfile)

def unzip_theia(bands, zip_dir,out_dir, empty_zip, correction_type):
    """
    Unzips zipped theia data, then empties the zip file

    Parameters
    ----------
    bands : list of str
        List of bands to extracted (B2, B3, B4, B5, B6, B7, B8, B8A, B11, B12, as well as CLMR2, CLMR2, EDGR1, EDGR2, SATR1, SATR2 for LEVEL2A data, and DTS1, DTS2, FLG1, FLG2, WGT1, WGT2 for LEVEL3A)
    zip_dir : str
        Directory where zip files containing theia data are stored
    out_dir : str
        Directory where data is extracted
    empty_zip : bool
        If True, the zip file is emptied as a way to save space
    correction_type : str
        Chosen correction type (SRE or FRE for LEVEL2A data, FRC for LEVEL3A)


    Returns
    -------
    None.
    

    """
    zip_dir = Path(zip_dir)
    out_dir = Path(out_dir)
    zipList=zip_dir.glob("*.zip")
    if not(out_dir.exists()):
        os.mkdir(out_dir)
    for zipfile in zipList:
        s2_unzip(zipfile,out_dir,bands, correction_type)
        if zipfile.exists() and (len(ZipFile(zipfile).namelist()) != 0) and empty_zip:
            print("Removal of " + str(zipfile))
            os.remove(zipfile)
            zipObj = ZipFile(zipfile, 'w')
            zipObj.close()

def delete_empty_zip(zipped_dir, unzipped_dir):
    """
    Deletes empty zip files if the unzipped directory is missing

    Parameters
    ----------
    zipped_dir : str
        Directory where zip files containing theia data are stored.
    unzipped_dir : str
        Directory where unzipped data containing theia data are stored

    Returns
    -------
    None.

    """

    tile = TileInfo(unzipped_dir)
    for i in range(2):
        tile.getdict_datepaths("zipped",zipped_dir)
        tile.getdict_datepaths("unzipped",unzipped_dir)
        for date in tile.paths["zipped"]:
            if date not in tile.paths["unzipped"]:
                try:
                    if (len(ZipFile(tile.paths["zipped"][date]).namelist()) == 0):
                        print("Empty zip with no unzipped directory detected : removal of " + str(tile.paths["zipped"][date]))
                        os.remove(tile.paths["zipped"][date])
                except BadZipfile:
                    print("Bad zip file, removing file")
                    os.remove(tile.paths["zipped"][date])

def merge_same_date(bands,out_dir):
    """
    Merges data from two theia directories if they share the same date of acquisition

    Parameters
    ----------
    bands : list of str
        List of bands to extracted (B2, B3, B4, B5, B6, B7, B8, B8A, B11, B12, CLMR2).
    out_dir : str
        Directory where unzipped data containing theia data are stored.

    Returns
    -------
    None.

    """

    
    SenPathGen = out_dir.glob("SEN*")
    # SenPathList=glob(out_dir+"/SEN*")
    SenDateList = [] #Création dictionnaire avec date : chemin du fichier
    SenPathList = []
    for SenPath in SenPathGen:
        # SenDate = SenPath.split('_')[1].split('-')[0]
        SenDate = retrieve_date_from_string(str(SenPath))
        SenDateList+=[SenDate]
        SenPathList += [SenPath]
    # tile = TileInfo(out_dir)
    # tile.getdict_datepaths("SENTINEL",tile.data_directory)

    
    for date in np.unique(np.array(SenDateList)):
        if np.sum(np.array(SenDateList)==date)>1:
            print("Doublon détecté à la date : " + date)
            Doublons=np.array(SenPathList)[np.array(SenDateList)==date]
            
            #MOSAIQUE BANDES
            
            for band in bands:
                if band != "CLMR2":
                    print("Fusion bande : " + band)
                    for doublon in Doublons:
                        # PathBande=doublon+"/"+os.path.basename(doublon)+"_FRE_"+band+".tif"
                        PathBande=doublon / (doublon.name +"_FRE_"+band+".tif")
                        with rasterio.open(PathBande) as RasterBand:
                            if doublon==Doublons[0]:
                                MergedBand=RasterBand.read(1)
                                ProfileSave=RasterBand.profile
                            else:
                                AddedBand=RasterBand.read(1)
                                MergedBand[AddedBand!=-10000]=AddedBand[AddedBand!=-10000]
                    
                    for doublon in Doublons:
                        if doublon==Doublons[0]:
                            # with rasterio.open(doublon+"/"+os.path.basename(doublon)+"_FRE_"+band+".tif", 'w', **ProfileSave) as dst:
                            with rasterio.open(doublon /(doublon.name +"_FRE_"+band+".tif"), 'w', **ProfileSave) as dst:
                                    dst.write(MergedBand,indexes=1)
            
            print("Fusion masque")
            #MOSAIQUE MASQUE THEIA
            for doublon in Doublons:
                    PathBande=doublon /  "MASKS" / (doublon.name +"_CLM_R2.tif")
                    with rasterio.open(PathBande) as RasterBand:
                        if doublon==Doublons[0]:
                            MergedBand=RasterBand.read(1)
                            ProfileSave=RasterBand.profile
                        else:
                            AddedBand=RasterBand.read(1)
                            MergedBand[AddedBand!=0]=AddedBand[AddedBand!=0]
                
            for doublon in Doublons:
                if doublon==Doublons[0]:
                    with rasterio.open(doublon /  "MASKS" / (doublon.name +"_CLM_R2.tif"), 'w', **ProfileSave) as dst:
                            dst.write(MergedBand,indexes=1)
            else:
                shutil.rmtree(str(doublon)) #Supprime les inutiles
                print("Suppresion doublons")