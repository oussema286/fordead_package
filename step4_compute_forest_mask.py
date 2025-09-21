#!/usr/bin/env python3
"""
Script pour l'étape 4: Compute forest mask
Ce script crée un masque forestier pour définir les zones d'intérêt
en rasterisant un fichier vectoriel.
"""

from fordead.steps.step4_compute_forest_mask import compute_forest_mask

def main():
    # Configuration des chemins
    data_directory = "tuto_output"
    vector_path = "fordead_data-main/fordead_data-main/vector/area_interest.shp"
    
    print("=== Étape 4: Compute forest mask ===")
    print(f"Répertoire de données: {data_directory}")
    print(f"Fichier vectoriel: {vector_path}")
    print()
    
    # Paramètres de configuration
    params = {
        'data_directory': data_directory,
        'forest_mask_source': "vector",  # Source du masque forestier
        'vector_path': vector_path  # Chemin vers le fichier shapefile
    }
    
    print("Paramètres utilisés:")
    for key, value in params.items():
        print(f"  {key}: {value}")
    print()
    
    print("Explication du processus:")
    print("  1. Lecture du fichier vectoriel area_interest.shp")
    print("  2. Rasterisation du shapefile en raster binaire")
    print("  3. Ajustement aux dimensions des images Sentinel-2")
    print("  4. Création du masque forestier final")
    print()
    
    print("Objectif du masque forestier:")
    print("  - Définir les zones d'intérêt (forêts de conifères)")
    print("  - Filtrer les zones non pertinentes")
    print("  - Optimiser l'export des cartes de dépérissement")
    print("  - Se concentrer sur les forêts uniquement")
    print()
    
    print("Caractéristiques du masque:")
    print("  - Valeur 1: Zone d'intérêt (forêt)")
    print("  - Valeur 0: Zone non pertinente (autre)")
    print("  - Même dimensions que les images Sentinel-2")
    print("  - Même résolution spatiale (10m)")
    print("  - Même projection et origine")
    print()
    
    try:
        print("Début du calcul du masque forestier...")
        compute_forest_mask(**params)
        print("✅ Calcul du masque forestier terminé avec succès!")
        print()
        print("Résultats générés dans:")
        print(f"  - {data_directory}/ForestMask/")
        print(f"    - Forest_Mask.tif (masque forestier binaire)")
        print()
        print("Utilisation du masque:")
        print("  - Filtrage des zones d'intérêt")
        print("  - Export des cartes de dépérissement")
        print("  - Focus sur les forêts de conifères")
        print("  - Amélioration de la lisibilité des résultats")
        
    except Exception as e:
        print(f"❌ Erreur lors du calcul du masque: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Étape 4 terminée avec succès!")
    else:
        print("\n💥 Échec de l'étape 4")
