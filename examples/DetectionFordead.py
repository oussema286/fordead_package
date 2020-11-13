# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 09:25:23 2020

@author: Raphaël Dutrieux
"""



# import os
import argparse
import pickle
# from fordead.DetectionDeperissement import DetectAnomalies,PredictVegetationIndex
# from fordead.ImportData import getDates, ImportMaskedVI, ImportMaskForet, ImportModel, ImportDataScolytes, InitializeDataScolytes


def parse_command_line():
    parser = argparse.ArgumentParser()
    # parser.add_argument("-d", "--data_directory", dest = "data_directory",type = str,default = "C:/Users/admin/Documents/Deperissement/fordead_data/tests/OutputFordead/ZoneTest", help = "Dossier avec les données")
    parser.add_argument("-s", "--threshold_min", dest = "threshold_min",type = float,default = 0.16, help = "Seuil minimum pour détection d'anomalies")
    parser.add_argument("-x", "--ExportAsShapefile", dest = "ExportAsShapefile", action="store_true",default = False, help = "Si activé, exporte les résultats sous la forme de shapefiles plutôt que de rasters")
    parser.add_argument("-o", "--Overwrite", dest = "Overwrite", action="store_true",default = False, help = "Si vrai, recommence la détection du début. Sinon, reprends de la dernière date analysée")
    dictArgs={}
    for key, value in parser.parse_args()._get_kwargs():
    	dictArgs[key]=value
    return dictArgs


def DetectionScolytes(
    # data_directory = "C:/Users/admin/Documents/Deperissement/fordead_data/tests/OutputFordead/ZoneTest",
    SeuilMin=0.16,
    ExportAsShapefile = False,
    Overwrite=False
    ):
    
    with open(data_directory / "dict_paths", 'rb') as f:
        dict_paths = pickle.load(f)
    
    
    
    # if Overwrite: OverwriteUpdate(tuile,DataDirectory)
    
    # Dates=getDates(os.path.join(DataDirectory,"VegetationIndex",tuile))
    # OldDates=getDates(os.path.join(DataDirectory,"DataAnomalies",tuile))
    
    # NbNewDates = Dates[Dates>"2018-01-01"].shape[0] - OldDates.shape[0]
    # if NbNewDates == 0:
    #     print("Pas de nouvelles dates SENTINEL-2")
    #     continue
    # else:
    #     print(str(NbNewDates)+ " nouvelles dates")
    
    # #RASTERIZE MASQUE FORET
    # MaskForet = ImportMaskForet(os.path.join(DataDirectory,"MaskForet",tuile+"_MaskForet.tif"))

    # #INITIALISATION
    # StackP,rasterSigma = ImportModel(tuile,DataDirectory)
    # rasterSigma=rasterSigma.where(~((rasterSigma < SeuilMin) & (rasterSigma != 0)),SeuilMin)
            
    
    # if os.path.exists(os.path.join(DataDirectory,"DataUpdate",tuile,"EtatChange.tif")):
    #     EtatChange,DateFirstScolyte,CompteurScolyte = ImportDataScolytes(tuile,DataDirectory)
    # else:
    #     EtatChange,DateFirstScolyte,CompteurScolyte = InitializeDataScolytes(tuile,DataDirectory,MaskForet.shape)
        
    # print("Détection du déperissement")
    
    # for DateIndex,date in enumerate(Dates):
    #     if date < "2018-01-01" or os.path.exists(os.path.join(DataDirectory,"DataAnomalies",tuile,"Anomalies_"+date+".tif")): #Si anomalies pas encore écrites, ou avant la date de début de détection
    #         continue
    #     else:
    #         VegetationIndex, Mask = ImportMaskedVI(DataDirectory,tuile,date)
        
    #     Anomalies = DetectAnomalies(VegetationIndex, PredictVegetationIndex(StackP,date),Mask, rasterSigma, CoeffAnomalie)



if __name__ == '__main__':
    dictArgs=parse_command_line()
    print(dictArgs)
    DetectionScolytes(**dictArgs)