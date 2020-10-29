# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 17:26:30 2020

@author: raphael.dutrieux
"""
import os
import pickle

def writeParameters(Version, Tuiles, SeuilMin, CoeffAnomalie, PercNuageLim, ApplyMaskTheia, RemoveOutliers, InterpolationOrder, ExportMasks, CorrectCRSWIR, DataSource,ExportAsShapefile,DateFinApprentissage):
    """
    Ecrit les paramètres dans un fichier texte. Permet de garder une trace des paramètres utilisés dans cette version.

    Parameters
    ----------
    Version: str
        Nom de la version (ex : V12)
    Tuiles: list
        Liste des tuiles utilisées
    SeuilMin : float
        Seuil minimum pour la détection d'anomalies
    CoeffAnomalie : float
        Coefficient appliqué au SeuilMin pour la détection d'anomalies
    PercNuageLim : float
        Pourcentage maximum d'ennuagement pour filter les dates SENTINEL-2
    ApplyMaskTheia : bool
        Si True, applique le masque de THEIA
    RemoveOutliers : bool
        Si True, retire les outliers des dates utilisées pour la modélisation du CRSWIR
    InterpolationOrder : int
        Ordre d’interpolation pour passage des pixels 20m à 10m (0 = proche voisin, 1 = linéaire, 2 = bilinéaire, 3 = cubique)
    NbBlocs : int
        Détermine le nombre de blocs (ex : si NbBlocs = 30, il y aura 30*30 blocs)
    ExportMasks : bool
        Si True, exporte les masques d'ombre et de nuages calculés
    CorrectCRSWIR : bool
        Si activé, execute la correction du CRSWIR à partir du CRSWIR médian de la tuile entière
    ExportAsShapefile : bool
        Si True, exporte les résultats en shapefile, sinon en raster

    Returns
    -------
    bool
        True if good
    """

    file = open(os.getcwd()+"/Out/Results/"+"V"+Version+"/Parametres.txt", "w") 
    file.write("Source des données SENTINEL : " + DataSource + "\n") 
    file.write("Seuil anomalie : " + str(SeuilMin)+"\n") 
    file.write("Coefficient anomalie : " + str(CoeffAnomalie)+"\n") 
    file.write("Ennuagement maximum : " + str(PercNuageLim)+"\n") 
    file.write("Masque Theia : " + str(ApplyMaskTheia)+"\n")
    file.write("Outliers retirés : " + str(RemoveOutliers)+"\n") 
    file.write("Interpolation : " + str(InterpolationOrder)+"\n") 
    file.write("Exportation des masques ombres et nuages : " + str(ExportMasks)+"\n")
    file.write("Correction du CRSWIR : " + str(CorrectCRSWIR)+"\n")
    file.write("Ecriture en shapefile : " + str(ExportAsShapefile)+"\n")
    file.write("\n")
    file.write("Tuiles : ")
    for tuile in Tuiles:
        file.write(tuile+" ")
    file.close()
    
    with open(os.getcwd()+"/Out/Results/"+"V"+Version+"/SaveVariables", 'wb') as f:
        pickle.dump([Tuiles,SeuilMin,CoeffAnomalie,PercNuageLim,ApplyMaskTheia,RemoveOutliers,InterpolationOrder,ExportMasks,CorrectCRSWIR, DataSource,ExportAsShapefile,DateFinApprentissage], f)
  
    return True

def writeExecutionTime(Version, tuile, TimeTotal, TimeInitialisation, TimeComputeDate,TimeWriteInputData,TimeReadInput,TimeModelCRSWIR,TimeWriteDataUpdate):
    
    """
    Ecrit le temps d'execution de chaque étape dans un fichier texte.

    """
    
    file = open(os.getcwd()+"/Out/Results/"+"V"+Version+"/Parametres.txt", "a") 
    file.write("\n"+tuile+" : "+str(round(TimeTotal))+" secondes")
    file.write("\n Temps intialisation : "+str(round(TimeInitialisation))+" secondes")
    file.write("\n Calcul masques et CRSWIR : "+str(round(TimeComputeDate))+" secondes")
    file.write("\n Ecriture masque et CRSWIR : "+str(round(TimeWriteInputData))+" secondes")
    file.write("\n Lecture masque et CRSWIR : "+str(round(TimeReadInput))+" secondes")
    file.write("\n Modélisation CRSWIR : "+str(round(TimeModelCRSWIR))+" secondes")
    file.write("\n Ecriture données pour mise à jour : "+str(round(TimeWriteDataUpdate))+" secondes")
    file.write("\n")
    file.close()
    
    return True

def writeExecutionTimeUpdate(Version, tuile, TimeTotal, TimeInitialisation, TimeComputeDate,TimeWriteInputData, TimeDetectAnomalies, TimeDetectDeperissement,TimeWriteDataUpdate, TimeWriteResults, NbNewDates):
    
    """
    Ecrit le temps d'execution de chaque étape dans un fichier texte.

    """
    
    file = open(os.getcwd()+"/Out/Results/"+"V"+Version+"/Parametres.txt", "a") 
    file.write("\n UPDATE : " + str(NbNewDates) + " Nouvelles dates")
    file.write("\n"+tuile+" : "+str(round(TimeTotal))+" secondes")
    file.write("\n Temps intialisation : "+str(round(TimeInitialisation))+" secondes")
    file.write("\n Calcul masques et CRSWIR : "+str(round(TimeComputeDate))+" secondes")
    file.write("\n ecriture masques et CRSWIR : "+str(round(TimeWriteInputData))+" secondes")
    file.write("\n Détection des anomalies : "+str(round(TimeDetectAnomalies))+" secondes")
    file.write("\n Détection du déperissement : "+str(round(TimeDetectDeperissement))+" secondes")
    file.write("\n Ecriture données pour mise à jour : "+str(round(TimeWriteDataUpdate))+" secondes")
    file.write("\n Ecriture Résultats : "+str(round(TimeWriteResults))+" secondes")
    file.write("\n")
    file.close()
    
    return True

