#!/usr/bin/env python3
"""
Script pour l'étape 3: Dieback detection
Ce script détecte les anomalies en comparant les indices de végétation observés
aux valeurs prédites par le modèle harmonique.
"""

from fordead.steps.step3_dieback_detection import dieback_detection

def main():
    # Configuration des chemins
    data_directory = "tuto_output"
    
    print("=== Étape 3: Dieback detection ===")
    print(f"Répertoire de données: {data_directory}")
    print()
    
    # Paramètres de configuration
    params = {
        'data_directory': data_directory,
        'threshold_anomaly': 0.16,  # Seuil d'anomalie
        'stress_index_mode': "weighted_mean"  # Mode de calcul de l'index de stress
    }
    
    print("Paramètres utilisés:")
    for key, value in params.items():
        print(f"  {key}: {value}")
    print()
    
    print("Explication du processus de détection:")
    print("  1. Pour chaque acquisition après la période d'entraînement:")
    print("     - Calcul de la valeur prédite par le modèle harmonique")
    print("     - Comparaison avec la valeur observée")
    print("     - Calcul de l'anomalie: |valeur_observée - valeur_prédite|")
    print()
    print("  2. Détection d'anomalie:")
    print("     - Si anomalie > seuil (0.16) → pixel marqué comme anomalie")
    print("     - Si anomalie ≤ seuil → pixel normal")
    print()
    print("  3. Confirmation du dépérissement:")
    print("     - 3 anomalies successives → dépérissement confirmé")
    print("     - < 3 anomalies successives → pas de dépérissement")
    print()
    print("  4. Retour à la normale:")
    print("     - 3 acquisitions normales successives → retour à la normale")
    print("     - Réduit les faux positifs (sécheresse prolongée)")
    print()
    print("  5. Index de stress:")
    print("     - Calculé pour chaque période de stress")
    print("     - Mode 'weighted_mean': moyenne pondérée des anomalies")
    print("     - Utilisé comme indice de confiance")
    print()
    
    try:
        print("Début de la détection de dépérissement...")
        dieback_detection(**params)
        print("✅ Détection terminée avec succès!")
        print()
        print("Résultats générés dans:")
        print(f"  - {data_directory}/DataDieback/ (données de dépérissement)")
        print(f"    - count_dieback.tif (nombre d'anomalies successives)")
        print(f"    - first_date_unconfirmed_dieback.tif (première anomalie)")
        print(f"    - first_date_dieback.tif (première anomalie confirmée)")
        print(f"    - state_dieback.tif (état de dépérissement binaire)")
        print(f"  - {data_directory}/DataStress/ (données de stress)")
        print(f"    - dates_stress.tif (dates des périodes de stress)")
        print(f"    - nb_periods_stress.tif (nombre de périodes de stress)")
        print(f"    - cum_diff_stress.tif (somme des différences)")
        print(f"    - nb_dates_stress.tif (nombre d'acquisitions par période)")
        print(f"    - stress_index.tif (index de stress)")
        print(f"  - {data_directory}/DataAnomalies/ (anomalies par date)")
        print(f"    - Anomalies_YYYY-MM-DD.tif (anomalies détectées)")
        
    except Exception as e:
        print(f"❌ Erreur lors de la détection: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Étape 3 terminée avec succès!")
    else:
        print("\n💥 Échec de l'étape 3")
