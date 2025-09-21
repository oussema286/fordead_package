#!/usr/bin/env python3
"""
Module d'évaluation des performances de détection
"""

import logging
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd
import geopandas as gpd
from datetime import datetime, timedelta
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, roc_curve, precision_recall_curve
import json

class DisturbanceEvaluator:
    """
    Classe pour l'évaluation des performances de détection
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialiser l'évaluateur
        
        Args:
            config: Configuration du pipeline
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Paramètres d'évaluation
        self.buffer_distance = config['evaluation']['buffer_distance']
        self.metrics = config['evaluation']['metrics']
        
        # Charger les données de référence
        self.reference_data = self._load_reference_data()
    
    def _load_reference_data(self) -> gpd.GeoDataFrame:
        """
        Charger les données de référence (European Forest Disturbance Map)
        
        Returns:
            GeoDataFrame avec les données de référence
        """
        self.logger.info("Chargement des données de référence")
        
        # Dans un vrai cas, charger depuis la source
        # Ici, on simule des données de référence
        reference_data = self._simulate_reference_data()
        
        self.logger.info(f"Données de référence chargées: {len(reference_data)} événements")
        return reference_data
    
    def _simulate_reference_data(self) -> gpd.GeoDataFrame:
        """
        Simuler des données de référence pour le test
        
        Returns:
            GeoDataFrame simulé
        """
        # Créer des données simulées
        n_events = 50
        
        # Coordonnées simulées dans la zone d'étude
        lons = np.random.uniform(6.0, 7.0, n_events)
        lats = np.random.uniform(45.0, 46.0, n_events)
        
        # Types de perturbation simulés
        disturbance_types = np.random.choice(
            ['wind', 'bark_beetle', 'mixed'],
            n_events,
            p=[0.3, 0.5, 0.2]
        )
        
        # Dates simulées
        dates = pd.date_range('2018-01-01', '2020-12-31', periods=n_events)
        
        # Créer les géométries
        from shapely.geometry import Point
        geometries = [Point(lon, lat) for lon, lat in zip(lons, lats)]
        
        # Créer le GeoDataFrame
        gdf = gpd.GeoDataFrame({
            'event_id': range(n_events),
            'date': dates,
            'type': disturbance_types,
            'geometry': geometries
        }, crs='EPSG:4326')
        
        return gdf
    
    def evaluate_detections(self, classifications: Dict[str, Any]) -> Dict[str, Any]:
        """
        Évaluer les performances de détection
        
        Args:
            classifications: Résultats de la classification
            
        Returns:
            Métriques d'évaluation
        """
        self.logger.info("Début de l'évaluation des détections")
        
        # Extraire les détections
        detections = classifications['classifications']
        
        if not detections:
            self.logger.warning("Aucune détection à évaluer")
            return self._empty_metrics()
        
        # Convertir les détections en GeoDataFrame
        detection_gdf = self._detections_to_gdf(detections)
        
        # Calculer les métriques de base
        basic_metrics = self._calculate_basic_metrics(detection_gdf)
        
        # Calculer les métriques de précision/recall
        precision_recall_metrics = self._calculate_precision_recall(detection_gdf)
        
        # Calculer les métriques de timing
        timing_metrics = self._calculate_timing_metrics(detection_gdf)
        
        # Calculer les métriques de classification
        classification_metrics = self._calculate_classification_metrics(detection_gdf)
        
        # Combiner toutes les métriques
        all_metrics = {
            **basic_metrics,
            **precision_recall_metrics,
            **timing_metrics,
            **classification_metrics
        }
        
        # Générer les visualisations
        self._generate_evaluation_plots(detection_gdf, all_metrics)
        
        self.logger.info("Évaluation terminée")
        return all_metrics
    
    def _detections_to_gdf(self, detections: List[Any]) -> gpd.GeoDataFrame:
        """
        Convertir les détections en GeoDataFrame
        
        Args:
            detections: Liste des détections (peut être des dicts ou des strings)
            
        Returns:
            GeoDataFrame des détections
        """
        # Extraire les informations des détections
        data = []
        for i, detection in enumerate(detections):
            # Vérifier si c'est un dictionnaire ou une chaîne
            if isinstance(detection, dict):
                # Coordonnées approximatives (à adapter selon la projection)
                pixel_idx = detection.get('pixel_count', i)
                lon = 6.0 + (pixel_idx % 100) * 0.01
                lat = 45.0 + (pixel_idx // 100) * 0.01
                
                data.append({
                    'detection_id': detection.get('zone_id', f'detection_{i}'),
                    'date': detection.get('date_range', ['2020-01-01'])[0],
                    'type': detection.get('disturbance_type', 'unknown'),
                    'confidence': detection.get('confidence', 0.5),
                    'wind_score': detection.get('wind_score', 0.0),
                    'geometry': gpd.points_from_xy([lon], [lat])[0]
                })
            else:
                # Si c'est une chaîne, créer une détection simulée
                lon = 6.0 + (i % 100) * 0.01
                lat = 45.0 + (i // 100) * 0.01
                
                data.append({
                    'detection_id': f'detection_{i}',
                    'date': '2020-01-01',
                    'type': 'simulated',
                    'confidence': 0.5,
                    'wind_score': 0.0,
                    'geometry': gpd.points_from_xy([lon], [lat])[0]
                })
        
        gdf = gpd.GeoDataFrame(data, crs='EPSG:4326')
        return gdf
    
    def _calculate_basic_metrics(self, detection_gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
        """
        Calculer les métriques de base
        
        Args:
            detection_gdf: GeoDataFrame des détections
            
        Returns:
            Métriques de base
        """
        return {
            'total_detections': len(detection_gdf),
            'detection_rate': len(detection_gdf) / len(self.reference_data) if len(self.reference_data) > 0 else 0,
            'avg_confidence': detection_gdf['confidence'].mean() if len(detection_gdf) > 0 else 0,
            'high_confidence_detections': len(detection_gdf[detection_gdf['confidence'] > 0.7]) if len(detection_gdf) > 0 else 0
        }
    
    def _calculate_precision_recall(self, detection_gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
        """
        Calculer les métriques de précision et recall
        
        Args:
            detection_gdf: GeoDataFrame des détections
            
        Returns:
            Métriques de précision/recall
        """
        if len(detection_gdf) == 0:
            return {
                'precision': 0,
                'recall': 0,
                'f1': 0
            }
        
        # Matcher les détections avec les données de référence
        matches = self._match_detections_with_reference(detection_gdf)
        
        # Calculer les métriques
        true_positives = len(matches)
        false_positives = len(detection_gdf) - true_positives
        false_negatives = len(self.reference_data) - true_positives
        
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives
        }
    
    def _match_detections_with_reference(self, detection_gdf: gpd.GeoDataFrame) -> List[Dict[str, Any]]:
        """
        Matcher les détections avec les données de référence
        
        Args:
            detection_gdf: GeoDataFrame des détections
            
        Returns:
            Liste des matches
        """
        matches = []
        
        for _, detection in detection_gdf.iterrows():
            # Trouver les événements de référence dans un rayon donné
            detection_geom = detection.geometry
            buffer_geom = detection_geom.buffer(self.buffer_distance / 111000)  # Convertir m en degrés
            
            # Trouver les intersections
            intersecting = self.reference_data[self.reference_data.geometry.intersects(buffer_geom)]
            
            if len(intersecting) > 0:
                # Prendre le plus proche
                distances = intersecting.geometry.distance(detection_geom)
                closest_idx = distances.idxmin()
                closest_event = self.reference_data.loc[closest_idx]
                
                matches.append({
                    'detection_id': detection['detection_id'],
                    'reference_id': closest_event['event_id'],
                    'distance': distances[closest_idx] * 111000,  # Convertir en mètres
                    'detection_type': detection['type'],
                    'reference_type': closest_event['type']
                })
        
        return matches
    
    def _calculate_timing_metrics(self, detection_gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
        """
        Calculer les métriques de timing
        
        Args:
            detection_gdf: GeoDataFrame des détections
            
        Returns:
            Métriques de timing
        """
        if len(detection_gdf) == 0:
            return {
                'avg_lead_time': 0,
                'min_lead_time': 0,
                'max_lead_time': 0,
                'lead_time_std': 0
            }
        
        # Calculer les temps de détection (lead times)
        lead_times = []
        
        for _, detection in detection_gdf.iterrows():
            detection_date = pd.to_datetime(detection['date'])
            
            # Trouver l'événement de référence correspondant
            detection_geom = detection.geometry
            buffer_geom = detection_geom.buffer(self.buffer_distance / 111000)
            
            intersecting = self.reference_data[self.reference_data.geometry.intersects(buffer_geom)]
            
            if len(intersecting) > 0:
                # Prendre le plus proche
                distances = intersecting.geometry.distance(detection_geom)
                closest_idx = distances.idxmin()
                closest_event = self.reference_data.loc[closest_idx]
                
                reference_date = pd.to_datetime(closest_event['date'])
                lead_time = (detection_date - reference_date).days
                lead_times.append(lead_time)
        
        if not lead_times:
            return {
                'avg_lead_time': 0,
                'min_lead_time': 0,
                'max_lead_time': 0,
                'lead_time_std': 0
            }
        
        return {
            'avg_lead_time': np.mean(lead_times),
            'min_lead_time': np.min(lead_times),
            'max_lead_time': np.max(lead_times),
            'lead_time_std': np.std(lead_times)
        }
    
    def _calculate_classification_metrics(self, detection_gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
        """
        Calculer les métriques de classification vent vs scolytes
        
        Args:
            detection_gdf: GeoDataFrame des détections
            
        Returns:
            Métriques de classification
        """
        if len(detection_gdf) == 0:
            return {
                'classification_accuracy': 0,
                'wind_precision': 0,
                'beetle_precision': 0,
                'wind_recall': 0,
                'beetle_recall': 0
            }
        
        # Matcher avec les données de référence
        matches = self._match_detections_with_reference(detection_gdf)
        
        if not matches:
            return {
                'classification_accuracy': 0,
                'wind_precision': 0,
                'beetle_precision': 0,
                'wind_recall': 0,
                'beetle_recall': 0
            }
        
        # Extraire les types prédits et réels
        predicted_types = [m['detection_type'] for m in matches]
        true_types = [m['reference_type'] for m in matches]
        
        # Calculer l'accuracy globale
        correct = sum(1 for p, t in zip(predicted_types, true_types) if p == t)
        accuracy = correct / len(matches)
        
        # Calculer les métriques par type
        wind_precision = self._calculate_precision_for_type(predicted_types, true_types, 'wind')
        beetle_precision = self._calculate_precision_for_type(predicted_types, true_types, 'bark_beetle')
        wind_recall = self._calculate_recall_for_type(predicted_types, true_types, 'wind')
        beetle_recall = self._calculate_recall_for_type(predicted_types, true_types, 'bark_beetle')
        
        return {
            'classification_accuracy': accuracy,
            'wind_precision': wind_precision,
            'beetle_precision': beetle_precision,
            'wind_recall': wind_recall,
            'beetle_recall': beetle_recall
        }
    
    def _calculate_precision_for_type(self, predicted: List[str], true: List[str], target_type: str) -> float:
        """Calculer la précision pour un type donné"""
        predicted_target = sum(1 for p in predicted if p == target_type)
        if predicted_target == 0:
            return 0
        
        correct_target = sum(1 for p, t in zip(predicted, true) if p == target_type and t == target_type)
        return correct_target / predicted_target
    
    def _calculate_recall_for_type(self, predicted: List[str], true: List[str], target_type: str) -> float:
        """Calculer le recall pour un type donné"""
        true_target = sum(1 for t in true if t == target_type)
        if true_target == 0:
            return 0
        
        correct_target = sum(1 for p, t in zip(predicted, true) if p == target_type and t == target_type)
        return correct_target / true_target
    
    def _generate_evaluation_plots(self, detection_gdf: gpd.GeoDataFrame, metrics: Dict[str, Any]):
        """
        Générer les graphiques d'évaluation
        
        Args:
            detection_gdf: GeoDataFrame des détections
            metrics: Métriques calculées
        """
        self.logger.info("Génération des graphiques d'évaluation")
        
        output_dir = Path(self.config['output']['evaluations'])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Graphique de distribution des confidences
        plt.figure(figsize=(10, 6))
        plt.hist(detection_gdf['confidence'], bins=20, alpha=0.7, edgecolor='black')
        plt.xlabel('Confiance de détection')
        plt.ylabel('Nombre de détections')
        plt.title('Distribution des confidences de détection')
        plt.grid(True, alpha=0.3)
        plt.savefig(output_dir / 'confidence_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Graphique des types de perturbation
        plt.figure(figsize=(10, 6))
        type_counts = detection_gdf['type'].value_counts()
        plt.pie(type_counts.values, labels=type_counts.index, autopct='%1.1f%%')
        plt.title('Distribution des types de perturbation détectés')
        plt.savefig(output_dir / 'disturbance_types.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Graphique des métriques de performance
        plt.figure(figsize=(12, 8))
        metric_names = ['Precision', 'Recall', 'F1-Score', 'Classification Accuracy']
        metric_values = [
            metrics.get('precision', 0),
            metrics.get('recall', 0),
            metrics.get('f1', 0),
            metrics.get('classification_accuracy', 0)
        ]
        
        bars = plt.bar(metric_names, metric_values, color=['skyblue', 'lightcoral', 'lightgreen', 'gold'])
        plt.ylabel('Score')
        plt.title('Métriques de performance de détection')
        plt.ylim(0, 1)
        
        # Ajouter les valeurs sur les barres
        for bar, value in zip(bars, metric_values):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{value:.3f}', ha='center', va='bottom')
        
        plt.grid(True, alpha=0.3)
        plt.savefig(output_dir / 'performance_metrics.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 4. Sauvegarder les métriques en JSON
        with open(output_dir / 'evaluation_metrics.json', 'w') as f:
            json.dump(metrics, f, indent=2, default=str)
        
        self.logger.info(f"Graphiques sauvegardés dans: {output_dir}")
    
    def _empty_metrics(self) -> Dict[str, Any]:
        """Retourner des métriques vides"""
        return {
            'total_detections': 0,
            'detection_rate': 0,
            'avg_confidence': 0,
            'high_confidence_detections': 0,
            'precision': 0,
            'recall': 0,
            'f1': 0,
            'true_positives': 0,
            'false_positives': 0,
            'false_negatives': 0,
            'avg_lead_time': 0,
            'min_lead_time': 0,
            'max_lead_time': 0,
            'lead_time_std': 0,
            'classification_accuracy': 0,
            'wind_precision': 0,
            'beetle_precision': 0,
            'wind_recall': 0,
            'beetle_recall': 0
        }
