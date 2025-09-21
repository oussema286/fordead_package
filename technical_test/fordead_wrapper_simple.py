#!/usr/bin/env python3
"""
Wrapper simplifié pour intégrer fordead dans le pipeline technique
"""

import logging
from typing import Dict, Any, Optional
import numpy as np
import xarray as xr
from pathlib import Path
import tempfile
import shutil

class FordeadWrapperSimple:
    """
    Wrapper simplifié pour intégrer fordead dans le pipeline technique
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialiser le wrapper fordead
        
        Args:
            config: Configuration du pipeline
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Paramètres fordead
        self.fordead_config = config['fordead']
        
        # Répertoires temporaires
        self.temp_dir = Path(tempfile.mkdtemp(prefix='fordead_technical_test_'))
        self.logger.info(f"Répertoire temporaire fordead: {self.temp_dir}")
    
    def run_pipeline(self, sentinel_data: xr.Dataset) -> Dict[str, Any]:
        """
        Exécuter le pipeline fordead simplifié
        
        Args:
            sentinel_data: Dataset Sentinel-2 traité
            
        Returns:
            Résultats du pipeline fordead
        """
        self.logger.info("Début de l'exécution du pipeline fordead simplifié")
        
        try:
            # 1. Calculer les indices de végétation
            vegetation_indices = self._compute_vegetation_indices(sentinel_data)
            
            # 2. Simuler la détection d'anomalies
            anomalies = self._simulate_anomaly_detection(vegetation_indices)
            
            # 3. Simuler le masque forestier
            forest_mask = self._simulate_forest_mask(sentinel_data)
            
            # 4. Créer les résultats
            results = {
                'vegetation_index': vegetation_indices,
                'anomalies': anomalies,
                'forest_mask': forest_mask,
                'detection_summary': {
                    'total_pixels': int(vegetation_indices.size),
                    'anomaly_pixels': int(np.sum(anomalies)),
                    'forest_pixels': int(np.sum(forest_mask))
                }
            }
            
            self.logger.info("Pipeline fordead simplifié exécuté avec succès")
            return results
            
        except Exception as e:
            self.logger.error(f"Erreur dans le pipeline fordead: {e}")
            raise
        finally:
            # Nettoyer le répertoire temporaire
            self._cleanup()
    
    def _compute_vegetation_indices(self, sentinel_data: xr.Dataset) -> xr.DataArray:
        """
        Calculer les indices de végétation
        
        Args:
            sentinel_data: Dataset Sentinel-2
            
        Returns:
            DataArray avec les indices de végétation
        """
        self.logger.info("Calcul des indices de végétation")
        
        # Utiliser l'indice configuré
        vi_name = self.fordead_config['vi']
        
        if vi_name == 'CRSWIR':
            vi_data = (sentinel_data['B08'] - sentinel_data['B11']) / (sentinel_data['B08'] + sentinel_data['B11'])
        elif vi_name == 'NDVI':
            vi_data = (sentinel_data['B08'] - sentinel_data['B04']) / (sentinel_data['B08'] + sentinel_data['B04'])
        else:
            # Utiliser CRSWIR par défaut
            vi_data = (sentinel_data['B08'] - sentinel_data['B11']) / (sentinel_data['B08'] + sentinel_data['B11'])
        
        return vi_data
    
    def _simulate_anomaly_detection(self, vi_data: xr.DataArray) -> np.ndarray:
        """
        Simuler la détection d'anomalies
        
        Args:
            vi_data: Indices de végétation
            
        Returns:
            Array booléen des anomalies
        """
        self.logger.info("Simulation de la détection d'anomalies")
        
        # Calculer la moyenne temporelle
        vi_mean = vi_data.mean(dim='time')
        
        # Calculer l'écart-type temporel
        vi_std = vi_data.std(dim='time')
        
        # Seuil d'anomalie
        threshold = self.fordead_config['threshold_anomaly']
        
        # Détecter les anomalies (valeurs < moyenne - seuil * écart-type)
        anomalies = vi_data < (vi_mean - threshold * vi_std)
        
        # Compter les anomalies par pixel
        anomaly_count = anomalies.sum(dim='time')
        
        # Seuil de détection (au moins 3 anomalies)
        detected_anomalies = anomaly_count >= 3
        
        return detected_anomalies.values
    
    def _simulate_forest_mask(self, sentinel_data: xr.Dataset) -> np.ndarray:
        """
        Simuler un masque forestier
        
        Args:
            sentinel_data: Dataset Sentinel-2
            
        Returns:
            Array booléen du masque forestier
        """
        self.logger.info("Simulation du masque forestier")
        
        # Utiliser NDVI pour simuler le masque forestier
        ndvi = (sentinel_data['B08'] - sentinel_data['B04']) / (sentinel_data['B08'] + sentinel_data['B04'])
        ndvi_mean = ndvi.mean(dim='time')
        
        # Seuil forestier (NDVI > 0.3)
        forest_mask = ndvi_mean > 0.3
        
        return forest_mask.values
    
    def _cleanup(self):
        """Nettoyer le répertoire temporaire"""
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                self.logger.info("Répertoire temporaire nettoyé")
        except Exception as e:
            self.logger.warning(f"Erreur lors du nettoyage: {e}")

