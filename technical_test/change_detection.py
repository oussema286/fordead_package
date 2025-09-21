#!/usr/bin/env python3
"""
Module de détection précise des changements avec ruptures
"""

import logging
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import xarray as xr
import pandas as pd
from datetime import datetime, timedelta
import ruptures as rpt
from scipy import stats
import matplotlib.pyplot as plt
from pathlib import Path
import rasterio
from rasterio.transform import from_bounds

class RupturesDetector:
    """
    Classe pour la détection précise des changements avec ruptures
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialiser le détecteur de changements
        
        Args:
            config: Configuration du pipeline
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Paramètres ruptures
        self.model = config['ruptures']['model']
        self.penalty = config['ruptures']['penalty']
        self.min_size = config['ruptures']['min_size']
        
        # Paramètres de détection
        self.vi_name = config['fordead']['vi']  # Nom de l'indice de végétation
        self.threshold = config['fordead']['threshold_anomaly']
    
    def detect_changes(self, vegetation_index_data: xr.DataArray) -> Dict[str, Any]:
        """
        Détecter les changements précis dans les séries temporelles
        
        Args:
            vegetation_index_data: DataArray avec les indices de végétation temporels
            
        Returns:
            Dictionnaire avec les détections de changements
        """
        self.logger.info("Début de la détection précise avec ruptures")
        
        # Extraire les séries temporelles pour chaque pixel
        time_series = self._extract_time_series(vegetation_index_data)
        
        # Détecter les changements pour chaque pixel
        change_points = self._detect_change_points(time_series)
        
        # Analyser les changements détectés
        change_analysis = self._analyze_changes(change_points, time_series)
        
        # Créer les cartes de résultats
        result_maps = self._create_result_maps(change_analysis, vegetation_index_data)
        
        self.logger.info("Détection précise terminée")
        return {
            'change_points': change_points,
            'change_analysis': change_analysis,
            'result_maps': result_maps
        }
    
    def _extract_time_series(self, data: xr.DataArray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extraire les séries temporelles des indices de végétation
        
        Args:
            data: DataArray avec les données temporelles
            
        Returns:
            Tuple (séries temporelles, pixels valides)
        """
        self.logger.info("Extraction des séries temporelles")
        
        # Utiliser directement le DataArray
        vi_data = data
        
        # Reshape pour avoir (pixels, temps)
        if 'time' in vi_data.dims:
            time_series = vi_data.values.reshape(-1, len(vi_data.time))
        else:
            raise ValueError("Dimension 'time' non trouvée dans les données")
        
        # Filtrer les pixels avec des données valides
        valid_pixels = ~np.isnan(time_series).all(axis=1)
        time_series = time_series[valid_pixels]
        
        self.logger.info(f"Séries temporelles extraites: {time_series.shape}")
        return time_series, valid_pixels
    
    def _detect_change_points(self, time_series_data: Tuple[np.ndarray, np.ndarray]) -> List[Dict[str, Any]]:
        """
        Détecter les points de changement pour chaque série temporelle
        
        Args:
            time_series_data: Tuple (séries temporelles, pixels valides)
            
        Returns:
            Liste des détections de changements par pixel
        """
        time_series, valid_pixels = time_series_data
        self.logger.info("Détection des points de changement")
        
        change_points = []
        
        for i, series in enumerate(time_series):
            try:
                # Nettoyer la série temporelle
                clean_series = self._clean_time_series(series)
                
                if len(clean_series) < self.min_size * 2:
                    continue
                
                # Appliquer ruptures
                change_points_pixel = self._apply_ruptures(clean_series)
                
                if change_points_pixel:
                    change_points.append({
                        'pixel_index': i,
                        'change_points': change_points_pixel,
                        'series_length': len(clean_series)
                    })
                    
            except Exception as e:
                self.logger.warning(f"Erreur pour le pixel {i}: {e}")
                continue
        
        self.logger.info(f"Points de changement détectés pour {len(change_points)} pixels")
        return change_points
    
    def _clean_time_series(self, series: np.ndarray) -> np.ndarray:
        """
        Nettoyer une série temporelle
        
        Args:
            series: Série temporelle brute
            
        Returns:
            Série temporelle nettoyée
        """
        # Remplacer les NaN par interpolation
        valid_mask = ~np.isnan(series)
        
        if not np.any(valid_mask):
            return np.array([])
        
        if np.all(valid_mask):
            return series
        
        # Interpolation linéaire pour les valeurs manquantes
        valid_indices = np.where(valid_mask)[0]
        valid_values = series[valid_mask]
        
        if len(valid_indices) < 2:
            return np.array([])
        
        # Interpolation
        series_clean = np.interp(
            np.arange(len(series)),
            valid_indices,
            valid_values
        )
        
        return series_clean
    
    def _apply_ruptures(self, series: np.ndarray) -> List[int]:
        """
        Appliquer l'algorithme ruptures
        
        Args:
            series: Série temporelle nettoyée
            
        Returns:
            Liste des indices des points de changement
        """
        try:
            # Initialiser le détecteur
            if self.model == 'rbf':
                detector = rpt.KernelCPD(kernel='rbf', min_size=self.min_size)
            elif self.model == 'linear':
                detector = rpt.Pelt(model='rbf', min_size=self.min_size)
            else:
                detector = rpt.Pelt(model='rbf', min_size=self.min_size)
            
            # Détecter les changements
            change_points = detector.fit_predict(series, pen=self.penalty)
            
            # Retourner les indices (sans le dernier élément qui est la fin)
            return change_points[:-1] if len(change_points) > 1 else []
            
        except Exception as e:
            self.logger.warning(f"Erreur ruptures: {e}")
            return []
    
    def _analyze_changes(self, change_points: List[Dict[str, Any]], 
                        time_series_data: Tuple[np.ndarray, np.ndarray]) -> Dict[str, Any]:
        """
        Analyser les changements détectés
        
        Args:
            change_points: Liste des points de changement détectés
            time_series_data: Tuple (séries temporelles, pixels valides)
            
        Returns:
            Analyse des changements
        """
        self.logger.info("Analyse des changements détectés")
        
        time_series, valid_pixels = time_series_data
        
        analysis = {
            'total_pixels_analyzed': len(time_series),
            'pixels_with_changes': len(change_points),
            'change_rate': len(change_points) / len(time_series) if len(time_series) > 0 else 0,
            'change_details': []
        }
        
        for change_info in change_points:
            pixel_idx = change_info['pixel_index']
            change_points_pixel = change_info['change_points']
            series = time_series[pixel_idx]
            
            # Analyser chaque changement
            for cp in change_points_pixel:
                if cp < len(series) - 1:
                    # Calculer l'amplitude du changement
                    before_change = np.mean(series[max(0, cp-3):cp])
                    after_change = np.mean(series[cp:min(len(series), cp+3)])
                    amplitude = abs(after_change - before_change)
                    
                    # Calculer la significativité statistique
                    before_data = series[max(0, cp-3):cp]
                    after_data = series[cp:min(len(series), cp+3)]
                    
                    if len(before_data) > 1 and len(after_data) > 1:
                        try:
                            t_stat, p_value = stats.ttest_ind(before_data, after_data)
                        except:
                            t_stat, p_value = 0, 1
                    else:
                        t_stat, p_value = 0, 1
                    
                    analysis['change_details'].append({
                        'pixel_index': pixel_idx,
                        'change_point': cp,
                        'amplitude': amplitude,
                        't_statistic': t_stat,
                        'p_value': p_value,
                        'before_mean': before_change,
                        'after_mean': after_change,
                        'significant': p_value < 0.05 and amplitude > self.threshold
                    })
        
        # Statistiques globales
        significant_changes = [c for c in analysis['change_details'] if c['significant']]
        analysis['significant_changes'] = len(significant_changes)
        analysis['significance_rate'] = len(significant_changes) / len(analysis['change_details']) if analysis['change_details'] else 0
        
        self.logger.info(f"Analyse terminée: {analysis['significant_changes']} changements significatifs")
        return analysis
    
    def _create_result_maps(self, change_analysis: Dict[str, Any], 
                           original_data: xr.DataArray) -> Dict[str, np.ndarray]:
        """
        Créer les cartes de résultats
        
        Args:
            change_analysis: Analyse des changements
            original_data: Données originales pour les dimensions
            
        Returns:
            Dictionnaire avec les cartes de résultats
        """
        self.logger.info("Création des cartes de résultats")
        
        # Dimensions de l'image
        if 'y' in original_data.dims and 'x' in original_data.dims:
            height, width = len(original_data.y), len(original_data.x)
        else:
            # Dimensions par défaut
            height, width = 300, 432
        
        # Cartes de résultats
        result_maps = {
            'change_count': np.zeros((height, width)),
            'first_change': np.full((height, width), -1),
            'last_change': np.full((height, width), -1),
            'max_amplitude': np.zeros((height, width)),
            'significant_changes': np.zeros((height, width))
        }
        
        # Remplir les cartes avec les détections
        for change_detail in change_analysis['change_details']:
            pixel_idx = change_detail['pixel_index']
            
            # Convertir l'index linéaire en coordonnées 2D
            y, x = divmod(pixel_idx, width)
            
            if y < height and x < width:
                # Compter les changements
                result_maps['change_count'][y, x] += 1
                
                # Premier et dernier changement
                if result_maps['first_change'][y, x] == -1:
                    result_maps['first_change'][y, x] = change_detail['change_point']
                result_maps['last_change'][y, x] = change_detail['change_point']
                
                # Amplitude maximale
                result_maps['max_amplitude'][y, x] = max(
                    result_maps['max_amplitude'][y, x],
                    change_detail['amplitude']
                )
                
                # Changements significatifs
                if change_detail['significant']:
                    result_maps['significant_changes'][y, x] += 1
        
        return result_maps
    
    def save_results(self, results: Dict[str, Any], output_dir: Path):
        """
        Sauvegarder les résultats
        
        Args:
            results: Résultats de la détection
            output_dir: Répertoire de sortie
        """
        self.logger.info("Sauvegarde des résultats")
        
        # Sauvegarder les cartes de résultats
        result_maps = results['result_maps']
        
        for map_name, map_data in result_maps.items():
            output_file = output_dir / f'ruptures_{map_name}.tif'
            
            # Créer un fichier GeoTIFF simple
            with rasterio.open(
                output_file, 'w',
                driver='GTiff',
                height=map_data.shape[0],
                width=map_data.shape[1],
                count=1,
                dtype=map_data.dtype,
                crs='EPSG:4326',
                transform=rasterio.transform.from_bounds(
                    -180, -90, 180, 90, map_data.shape[1], map_data.shape[0]
                )
            ) as dst:
                dst.write(map_data, 1)
        
        # Sauvegarder l'analyse détaillée
        analysis_file = output_dir / 'ruptures_analysis.json'
        import json
        
        # Convertir les numpy arrays en listes pour JSON
        analysis_serializable = {}
        for key, value in results['change_analysis'].items():
            if key == 'change_details':
                # Convertir les détails de changement
                details_serializable = []
                for detail in value:
                    detail_serializable = {}
                    for k, v in detail.items():
                        if isinstance(v, np.integer):
                            detail_serializable[k] = int(v)
                        elif isinstance(v, np.floating):
                            detail_serializable[k] = float(v)
                        elif isinstance(v, np.bool_):
                            detail_serializable[k] = bool(v)
                        elif isinstance(v, np.ndarray):
                            detail_serializable[k] = v.tolist()
                        else:
                            detail_serializable[k] = v
                    details_serializable.append(detail_serializable)
                analysis_serializable[key] = details_serializable
            else:
                if isinstance(value, np.integer):
                    analysis_serializable[key] = int(value)
                elif isinstance(value, np.floating):
                    analysis_serializable[key] = float(value)
                elif isinstance(value, np.bool_):
                    analysis_serializable[key] = bool(value)
                elif isinstance(value, np.ndarray):
                    analysis_serializable[key] = value.tolist()
                else:
                    analysis_serializable[key] = value
        
        with open(analysis_file, 'w') as f:
            json.dump(analysis_serializable, f, indent=2)
        
        self.logger.info(f"Résultats sauvegardés dans: {output_dir}")
