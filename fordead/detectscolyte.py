# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 10:30:53 2020

@author: admin


L'arborescence nécessaire pour faire tourner l'algorithme est la suivante :
    - Data
        -SENTINEL
            -Tuile1
                -Date1
                -Date2
                ...
            -Tuile2
            ...
        -Vecteurs
            -Departements
                departements-20140306-100m.shp
            -BDFORET
                -BD_Foret_V2_Dep001
                -BD_Foret_V2_Dep002
                ...
            TilesSentinel.shp

Les résultats sont écrits dans :
    -Out
        -Results


"""

# %% =============================================================================
#   LIBRAIRIES
# =============================================================================


import os, time, sys
# import numpy as np
import argparse

# %% ===========================================================================
#   IMPORT LIBRAIRIES PERSO
# =============================================================================
# from .Lib_TrainFordead import readInputDataDateByDate
# from Lib_WritingLog import writeParameters, writeExecutionTime
# from Lib_ImportValidSentinelData import getSentinelPaths, getValidDates, readInputDataDateByDate, ComputeDate
# from Lib_ComputeMasks import getRasterizedBDForet
# from Lib_DetectionDeperissement import ModelForAnomalies, getCRSWIRCorrection
# from Lib_WritingResults import getVersion, CreateDirectories, writeInputDataDateByDate
# from Lib_SaveForUpdate import SaveData


# %% =============================================================================
#   DEFINITION DES PARAMETRES
# =============================================================================
# Processeur="VM"
# Processeur = "Maison"

def parse_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--Tuiles', nargs='+',
                        default=["T31UFQ", "T31UGQ", "T31UGP", "T31TGL", "T31TGM", "T31UFR", "T31TDL", "T31UFP",
                                 "T31TFL", "T31TDK", "T32ULU", "T31UEP"],
                        help="Liste des tuiles à analyser ex : -t T31UGP T31UGQ")
    parser.add_argument("-s", "--SeuilMin", dest="SeuilMin", type=float, default=0.04,
                        help="Seuil minimum pour détection d'anomalies")
    parser.add_argument("-a", "--CoeffAnomalie", dest="CoeffAnomalie", type=float, default=4,
                        help="Coefficient multiplicateur du seuil de détection d'anomalies")
    parser.add_argument("-n", "--PercNuageLim", dest="PercNuageLim", type=float, default=0.3,
                        help="Pourcentage d'ennuagement maximum à l'échelle de la tuile pour utilisation de la date SENTINEL")
    parser.add_argument("-e", "--ExportMasks", dest="ExportMasks", action="store_true", default=False,
                        help="Si activé, exporte les masques nuages et ombres")
    parser.add_argument("-m", "--ApplyMaskTheia", dest="ApplyMaskTheia", action="store_true", default=False,
                        help="Si activé, applique le masque theia")
    parser.add_argument("-i", "--InterpolationOrder", dest="InterpolationOrder", type=int, default=0,
                        help="Ordre d'interpolation : 0 = proche voisin, 1 = linéaire, 2 = bilinéaire, 3 = cubique")
    parser.add_argument("-k", "--RemoveOutliers", dest="RemoveOutliers", action="store_false", default=True,
                        help="Si activé, garde les outliers dans les deux premières années")
    parser.add_argument("-c", "--CorrectCRSWIR", dest="CorrectCRSWIR", action="store_true", default=False,
                        help="Si activé, execute la correction du CRSWIR à partir")
    parser.add_argument("-d", "--DataSource", dest="DataSource", type=str, default="THEIA",
                        help="Source des données parmi THEIA et Scihub et PEPS")
    parser.add_argument("-g", "--DateFinApprentissage", dest="DateFinApprentissage", type=str, default="2018-06-01",
                        help="Uniquement les dates antérieures à la date indiquée seront utilisées")
    parser.add_argument("-x", "--ExportAsShapefile", dest="ExportAsShapefile", action="store_true", default=False,
                        help="Si activé, exporte les résultats sous la forme de shapefiles plutôt que de rasters")

    option, args = parser.parse_args()

    return options, args


    # os.chdir('/mnt/fordead')
    # sys.path.append(os.path.abspath("~/Scripts/DetectionScolytes"))

# else:
#     # ["T31UFQ","T31UGP","T31UGQ"]
#     Tuiles = ["ZoneFaucheUnique"]
#     BlocWithObs = False  # If True, compute only blocks with observations
#     SeuilMin = 0.04
#     CoeffAnomalie = 4
#     PercNuageLim = 0.3
#     ExportMasks = True
#     ApplyMaskTheia = True
#     InterpolationOrder = 0
#     RemoveOutliers = True
#     CorrectCRSWIR = False
#     DataSource = "THEIA"
#     DateFinApprentissage = "2018-06-01"
#     ExportAsShapefile = False
#     #    DataSource="Scihub"
#     os.chdir('F:/Deperissement')
#     sys.path.append(os.path.abspath(os.getcwd() + "/Code/Python/fordead/DetectionScolytes"))


# %% =============================================================================
#   MAIN CODE
# ===============================================================================

def detect_scolyte(
    Tuiles = ["ZoneFaucheUnique"],
    BlocWithObs = False,  # If True, compute only blocks with observations
    SeuilMin = 0.04,
    CoeffAnomalie = 4,
    PercNuageLim = 0.3,
    ExportMasks = True,
    ApplyMaskTheia = True,
    InterpolationOrder = 0,
    RemoveOutliers = True,
    CorrectCRSWIR = False,
    DataSource = "THEIA",
    DateFinApprentissage = "2018-06-01",
    ExportAsShapefile = False):

    Version = str(getVersion())
    CreateDirectories(Version, ExportMasks, Tuiles)
    writeParameters(Version, Tuiles, SeuilMin, CoeffAnomalie, PercNuageLim, ApplyMaskTheia, RemoveOutliers,
                    InterpolationOrder, ExportMasks, CorrectCRSWIR, DataSource, ExportAsShapefile, DateFinApprentissage)

    for tuile in Tuiles:
        start_time_debut = time.time()

        TimeComputeDate = 0;
        TimeWriteInputData = 0
        # DETERMINE DATES VALIDES
        DictSentinelPaths = getSentinelPaths(tuile, DateFinApprentissage,
                                             DataSource)  # Récupération de l'ensemble des dates avant la date de fin d'apprentissage, associées aux chemins de chaque bande SENTINEL-2

        Dates = getValidDates(DictSentinelPaths, tuile, PercNuageLim, DataSource)

        # RASTERIZE MASQUE FORET
        MaskForet, MetaProfile, CRS_Tuile = getRasterizedBDForet(DictSentinelPaths[Dates[0]]["B2"], tuile, DataSource)

        # COMPUTE CRSWIR MEDIAN
        listDiffCRSWIRmedian = getCRSWIRCorrection(DictSentinelPaths,
                                                   getValidDates(getSentinelPaths(tuile, "3000-01-01", DataSource), tuile,
                                                                 PercNuageLim, DataSource), tuile, MaskForet)[
                               :Dates.shape[0]] if CorrectCRSWIR else []

        CompteurSolNu = np.zeros((MaskForet.shape[0], MaskForet.shape[1]), dtype=np.uint8)  # np.int8 possible ?
        DateFirstSolNu = np.zeros((MaskForet.shape[0], MaskForet.shape[1]), dtype=np.uint16)  # np.int8 possible ?
        BoolSolNu = np.zeros((MaskForet.shape[0], MaskForet.shape[1]), dtype='bool')

        TimeInitialisation = time.time() - start_time_debut
        for DateIndex, date in enumerate(Dates):
            print(date)
            start_time = time.time()
            VegetationIndex, Mask, BoolSolNu, CompteurSolNu, DateFirstSolNu = ComputeDate(date, DateIndex,
                                                                                          DictSentinelPaths,
                                                                                          InterpolationOrder,
                                                                                          ApplyMaskTheia, BoolSolNu,
                                                                                          CompteurSolNu, DateFirstSolNu,
                                                                                          listDiffCRSWIRmedian,
                                                                                          CorrectCRSWIR)
            TimeComputeDate += time.time() - start_time;
            start_time = time.time()
            writeInputDataDateByDate(VegetationIndex, Mask, MetaProfile, date, Version, tuile)
            TimeWriteInputData += time.time() - start_time
            # writeInputDataStack(VegetationIndex,Mask,MetaProfile,DateIndex,Version,tuile,Dates)

        print("Calcul des masques et du CRSWIR : %s secondes ---" % (time.time() - start_time_debut))

        start_time = time.time()
        StackVegetationIndex, StackMask = readInputDataDateByDate(Dates, Version, tuile)
        TimeReadInput = time.time() - start_time;
        start_time = time.time()
        # StackVegetationIndex, StackMask = readInputDataStack(Version,tuile)

        StackVegetationIndex = np.ma.masked_array(StackVegetationIndex, mask=StackMask)  # Application du masque
        StackEtat, rasterP, rasterSigma = ModelForAnomalies(np.where(np.logical_and(
            ~np.logical_and(DateFirstSolNu <= np.where(Dates == Dates[Dates >= "2018-01-01"][2])[0][0], BoolSolNu),
            MaskForet)), Dates, StackVegetationIndex, RemoveOutliers, SeuilMin, CoeffAnomalie)
        TimeModelCRSWIR = time.time() - start_time;
        start_time = time.time()
        print("Modélisation du CRSWIR : %s secondes ---" % (time.time() - start_time_debut))

        SaveData(BoolSolNu, DateFirstSolNu, CompteurSolNu, rasterP, rasterSigma, StackEtat, Dates, MetaProfile, Version,
                 tuile)
        TimeWriteDataUpdate = time.time() - start_time
        print("Ecriture des résultats : %s secondes ---" % (time.time() - start_time_debut))
        TimeTotal = time.time() - start_time_debut
        writeExecutionTime(Version, tuile, TimeTotal, TimeInitialisation, TimeComputeDate, TimeWriteInputData,
                           TimeReadInput, TimeModelCRSWIR, TimeWriteDataUpdate)
