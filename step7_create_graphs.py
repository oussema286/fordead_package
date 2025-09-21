#!/usr/bin/env python3
"""
Script pour l'étape 7: Create graphs
Ce script crée des graphiques de séries temporelles pour visualiser
l'évolution des indices de végétation au niveau des pixels.
"""

from fordead.visualisation.vi_series_visualisation import vi_series_visualisation

def main():
    # Configuration des chemins
    data_directory = "tuto_output"
    shape_path = "fordead_data-main/fordead_data-main/vector/points_for_graphs.shp"
    
    print("=== Étape 7: Create graphs ===")
    print(f"Répertoire de données: {data_directory}")
    print(f"Fichier de points: {shape_path}")
    print()
    
    # Paramètres de configuration
    params = {
        'data_directory': data_directory,
        'shape_path': shape_path,  # Fichier shapefile avec les points
        'name_column': "id",  # Colonne contenant les identifiants
        'ymin': 0,  # Limite minimale de l'axe Y
        'ymax': 2,  # Limite maximale de l'axe Y
        'chunks': 1280  # Taille des chunks pour l'optimisation
    }
    
    print("Paramètres utilisés:")
    for key, value in params.items():
        print(f"  {key}: {value}")
    print()
    
    print("Explication des graphiques:")
    print("  1. Création de graphiques de séries temporelles par pixel")
    print("  2. Affichage des valeurs d'indices de végétation observées")
    print("  3. Superposition du modèle harmonique ajusté")
    print("  4. Indication du seuil de détection d'anomalie")
    print("  5. Marquage de la période d'entraînement")
    print()
    
    print("Contenu des graphiques:")
    print("  - Valeurs d'indices de végétation (points bleus)")
    print("  - Modèle harmonique ajusté (ligne rouge)")
    print("  - Seuil d'anomalie (ligne horizontale)")
    print("  - Période d'entraînement (zone grisée)")
    print("  - Anomalies détectées (marquées)")
    print()
    
    print("Types de pixels analysés:")
    print("  - Pixels sains: Évolution normale de la végétation")
    print("  - Pixels attaqués: Détection d'anomalies de dépérissement")
    print("  - Comparaison des patterns temporels")
    print()
    
    print("Utilisation des graphiques:")
    print("  - Validation des détections de dépérissement")
    print("  - Compréhension des patterns temporels")
    print("  - Analyse de la qualité du modèle harmonique")
    print("  - Documentation des résultats")
    print()
    
    try:
        print("Début de la création des graphiques...")
        vi_series_visualisation(**params)
        print("✅ Graphiques créés avec succès!")
        print()
        print("Résultats générés dans:")
        print(f"  - {data_directory}/TimeSeries/")
        print(f"    - Fichiers .png pour chaque point (id_1.png, id_2.png, etc.)")
        print()
        print("Caractéristiques des graphiques:")
        print("  - Format: PNG haute résolution")
        print("  - Axe Y: 0 à 2 (indices de végétation)")
        print("  - Axe X: Temps (dates des acquisitions)")
        print("  - Légende: Modèle, seuil, période d'entraînement")
        print()
        print("Utilisation des graphiques:")
        print("  - Ouvrir les fichiers .png dans un visualiseur d'images")
        print("  - Analyser l'évolution temporelle des pixels")
        print("  - Valider les détections de dépérissement")
        print("  - Comprendre les patterns de stress forestier")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des graphiques: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Étape 7 terminée avec succès!")
        print("📊 Graphiques de séries temporelles créés!")
    else:
        print("\n💥 Échec de l'étape 7")
