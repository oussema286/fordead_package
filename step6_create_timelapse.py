#!/usr/bin/env python3
"""
Script pour l'étape 6: Create timelapse
Ce script crée une visualisation temporelle interactive pour explorer
l'évolution des anomalies de dépérissement détectées.
"""

from fordead.visualisation.create_timelapse import create_timelapse

def main():
    # Configuration des chemins
    data_directory = "tuto_output"
    
    print("=== Étape 6: Create timelapse ===")
    print(f"Répertoire de données: {data_directory}")
    print()
    
    # Coordonnées du centre de la zone d'intérêt
    x_center = 643069  # Coordonnée X (projection Sentinel-2)
    y_center = 5452565  # Coordonnée Y (projection Sentinel-2)
    buffer_size = 1500  # Buffer de 1500 mètres
    
    # Paramètres de configuration
    params = {
        'data_directory': data_directory,
        'x': x_center,  # Coordonnée X du centre
        'y': y_center,  # Coordonnée Y du centre
        'buffer': buffer_size  # Buffer en mètres
    }
    
    print("Paramètres utilisés:")
    for key, value in params.items():
        print(f"  {key}: {value}")
    print()
    
    print("Explication du timelapse:")
    print("  1. Création d'une visualisation interactive HTML")
    print("  2. Navigation temporelle avec un slider")
    print("  3. Affichage des images RGB Sentinel-2 en arrière-plan")
    print("  4. Superposition des zones de dépérissement détectées")
    print("  5. Légende interactive et informations au survol")
    print()
    
    print("Zone d'analyse:")
    print(f"  - Centre: X={x_center}, Y={y_center}")
    print(f"  - Buffer: {buffer_size} mètres")
    print(f"  - Zone totale: {buffer_size*2}x{buffer_size*2} mètres")
    print()
    
    print("Fonctionnalités du timelapse:")
    print("  - Slider pour naviguer entre les acquisitions")
    print("  - Images RGB Sentinel-2 en arrière-plan")
    print("  - Polygones blancs pour les attaques de scolytes confirmées")
    print("  - Légende interactive (clic pour masquer/afficher)")
    print("  - Zoom et déplacement de la vue")
    print("  - Informations au survol des pixels")
    print()
    
    print("Critères d'affichage des anomalies:")
    print("  - Détection confirmée (≥ 3 anomalies successives)")
    print("  - Pas de retour à la normale")
    print("  - Exclusion des fausses détections temporaires")
    print("  - Affichage à la date de la première anomalie")
    print()
    
    try:
        print("Début de la création du timelapse...")
        create_timelapse(**params)
        print("✅ Timelapse créé avec succès!")
        print()
        print("Résultats générés dans:")
        print(f"  - {data_directory}/Timelapses/")
        print(f"    - {x_center}_{y_center}.html (timelapse interactif)")
        print()
        print("Utilisation du timelapse:")
        print("  - Ouvrir le fichier .html dans un navigateur web")
        print("  - Utiliser le slider pour naviguer dans le temps")
        print("  - Cliquer sur la légende pour masquer/afficher les éléments")
        print("  - Zoomer en maintenant le clic et en délimitant une zone")
        print("  - Double-cliquer pour dézoomer")
        print("  - Survoler les pixels pour obtenir des informations")
        print()
        print("Informations disponibles au survol:")
        print("  - x: coordonnée X du pixel")
        print("  - y: coordonnée Y du pixel")
        print("  - z: [B04, B03, B02] - valeurs RGB Sentinel-2")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création du timelapse: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Étape 6 terminée avec succès!")
        print("🎬 Timelapse interactif créé!")
    else:
        print("\n💥 Échec de l'étape 6")
