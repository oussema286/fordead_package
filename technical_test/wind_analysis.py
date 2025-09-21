#!/usr/bin/env python3
"""
Module d'analyse du vent et classification vent vs scolytes
"""

import logging
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd
import geopandas as gpd
from datetime import datetime, timedelta
import ee
import json
from pathlib import Path
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from scipy import stats

class WindBeetleClassifier:
    """
    Classe pour la classification vent vs scolytes basée sur les données ERA5
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialiser le classifieur vent vs scolytes
        
        Args:
            config: Configuration du pipeline
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Paramètres ERA5
        self.wind_threshold = config['era5']['wind_threshold']
        self.variables = config['era5']['variables']
        
        # Initialiser Google Earth Engine
        self._initialize_ee()
        
        # Charger les données de référence
        self.disturbance_map = self._load_disturbance_map()
    
    def _initialize_ee(self):
        """Initialiser Google Earth Engine"""
        try:
            ee.Initialize(project='symbiose-472610')
            self.logger.info("Google Earth Engine initialisé avec le projet symbiose-472610")
        except Exception as e:
            self.logger.error(f"Erreur initialisation EE: {e}")
            raise
    
    def _load_disturbance_map(self) -> ee.Image:
        """
        Charger la carte des perturbations européennes
        
        Returns:
            Image EE avec les données de perturbation
        """
        self.logger.info("Chargement de la carte des perturbations européennes")
        
        try:
            # Charger les images de perturbation
            disturbance_agent = ee.Image("projects/ee-albaviana/assets/disturbance_agent_v211")
            disturbance_number = ee.Image("projects/ee-albaviana/assets/number_disturbances_v211")
            disturbance_year = ee.Image("projects/ee-albaviana/assets/latest_disturbance_v211")
            
            # Combiner les images
            disturbance_map = disturbance_agent.addBands(disturbance_number).addBands(disturbance_year)
            
            self.logger.info("Carte des perturbations chargée")
            return disturbance_map
            
        except Exception as e:
            self.logger.error(f"Erreur chargement carte perturbations: {e}")
            raise
    
    def get_era5_wind_data(self, geometry: ee.Geometry, 
                          start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Récupérer les données de vent ERA5 pour une géométrie et une période
        
        Args:
            geometry: Géométrie d'intérêt
            start_date: Date de début (YYYY-MM-DD)
            end_date: Date de fin (YYYY-MM-DD)
            
        Returns:
            Dictionnaire avec les données de vent
        """
        self.logger.info(f"Récupération des données ERA5: {start_date} à {end_date}")
        
        try:
            # Charger les données ERA5
            era5 = ee.ImageCollection('ECMWF/ERA5/DAILY') \
                .filterDate(start_date, end_date) \
                .filterBounds(geometry)
            
            # Sélectionner les variables de vent
            wind_data = era5.select(['mean_10m_wind_speed', 'mean_10m_wind_direction'])
            
            # Calculer les statistiques pour la géométrie
            def calculate_stats(image):
                stats = image.reduceRegion(
                    reducer=ee.Reducer.mean().combine(
                        ee.Reducer.max(), sharedInputs=True
                    ).combine(
                        ee.Reducer.min(), sharedInputs=True
                    ),
                    geometry=geometry,
                    scale=1000,  # 1km de résolution
                    maxPixels=1e9
                )
                return image.set(stats)
            
            # Appliquer les statistiques
            wind_stats = wind_data.map(calculate_stats)
            
            # Récupérer les données
            wind_list = wind_stats.getInfo()
            
            # Traiter les résultats
            wind_data_processed = []
            for feature in wind_list['features']:
                properties = feature['properties']
                wind_data_processed.append({
                    'date': properties['system:time_start'],
                    'mean_wind_speed': properties.get('mean_10m_wind_speed_mean', 0),
                    'max_wind_speed': properties.get('mean_10m_wind_speed_max', 0),
                    'min_wind_speed': properties.get('mean_10m_wind_speed_min', 0),
                    'wind_direction': properties.get('mean_10m_wind_direction_mean', 0)
                })
            
            self.logger.info(f"Données ERA5 récupérées: {len(wind_data_processed)} jours")
            return {
                'wind_data': wind_data_processed,
                'geometry': geometry,
                'date_range': (start_date, end_date)
            }
            
        except Exception as e:
            self.logger.error(f"Erreur récupération ERA5: {e}")
            raise
    
    def classify_disturbances(self, change_detections: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classifier les perturbations détectées en vent vs scolytes
        
        Args:
            change_detections: Résultats de la détection de changements
            
        Returns:
            Classification des perturbations
        """
        self.logger.info("Classification des perturbations vent vs scolytes")
        
        # Extraire les zones de perturbation
        disturbance_zones = self._extract_disturbance_zones(change_detections)
        
        # Pour chaque zone, analyser les données de vent
        classifications = []
        
        for zone in disturbance_zones:
            try:
                # Récupérer les données de vent pour cette zone
                wind_data = self.get_era5_wind_data(
                    zone['geometry'],
                    zone['start_date'],
                    zone['end_date']
                )
                
                # Analyser les vitesses de vent
                wind_analysis = self._analyze_wind_patterns(wind_data)
                
                # Classifier la perturbation
                classification = self._classify_disturbance_type(zone, wind_analysis)
                
                classifications.append(classification)
                
            except Exception as e:
                self.logger.warning(f"Erreur classification zone {zone['id']}: {e}")
                continue
        
        # Résultats globaux
        results = {
            'classifications': classifications,
            'summary': self._summarize_classifications(classifications)
        }
        
        self.logger.info(f"Classification terminée: {len(classifications)} zones analysées")
        return results
    
    def _extract_disturbance_zones(self, change_detections: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extraire les zones de perturbation à partir des détections
        
        Args:
            change_detections: Résultats de la détection
            
        Returns:
            Liste des zones de perturbation
        """
        self.logger.info("Extraction des zones de perturbation")
        
        zones = []
        change_analysis = change_detections['change_analysis']
        
        # Grouper les pixels avec des changements significatifs
        significant_changes = [c for c in change_analysis['change_details'] if c['significant']]
        
        if not significant_changes:
            self.logger.warning("Aucun changement significatif trouvé")
            return zones
        
        # Créer des zones basées sur la proximité des pixels
        zones = self._cluster_nearby_changes(significant_changes)
        
        self.logger.info(f"Zones de perturbation extraites: {len(zones)}")
        return zones
    
    def _cluster_nearby_changes(self, changes: List[Dict[str, Any]], 
                               distance_threshold: float = 1000.0) -> List[Dict[str, Any]]:
        """
        Grouper les changements proches en zones
        
        Args:
            changes: Liste des changements significatifs
            distance_threshold: Distance maximale pour grouper (mètres)
            
        Returns:
            Liste des zones groupées
        """
        # Implémentation simplifiée - grouper par proximité temporelle et spatiale
        zones = []
        
        # Grouper par période temporelle (par mois)
        changes_by_month = {}
        for change in changes:
            # Convertir l'index de changement en date approximative
            month_key = f"month_{change['change_point'] // 30}"
            
            if month_key not in changes_by_month:
                changes_by_month[month_key] = []
            changes_by_month[month_key].append(change)
        
        # Créer une zone pour chaque groupe
        for month_key, month_changes in changes_by_month.items():
            if len(month_changes) >= 3:  # Minimum 3 pixels pour former une zone
                zone = {
                    'id': f"zone_{month_key}",
                    'changes': month_changes,
                    'pixel_count': len(month_changes),
                    'start_date': f"2018-{month_key.split('_')[1].zfill(2)}-01",
                    'end_date': f"2018-{month_key.split('_')[1].zfill(2)}-28",
                    'geometry': self._create_zone_geometry(month_changes)
                }
                zones.append(zone)
        
        return zones
    
    def _create_zone_geometry(self, changes: List[Dict[str, Any]]) -> ee.Geometry:
        """
        Créer une géométrie EE pour une zone de perturbation
        
        Args:
            changes: Liste des changements dans la zone
            
        Returns:
            Géométrie EE de la zone
        """
        # Coordonnées approximatives basées sur les indices de pixels
        # Dans un vrai cas, il faudrait convertir les indices en coordonnées géographiques
        lons = []
        lats = []
        
        for change in changes:
            pixel_idx = change['pixel_index']
            # Conversion simplifiée - à adapter selon la projection
            lon = 6.0 + (pixel_idx % 432) * 0.001  # Exemple
            lat = 45.0 + (pixel_idx // 432) * 0.001  # Exemple
            lons.append(lon)
            lats.append(lat)
        
        # Créer un rectangle englobant
        min_lon, max_lon = min(lons), max(lons)
        min_lat, max_lat = min(lats), max(lats)
        
        # Ajouter un buffer
        buffer = 0.01  # ~1km
        geometry = ee.Geometry.Rectangle([
            min_lon - buffer, min_lat - buffer,
            max_lon + buffer, max_lat + buffer
        ])
        
        return geometry
    
    def _analyze_wind_patterns(self, wind_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyser les patterns de vent pour une zone
        
        Args:
            wind_data: Données de vent ERA5
            
        Returns:
            Analyse des patterns de vent
        """
        wind_series = wind_data['wind_data']
        
        if not wind_series:
            return {
                'max_wind_speed': 0,
                'mean_wind_speed': 0,
                'wind_events': 0,
                'high_wind_days': 0
            }
        
        # Extraire les vitesses de vent
        wind_speeds = [day['max_wind_speed'] for day in wind_series if day['max_wind_speed'] is not None]
        
        if not wind_speeds:
            return {
                'max_wind_speed': 0,
                'mean_wind_speed': 0,
                'wind_events': 0,
                'high_wind_days': 0
            }
        
        # Calculer les statistiques
        max_wind = max(wind_speeds)
        mean_wind = np.mean(wind_speeds)
        high_wind_days = sum(1 for speed in wind_speeds if speed > self.wind_threshold)
        
        # Détecter les événements de vent fort (consecutifs)
        wind_events = self._detect_wind_events(wind_speeds)
        
        return {
            'max_wind_speed': max_wind,
            'mean_wind_speed': mean_wind,
            'wind_events': len(wind_events),
            'high_wind_days': high_wind_days,
            'wind_series': wind_speeds
        }
    
    def _detect_wind_events(self, wind_speeds: List[float], 
                           min_duration: int = 2) -> List[Dict[str, Any]]:
        """
        Détecter les événements de vent fort
        
        Args:
            wind_speeds: Série des vitesses de vent
            min_duration: Durée minimale d'un événement (jours)
            
        Returns:
            Liste des événements de vent détectés
        """
        events = []
        in_event = False
        event_start = 0
        
        for i, speed in enumerate(wind_speeds):
            if speed > self.wind_threshold:
                if not in_event:
                    event_start = i
                    in_event = True
            else:
                if in_event:
                    event_duration = i - event_start
                    if event_duration >= min_duration:
                        events.append({
                            'start': event_start,
                            'end': i,
                            'duration': event_duration,
                            'max_speed': max(wind_speeds[event_start:i])
                        })
                    in_event = False
        
        # Gérer le cas où l'événement se termine à la fin de la série
        if in_event:
            event_duration = len(wind_speeds) - event_start
            if event_duration >= min_duration:
                events.append({
                    'start': event_start,
                    'end': len(wind_speeds),
                    'duration': event_duration,
                    'max_speed': max(wind_speeds[event_start:])
                })
        
        return events
    
    def _classify_disturbance_type(self, zone: Dict[str, Any], 
                                  wind_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classifier le type de perturbation (vent vs scolytes)
        
        Args:
            zone: Zone de perturbation
            wind_analysis: Analyse des patterns de vent
            
        Returns:
            Classification de la perturbation
        """
        # Règles de classification
        max_wind = wind_analysis['max_wind_speed']
        mean_wind = wind_analysis['mean_wind_speed']
        wind_events = wind_analysis['wind_events']
        high_wind_days = wind_analysis['high_wind_days']
        
        # Score de probabilité vent
        wind_score = 0
        
        # Règle 1: Vent maximum élevé
        if max_wind > self.wind_threshold * 1.5:
            wind_score += 3
        elif max_wind > self.wind_threshold:
            wind_score += 2
        
        # Règle 2: Vent moyen élevé
        if mean_wind > self.wind_threshold * 0.8:
            wind_score += 2
        elif mean_wind > self.wind_threshold * 0.5:
            wind_score += 1
        
        # Règle 3: Nombre d'événements de vent
        if wind_events > 3:
            wind_score += 2
        elif wind_events > 1:
            wind_score += 1
        
        # Règle 4: Jours de vent fort
        if high_wind_days > 5:
            wind_score += 2
        elif high_wind_days > 2:
            wind_score += 1
        
        # Classification finale
        if wind_score >= 5:
            disturbance_type = "wind"
            confidence = min(0.9, wind_score / 8.0)
        elif wind_score >= 2:
            disturbance_type = "mixed"
            confidence = wind_score / 8.0
        else:
            disturbance_type = "bark_beetle"
            confidence = min(0.9, (8 - wind_score) / 8.0)
        
        return {
            'zone_id': zone['id'],
            'disturbance_type': disturbance_type,
            'confidence': confidence,
            'wind_score': wind_score,
            'wind_analysis': wind_analysis,
            'pixel_count': zone['pixel_count'],
            'date_range': (zone['start_date'], zone['end_date'])
        }
    
    def _summarize_classifications(self, classifications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Résumer les classifications
        
        Args:
            classifications: Liste des classifications
            
        Returns:
            Résumé des classifications
        """
        if not classifications:
            return {
                'total_zones': 0,
                'wind_zones': 0,
                'beetle_zones': 0,
                'mixed_zones': 0,
                'avg_confidence': 0
            }
        
        wind_zones = [c for c in classifications if c['disturbance_type'] == 'wind']
        beetle_zones = [c for c in classifications if c['disturbance_type'] == 'bark_beetle']
        mixed_zones = [c for c in classifications if c['disturbance_type'] == 'mixed']
        
        avg_confidence = np.mean([c['confidence'] for c in classifications])
        
        return {
            'total_zones': len(classifications),
            'wind_zones': len(wind_zones),
            'beetle_zones': len(beetle_zones),
            'mixed_zones': len(mixed_zones),
            'avg_confidence': avg_confidence,
            'wind_percentage': len(wind_zones) / len(classifications) * 100,
            'beetle_percentage': len(beetle_zones) / len(classifications) * 100
        }
