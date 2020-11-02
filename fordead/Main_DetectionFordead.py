# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 09:25:23 2020

@author: admin
"""



import os
import numpy as np
import argparse

from DetectionDeperissement import DetectAnomalies,PredictVegetationIndex
from ImportData import getDates, ImportMaskedVI, ImportMaskForet, ImportModel, ImportDataScolytes, InitializeDataScolytes


def parse_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--Tuiles', nargs='+',default=["ZoneTest"],help="Liste des tuiles à analyser ex : -t T31UGP T31UGQ")
    parser.add_argument("-s", "--SeuilMin", dest = "SeuilMin",type = float,default = 0.04, help = "Seuil minimum pour détection d'anomalies")
    parser.add_argument("-a", "--CoeffAnomalie", dest = "CoeffAnomalie",type = float,default = 4, help = "Coefficient multiplicateur du seuil de détection d'anomalies")
    parser.add_argument("-x", "--ExportAsShapefile", dest = "ExportAsShapefile", action="store_true",default = False, help = "Si activé, exporte les résultats sous la forme de shapefiles plutôt que de rasters")
    parser.add_argument("-d", "--DataDirectory", dest = "DataDirectory",type = str,default = "C:/Users/admin/Documents/Deperissement/fordead_data/tests/OutputFordead", help = "Dossier avec les données")
    parser.add_argument("-o", "--Overwrite", dest = "Overwrite", action="store_true",default = False, help = "Si vrai, recommence la détection du début. Sinon, reprends de la dernière date analysée")
    dictArgs={}
    for key, value in parser.parse_args()._get_kwargs():
    	dictArgs[key]=value
    return dictArgs


def DetectionScolytes(
    Tuiles= ["ZoneTest"],
    SeuilMin=0.04,
    CoeffAnomalie=4,
    ExportAsShapefile = False,
    DataDirectory = "G:/Deperissement/Out/PackageVersion",
    Overwrite=False
    ):

    for tuile in Tuiles:
        # start_time_debut=time.time()
        print("Tuile : " + tuile)
    
        if Overwrite: OverwriteUpdate(tuile,DataDirectory)
        
        Dates=getDates(os.path.join(DataDirectory,"VegetationIndex",tuile))
        OldDates=getDates(os.path.join(DataDirectory,"DataAnomalies",tuile))
        
        NbNewDates = Dates[Dates>"2018-01-01"].shape[0] - OldDates.shape[0]
        if NbNewDates == 0:
            print("Pas de nouvelles dates SENTINEL-2")
            continue
        else:
            print(str(NbNewDates)+ " nouvelles dates")
        
        #RASTERIZE MASQUE FORET
        MaskForet,MetaProfile,CRS_Tuile = ImportMaskForet(os.path.join(DataDirectory,"MaskForet",tuile+"_MaskForet.tif"))
      
        #INITIALISATION
        StackP,rasterSigma = ImportModel(tuile,DataDirectory)
        rasterSigma[rasterSigma<SeuilMin]=SeuilMin
        
        if os.path.exists(os.path.join(DataDirectory,"DataUpdate",tuile,"EtatChange.tif")):
            EtatChange,DateFirstScolyte,CompteurScolyte = ImportDataScolytes(tuile,DataDirectory)
        else:
            EtatChange,DateFirstScolyte,CompteurScolyte = InitializeDataScolytes(tuile,DataDirectory,MaskForet.shape)
            
        print("Détection du déperissement")
        
        for DateIndex,date in enumerate(Dates):
            if date < "2018-01-01" or os.path.exists(os.path.join(DataDirectory,"DataAnomalies",tuile,"Anomalies_"+date+".tif")):
                continue
            else:
                VegetationIndex, Mask = ImportMaskedVI(DataDirectory,tuile,date)
    
            Anomalies = DetectAnomalies(VegetationIndex, PredictVegetationIndex(StackP,date), rasterSigma, CoeffAnomalie)


if __name__ == '__main__':
    dictArgs=parse_command_line()
    print(dictArgs)
    DetectionScolytes(**dictArgs)