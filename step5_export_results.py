#!/usr/bin/env python3
"""
Script pour l'étape 5: Export results
Ce script exporte les résultats de détection de dépérissement sous forme de shapefile
avec des classes de confiance basées sur l'index de stress.
"""

from fordead.steps.step5_export_results import export_results

def main():
    # Configuration des chemins
    data_directory = "tuto_output"
    
    print("=== Étape 5: Export results ===")
    print(f"Répertoire de données: {data_directory}")
    print()
    
    # Paramètres de configuration
    params = {
        'data_directory': data_directory,
        'frequency': "M",  # Fréquence d'export (M = mensuel)
        'multiple_files': False,  # Un seul fichier de résultats
        'conf_threshold_list': [0.265],  # Seuil de confiance
        'conf_classes_list': ["Low anomaly", "Severe anomaly"]  # Classes de confiance
    }
    
    print("Paramètres utilisés:")
    for key, value in params.items():
        print(f"  {key}: {value}")
    print()
    
    print("Explication du processus d'export:")
    print("  1. Vectorisation des résultats de dépérissement")
    print("  2. Création de polygones pour chaque zone de dépérissement")
    print("  3. Attribution des classes de confiance basées sur l'index de stress")
    print("  4. Export au format shapefile (.shp)")
    print()
    
    print("Classes de confiance:")
    print("  - Seuil: 0.265")
    print("  - 'Low anomaly': Index de stress < 0.265 (anomalie légère)")
    print("  - 'Severe anomaly': Index de stress ≥ 0.265 (anomalie sévère)")
    print()
    
    print("Fréquence d'export:")
    print("  - 'M' = Mensuel")
    print("  - Export des résultats à la fin de chaque mois")
    print("  - Polygones contiennent l'état à la fin de la période")
    print()
    
    print("Contenu des polygones:")
    print("  - Période de détection de la première anomalie")
    print("  - Classe de confiance (Low/Severe anomaly)")
    print("  - Géométrie des zones de dépérissement")
    print("  - Attributs temporels et de confiance")
    print()
    
    print("Filtrage appliqué:")
    print("  - Masque forestier: Seules les zones forestières")
    print("  - Anomalies confirmées: ≥ 3 anomalies successives")
    print("  - Pixels non analysables: Exclus")
    print()
    
    try:
        print("Début de l'export des résultats...")
        export_results(**params)
        print("✅ Export terminé avec succès!")
        print()
        print("Résultats générés dans:")
        print(f"  - {data_directory}/Results/")
        print(f"    - periodic_results_dieback.shp (shapefile principal)")
        print(f"    - periodic_results_dieback.dbf (table attributaire)")
        print(f"    - periodic_results_dieback.prj (projection)")
        print(f"    - periodic_results_dieback.shx (index)")
        print()
        print("Utilisation des résultats:")
        print("  - Visualisation dans un SIG (QGIS, ArcGIS)")
        print("  - Analyse spatiale des zones de dépérissement")
        print("  - Cartographie des forêts affectées")
        print("  - Suivi temporel des anomalies")
        print("  - Planification des interventions forestières")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'export: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Étape 5 terminée avec succès!")
        print("🎯 Workflow fordead complet terminé!")
    else:
        print("\n💥 Échec de l'étape 5")
