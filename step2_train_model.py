#!/usr/bin/env python3
"""
Script pour l'étape 2: Train model
Ce script ajuste un modèle harmonique pour chaque pixel afin de définir la saisonnalité normale
de la végétation basée sur une période d'entraînement.
"""

from fordead.steps.step2_train_model import train_model

def main():
    # Configuration des chemins
    data_directory = "tuto_output"
    
    print("=== Étape 2: Train model ===")
    print(f"Répertoire de données: {data_directory}")
    print()
    
    # Paramètres de configuration
    params = {
        'data_directory': data_directory,
        'nb_min_date': 10,  # Minimum 10 acquisitions valides
        'min_last_date_training': "2018-01-01",  # Date de fin minimale d'entraînement
        'max_last_date_training': "2018-06-01"   # Date de fin maximale d'entraînement
    }
    
    print("Paramètres utilisés:")
    for key, value in params.items():
        print(f"  {key}: {value}")
    print()
    
    print("Explication du modèle harmonique:")
    print("  Le modèle ajusté pour chaque pixel est de la forme:")
    print("  a1 + b1*sin(2πt/T) + b2*cos(2πt/T) + b3*sin(4πt/T) + b4*cos(4πt/T)")
    print("  où T est la période (1 an) et t est le temps")
    print()
    
    print("Période d'entraînement:")
    print("  - Début: Première acquisition disponible")
    print("  - Fin: Dernière acquisition avant 2018-01-01")
    print("  - Minimum requis: 10 acquisitions valides par pixel")
    print("  - Si < 10 acquisitions le 2018-01-01, utilisation jusqu'au 2018-06-01")
    print("  - Si < 10 acquisitions le 2018-06-01, le pixel est exclu")
    print()
    
    try:
        print("Début de l'entraînement du modèle harmonique...")
        train_model(**params)
        print("✅ Entraînement terminé avec succès!")
        print()
        print("Résultats générés dans:")
        print(f"  - {data_directory}/DataModel/ (modèle harmonique)")
        print(f"    - first_detection_date_index.tif (index de la première acquisition)")
        print(f"    - coeff_model.tif (5 coefficients du modèle)")
        print(f"  - {data_directory}/TimelessMasks/ (masques temporels)")
        print(f"    - sufficient_coverage_mask.tif (pixels avec couverture suffisante)")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'entraînement: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Étape 2 terminée avec succès!")
    else:
        print("\n💥 Échec de l'étape 2")
