#!/usr/bin/env python3
"""
Script pour l'étape 1: Compute masked vegetation index
Ce script calcule les indices de végétation masqués pour une série temporelle Sentinel-2
"""

from fordead.steps.step1_compute_masked_vegetationindex import compute_masked_vegetationindex

def main():
    # Configuration des chemins
    input_directory = "fordead_data-main/fordead_data-main/sentinel_data/dieback_detection_tutorial/study_area"
    data_directory = "tuto_output"
    
    print("=== Étape 1: Compute masked vegetation index ===")
    print(f"Répertoire d'entrée: {input_directory}")
    print(f"Répertoire de sortie: {data_directory}")
    print()
    
    # Paramètres de configuration
    params = {
        'input_directory': input_directory,
        'data_directory': data_directory,
        'lim_perc_cloud': 0.4,  # Maximum 40% de couverture nuageuse
        'interpolation_order': 0,  # Interpolation par plus proche voisin
        'sentinel_source': "THEIA",  # Source des données Sentinel-2
        'soil_detection': False,  # Désactiver la détection de sol
        'formula_mask': "B2 > 600 | (B3 == 0) | (B4 == 0)",  # Formule de masquage
        'vi': "CRSWIR",  # Indice de végétation CRSWIR
        'apply_source_mask': True  # Appliquer le masque de source
    }
    
    print("Paramètres utilisés:")
    for key, value in params.items():
        print(f"  {key}: {value}")
    print()
    
    try:
        print("Début du calcul des indices de végétation masqués...")
        compute_masked_vegetationindex(**params)
        print("✅ Calcul terminé avec succès!")
        print()
        print("Résultats générés dans:")
        print(f"  - {data_directory}/VegetationIndex/ (indices de végétation)")
        print(f"  - {data_directory}/Mask/ (masques binaires)")
        
    except Exception as e:
        print(f"❌ Erreur lors du calcul: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Étape 1 terminée avec succès!")
    else:
        print("\n💥 Échec de l'étape 1")
