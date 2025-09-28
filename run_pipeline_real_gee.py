#!/usr/bin/env python3
"""
Pipeline complet avec de vraies données Sentinel-2 via Google Earth Engine
"""

import sys
import os
from pathlib import Path
import yaml
import logging
from datetime import datetime
import numpy as np
import xarray as xr
import geopandas as gpd
from shapely.geometry import box
import ee

# Ajouter le répertoire technical_test au path
sys.path.append('technical_test')

def run_pipeline_real_gee():
    """Lancer le pipeline complet avec de vraies données Sentinel-2"""
    print("🚀 PIPELINE COMPLET AVEC VRAIES DONNÉES SENTINEL-2")
    print("=" * 60)
    
    try:
        # 1. Charger la configuration
        print("\n📋 ÉTAPE 1 : Chargement de la configuration")
        with open('technical_test/configs/config_test.yaml', 'r') as f:
            config = yaml.safe_load(f)
        print(f"  ✅ Configuration chargée: {config['project_name']} v{config['version']}")
        
        # 2. Créer une parcelle de test
        print("\n🗺️ ÉTAPE 2 : Création de la parcelle de test")
        
        # Parcelle: Forêt de Fontainebleau (France)
        bbox = [2.6, 48.3, 2.8, 48.5]  # [minx, miny, maxx, maxy]
        geometry = [box(bbox[0], bbox[1], bbox[2], bbox[3])]
        roi = gpd.GeoDataFrame({'id': [1], 'name': ['Fontainebleau']}, 
                              geometry=geometry, crs='EPSG:4326')
        
        print(f"  ✅ Parcelle créée: Fontainebleau")
        print(f"    - Bbox: {bbox}")
        print(f"    - Surface: {(bbox[2]-bbox[0])*(bbox[3]-bbox[1]):.4f} deg²")
        
        # 3. Initialiser l'ingestion avec Google Earth Engine
        print("\n🔧 ÉTAPE 3 : Initialisation de l'ingestion avec Google Earth Engine")
        from technical_test.data_ingestion_gee import Sentinel2IngestionGEE
        ingestion = Sentinel2IngestionGEE(config)
        print("  ✅ Ingestion Sentinel-2 avec GEE initialisée")
        
        # 4. Télécharger de vraies données Sentinel-2 (si pas déjà fait)
        print("\n📥 ÉTAPE 4 : Téléchargement de vraies données Sentinel-2")
        
        # Vérifier si les données existent déjà
        data_dir = os.path.join(config['output']['base_path'], 'data', 'sentinel2_gee')
        if os.path.exists(data_dir) and os.listdir(data_dir):
            print("  📁 Données Sentinel-2 déjà téléchargées, réutilisation...")
            # Lister les acquisitions existantes
            acquisitions = []
            for acq_name in sorted(os.listdir(data_dir)):
                acq_path = os.path.join(data_dir, acq_name)
                if os.path.isdir(acq_path) and acq_name.startswith('SENTINEL2_'):
                    date_str = acq_name.replace('SENTINEL2_', '')
                    acquisitions.append({
                        'title': acq_name,
                        'date': f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}",
                        'path': acq_path,
                        'real_data': True
                    })
            print(f"  ✅ Données Sentinel-2 réutilisées: {len(acquisitions)} acquisitions")
        else:
            acquisitions = ingestion.download_sentinel2_data(roi)
            print(f"  ✅ Données Sentinel-2 téléchargées: {len(acquisitions)} acquisitions")
        
        if acquisitions and acquisitions[0].get('real_data', False):
            print(f"    - Source: VRAIES DONNÉES SENTINEL-2 ✅")
            print(f"    - Période: {acquisitions[0]['date']} à {acquisitions[-1]['date']}")
            print(f"    - Couverture nuageuse moyenne: {np.mean([acq.get('cloud_cover', 0) for acq in acquisitions]):.1f}%")
        else:
            print(f"    - Source: DONNÉES SIMULÉES ⚠️")
        
        # 5. Traiter les données Sentinel-2
        print("\n🔄 ÉTAPE 5 : Traitement des données Sentinel-2")
        sentinel_data = ingestion.process_sentinel2_data(acquisitions)
        print(f"  ✅ Données traitées: {sentinel_data.dims}")
        print(f"    - Variables: {list(sentinel_data.data_vars)}")
        
        # 6. Intégration avec fordead (détection de dépérissement)
        print("\n🌲 ÉTAPE 6 : Détection de dépérissement avec fordead")
        from technical_test.fordead_wrapper_real import FordeadWrapperReal
        fordead_wrapper = FordeadWrapperReal(config)
        
        # Exécuter le pipeline fordead pour détecter les zones de dépérissement
        fordead_results = fordead_wrapper.run_fordead_pipeline(sentinel_data)
        print(f"  ✅ Fordead terminé: {len(fordead_results)} résultats")
        
        # Extraire les pixels de dépérissement détectés
        dieback_pixels = fordead_results.get('dieback_pixels', [])
        print(f"    - Pixels de dépérissement détectés: {len(dieback_pixels)}")
        
        # 7. Détection de changements avec ruptures (affinage temporel)
        print("\n🔍 ÉTAPE 7 : Détection de changements avec ruptures")
        from technical_test.change_detection import RupturesDetector
        detector = RupturesDetector(config)
        
        # Détecter les changements sur l'indice CRSWIR (affinage temporel des pixels fordead)
        vi_data = sentinel_data['crswir']
        change_results = detector.detect_changes(vi_data)
        print(f"  ✅ Détection terminée: {len(change_results['change_points'])} changements détectés")
        print(f"    - Affinage temporel des pixels détectés par fordead")
        
        # Sauvegarder les masques de détection
        from pathlib import Path
        detections_dir = Path(config['output']['detections'])
        detections_dir.mkdir(parents=True, exist_ok=True)
        detector.save_results(change_results, detections_dir)
        print(f"  ✅ Masques sauvegardés dans: {detections_dir}")
        
        # 8. Chargement des données de perturbation de référence
        print("\n🗺️ ÉTAPE 8 : Chargement des données de perturbation de référence")
        from technical_test.disturbance_map_integration import DisturbanceMapIntegrator
        from technical_test.era5_wind_analysis import ERA5WindAnalyzer
        from technical_test.advanced_classification import AdvancedWindBeetleClassifier
        
        # Charger les données de perturbation
        disturbance_integrator = DisturbanceMapIntegrator(config)
        
        # Charger la ROI depuis le fichier GeoJSON
        import geopandas as gpd_roi
        roi_file = config['roi']['file_path']
        if os.path.exists(roi_file):
            roi_gdf = gpd_roi.read_file(roi_file)
            roi_bounds = roi_gdf.total_bounds
            roi_geometry = ee.Geometry.Rectangle([roi_bounds[0], roi_bounds[1], roi_bounds[2], roi_bounds[3]])
            print(f"  📍 ROI chargée depuis {roi_file}: {roi_bounds}")
        else:
            # Fallback vers les coordonnées de la config
            bbox = config['roi']['bbox']
            roi_geometry = ee.Geometry.Rectangle([bbox[0], bbox[1], bbox[2], bbox[3]])
            print(f"  📍 ROI utilisée depuis config: {bbox}")
        
        disturbance_data = disturbance_integrator.load_disturbance_data(roi_geometry)
        print(f"  ✅ Données de perturbation chargées: {disturbance_data['total_events']} événements")
        
        # Extraire les données de vent ERA5
        print("\n🌪️ ÉTAPE 9 : Extraction des données de vent ERA5")
        wind_analyzer = ERA5WindAnalyzer(config)
        wind_data = wind_analyzer.extract_wind_data(disturbance_data['disturbances'], roi_geometry)
        print(f"  ✅ Données de vent extraites: {wind_data['total_analyzed']} analyses")
        
        # Classification avancée
        print("\n🔬 ÉTAPE 10 : Classification avancée Wind vs Bark Beetle")
        classifier = AdvancedWindBeetleClassifier(config)
        classification_results = classifier.classify_disturbances(
            disturbance_data['disturbances'], 
            wind_data['wind_data']
        )
        print(f"  ✅ Classification terminée: {classification_results['total_classified']} classifications")
        print(f"    - Précision: {classification_results['metrics']['precision']:.3f}")
        print(f"    - Rappel: {classification_results['metrics']['recall']:.3f}")
        print(f"    - Délai de détection: {classification_results['metrics']['detection_lead_time_days']:.1f} jours")
        
        # Sauvegarder les résultats
        classifier.save_classification_results(classification_results, Path(config['output']['classifications']))
        wind_analyzer.save_wind_data(wind_data, Path(config['output']['wind_data']))
        disturbance_integrator.save_disturbance_data(disturbance_data, Path(config['output']['disturbances']))
        
        # Extraire les classifications pour compatibilité
        classifications = [c['classified_type'] for c in classification_results['classifications']]
        print(f"  ✅ Classifications simulées: {len(classifications)}")
        
        # 11. Évaluation des performances
        print("\n📊 ÉTAPE 11 : Évaluation des performances")
        from technical_test.evaluation import DisturbanceEvaluator
        evaluator = DisturbanceEvaluator(config)
        
        # Créer un dictionnaire structuré pour l'évaluation
        evaluation_data = {
            'change_points': change_results['change_points'],
            'classifications': classifications,
            'result_maps': change_results.get('result_maps', {}),
            'change_analysis': change_results.get('change_analysis', {})
        }
        
        try:
            evaluation_results = evaluator.evaluate_detections(evaluation_data)
            print(f"  ✅ Évaluation terminée: {list(evaluation_results.keys())}")
        except Exception as e:
            print(f"  ⚠️ Erreur évaluation: {e}")
            evaluation_results = {'metrics': {'precision': 0.0, 'recall': 0.0}}
        
        # 10. Résumé final
        print("\n🎉 PIPELINE COMPLET TERMINÉ AVEC SUCCÈS !")
        print("=" * 60)
        print(f"📊 Résultats finaux:")
        print(f"  - Acquisitions Sentinel-2: {len(acquisitions)}")
        print(f"  - Changements détectés: {len(change_results['change_points'])}")
        print(f"  - Classifications: {len(classifications)}")
        print(f"  - Pixels fordead détectés: {len(dieback_pixels)}")
        print(f"  - Changements ruptures: {len(change_results['change_points'])}")
        print(f"  - Résultats fordead: {len(fordead_results)}")
        print(f"  - Métriques d'évaluation: {len(evaluation_results)}")
        
        # Statistiques des classifications
        wind_count = classifications.count('wind')
        beetle_count = classifications.count('bark_beetle')
        print(f"  - Classifications vent: {wind_count}")
        print(f"  - Classifications scolytes: {beetle_count}")
        
        # Vérifier si on a utilisé de vraies données
        if acquisitions and acquisitions[0].get('real_data', False):
            print(f"  - Source: VRAIES DONNÉES SENTINEL-2 ✅")
            print(f"  - Méthode: Google Earth Engine")
        else:
            print(f"  - Source: DONNÉES SIMULÉES ⚠️")
        

        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur dans le pipeline: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_pipeline_real_gee()
    if success:
        print("\n✅ Pipeline complet réussi !")
    else:
        print("\n❌ Pipeline échoué !")
