# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 16:21:15 2020

@author: Raphaël Dutrieux
"""



#Import ou création d'un dictionnaire :
    # Tuile :
        # Dates : 
            # VegetationIndex
                #Chemins des .tif
            # Mask
                 #Chemins des .tif
        # Masque Foret
            #Chemin du masque

#Import du masque forêt

# Import des index de végétations et des masques

# Pour chaque pixel dans le masque forêt :
    # Déterminer la date à partir de laquelle il y a suffisamment de données valides (si elle existe)
    # Retirer les outliers (optionnel)
    # Modéliser le CRSWIR
    # Mettre dans des rasters l'index de la dernière date utilisée, les coefficients, l'écart type
#Ecrire ces rasters 