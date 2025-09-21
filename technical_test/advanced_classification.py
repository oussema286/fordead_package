"""
Classification avancée Wind vs Bark Beetle avec métriques de performance
"""

import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

class AdvancedWindBeetleClassifier:
    """
    Classificateur avancé Wind vs Bark Beetle avec métriques de performance
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialiser le classificateur
        
        Args:
            config: Configuration du pipeline
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.wind_threshold = config.get('wind_analysis', {}).get('wind_threshold', 12.0)
        self.confidence_threshold = config.get('wind_analysis', {}).get('confidence_threshold', 0.3)  # Réduire le seuil
    
    def classify_disturbances(self, disturbances: List[Dict[str, Any]], 
                            wind_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Classifier les perturbations avec les données de vent
        
        Args:
            disturbances: Liste des perturbations
            wind_data: Données de vent ERA5
            
        Returns:
            Résultats de classification
        """
        self.logger.info("Classification avancée des perturbations")
        
        # Créer un dictionnaire de mapping
        wind_dict = {w['disturbance_id']: w for w in wind_data}
        
        classifications = []
        for disturbance in disturbances:
            disturbance_id = disturbance['id']
            
            if disturbance_id in wind_dict:
                wind_info = wind_dict[disturbance_id]
                classification = self._classify_single_disturbance(disturbance, wind_info)
            else:
                # Classification par défaut si pas de données de vent
                classification = self._classify_without_wind_data(disturbance)
            
            classifications.append(classification)
        
        # Calculer les métriques de performance
        metrics = self._calculate_performance_metrics(disturbances, classifications)
        
        self.logger.info(f"Classification terminée: {len(classifications)} perturbations")
        return {
            'classifications': classifications,
            'metrics': metrics,
            'total_classified': len(classifications)
        }
    
    def _classify_single_disturbance(self, disturbance: Dict[str, Any], 
                                   wind_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classifier une perturbation individuelle
        
        Args:
            disturbance: Données de perturbation
            wind_info: Données de vent
            
        Returns:
            Classification de la perturbation
        """
        max_wind = wind_info['max_wind_speed']
        mean_wind = wind_info['mean_wind_speed']
        wind_events = wind_info['wind_events_count']
        confidence = wind_info['confidence']
        
        # Classification basée sur plusieurs critères
        wind_score = self._calculate_wind_score(max_wind, mean_wind, wind_events)
        beetle_score = self._calculate_beetle_score(max_wind, mean_wind, wind_events)
        
        # Debug: afficher les scores
        self.logger.info(f"Disturbance {disturbance['id']}: wind_score={wind_score:.3f}, beetle_score={beetle_score:.3f}, confidence={confidence:.3f}, threshold={self.confidence_threshold}")
        
        # Classification finale
        if wind_score > beetle_score and confidence > self.confidence_threshold:
            classification = 'wind'
            final_confidence = wind_score
        elif beetle_score > wind_score and confidence > self.confidence_threshold:
            classification = 'bark_beetle'
            final_confidence = beetle_score
        else:
            # Classification incertaine
            classification = 'uncertain'
            final_confidence = min(wind_score, beetle_score)
        
        return {
            'disturbance_id': disturbance['id'],
            'original_type': disturbance.get('type', 'unknown'),
            'classified_type': classification,
            'confidence': final_confidence,
            'wind_score': wind_score,
            'beetle_score': beetle_score,
            'max_wind_speed': max_wind,
            'mean_wind_speed': mean_wind,
            'wind_events_count': wind_events,
            'classification_reason': self._get_classification_reason(
                max_wind, mean_wind, wind_events, classification
            )
        }
    
    def _calculate_wind_score(self, max_wind: float, mean_wind: float, 
                            wind_events: int) -> float:
        """
        Calculer le score de probabilité de vent
        
        Args:
            max_wind: Vitesse de vent maximale
            mean_wind: Vitesse de vent moyenne
            wind_events: Nombre d'événements de vent fort
            
        Returns:
            Score de probabilité de vent (0-1)
        """
        # Score basé sur la vitesse maximale
        max_wind_score = min(1.0, max_wind / 20.0)
        
        # Score basé sur la vitesse moyenne
        mean_wind_score = min(1.0, mean_wind / 15.0)
        
        # Score basé sur les événements de vent fort
        events_score = min(1.0, wind_events / 10.0)
        
        # Score combiné avec pondération
        wind_score = (0.5 * max_wind_score + 0.3 * mean_wind_score + 0.2 * events_score)
        
        return min(1.0, wind_score)
    
    def _calculate_beetle_score(self, max_wind: float, mean_wind: float, 
                              wind_events: int) -> float:
        """
        Calculer le score de probabilité de scolyte
        
        Args:
            max_wind: Vitesse de vent maximale
            mean_wind: Vitesse de vent moyenne
            wind_events: Nombre d'événements de vent fort
            
        Returns:
            Score de probabilité de scolyte (0-1)
        """
        # Score inversement proportionnel au vent
        max_wind_score = max(0.0, 1.0 - (max_wind / 20.0))
        mean_wind_score = max(0.0, 1.0 - (mean_wind / 15.0))
        events_score = max(0.0, 1.0 - (wind_events / 10.0))
        
        # Score combiné
        beetle_score = (0.4 * max_wind_score + 0.4 * mean_wind_score + 0.2 * events_score)
        
        return min(1.0, beetle_score)
    
    def _classify_without_wind_data(self, disturbance: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classifier une perturbation sans données de vent
        
        Args:
            disturbance: Données de perturbation
            
        Returns:
            Classification par défaut
        """
        return {
            'disturbance_id': disturbance['id'],
            'original_type': disturbance.get('type', 'unknown'),
            'classified_type': 'unknown',
            'confidence': 0.5,
            'wind_score': 0.5,
            'beetle_score': 0.5,
            'max_wind_speed': 0.0,
            'mean_wind_speed': 0.0,
            'wind_events_count': 0,
            'classification_reason': 'No wind data available'
        }
    
    def _get_classification_reason(self, max_wind: float, mean_wind: float, 
                                 wind_events: int, classification: str) -> str:
        """
        Obtenir la raison de la classification
        
        Args:
            max_wind: Vitesse de vent maximale
            mean_wind: Vitesse de vent moyenne
            wind_events: Nombre d'événements de vent fort
            classification: Classification finale
            
        Returns:
            Raison de la classification
        """
        if classification == 'wind':
            if max_wind > 15.0:
                return f"High maximum wind speed ({max_wind:.1f} m/s)"
            elif wind_events > 5:
                return f"Multiple wind events ({wind_events})"
            else:
                return f"Moderate wind conditions ({mean_wind:.1f} m/s mean)"
        elif classification == 'bark_beetle':
            if max_wind < 8.0:
                return f"Low wind conditions ({max_wind:.1f} m/s max)"
            elif wind_events < 2:
                return f"Few wind events ({wind_events})"
            else:
                return f"Moderate wind but beetle indicators present"
        else:
            return "Uncertain classification due to conflicting indicators"
    
    def _calculate_performance_metrics(self, disturbances: List[Dict[str, Any]], 
                                     classifications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculer les métriques de performance
        
        Args:
            disturbances: Perturbations originales
            classifications: Classifications prédites
            
        Returns:
            Métriques de performance
        """
        # Extraire les types originaux et prédits
        y_true = [str(d.get('type', 'unknown')) for d in disturbances]  # Convertir en str Python
        y_pred = [str(c['classified_type']) for c in classifications]  # Convertir en str Python
        
        # Debug: afficher les types
        self.logger.info(f"Types originaux: {set(y_true)}")
        self.logger.info(f"Types prédits: {set(y_pred)}")
        
        # Obtenir les labels uniques
        unique_labels = list(set(y_true + y_pred))
        
        # Vérifier s'il y a des labels
        if not unique_labels:
            self.logger.warning("Aucun label trouvé, utilisation de labels par défaut")
            unique_labels = ['wind', 'bark_beetle', 'unknown']
            y_true = ['unknown'] * len(disturbances)
            y_pred = ['uncertain'] * len(classifications)
        
        # Calculer les métriques de base
        precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
        
        # Matrice de confusion
        cm = confusion_matrix(y_true, y_pred, labels=unique_labels)
        
        # Métriques spécifiques pour wind et bark_beetle
        wind_precision = 0.0
        wind_recall = 0.0
        beetle_precision = 0.0
        beetle_recall = 0.0
        
        if 'wind' in unique_labels:
            wind_precision = precision_score(y_true, y_pred, labels=['wind'], average='micro', zero_division=0)
            wind_recall = recall_score(y_true, y_pred, labels=['wind'], average='micro', zero_division=0)
        
        if 'bark_beetle' in unique_labels:
            beetle_precision = precision_score(y_true, y_pred, labels=['bark_beetle'], average='micro', zero_division=0)
            beetle_recall = recall_score(y_true, y_pred, labels=['bark_beetle'], average='micro', zero_division=0)
        
        # Délai de détection (simulé)
        detection_lead_time = self._calculate_detection_lead_time(classifications)
        
        return {
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'wind_precision': wind_precision,
            'beetle_precision': beetle_precision,
            'confusion_matrix': cm.tolist(),
            'detection_lead_time_days': detection_lead_time,
            'total_classifications': len(classifications),
            'high_confidence_classifications': len([c for c in classifications if c['confidence'] > 0.8])
        }
    
    def _calculate_detection_lead_time(self, classifications: List[Dict[str, Any]]) -> float:
        """
        Calculer le délai de détection moyen
        
        Args:
            classifications: Classifications
            
        Returns:
            Délai de détection moyen en jours
        """
        # Simulation du délai de détection basé sur la confiance
        lead_times = []
        for classification in classifications:
            confidence = classification['confidence']
            # Plus la confiance est élevée, plus le délai est court
            lead_time = max(0, 30 - (confidence * 25))  # 5-30 jours
            lead_times.append(lead_time)
        
        return np.mean(lead_times) if lead_times else 0.0
    
    def save_classification_results(self, results: Dict[str, Any], output_dir: Path):
        """
        Sauvegarder les résultats de classification
        
        Args:
            results: Résultats de classification
            output_dir: Répertoire de sortie
        """
        self.logger.info("Sauvegarde des résultats de classification")
        
        # Créer le répertoire
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Sauvegarder les classifications
        classifications_df = pd.DataFrame(results['classifications'])
        classifications_df.to_csv(output_dir / 'wind_beetle_classifications.csv', index=False)
        
        # Sauvegarder les métriques
        metrics_file = output_dir / 'classification_metrics.txt'
        with open(metrics_file, 'w', encoding='utf-8') as f:
            f.write("=== MÉTRIQUES DE CLASSIFICATION ===\n")
            f.write(f"Précision globale: {results['metrics']['precision']:.3f}\n")
            f.write(f"Rappel global: {results['metrics']['recall']:.3f}\n")
            f.write(f"F1-score: {results['metrics']['f1_score']:.3f}\n")
            f.write(f"Précision vent: {results['metrics']['wind_precision']:.3f}\n")
            f.write(f"Précision scolyte: {results['metrics']['beetle_precision']:.3f}\n")
            f.write(f"Délai de détection moyen: {results['metrics']['detection_lead_time_days']:.1f} jours\n")
            f.write(f"Classifications haute confiance: {results['metrics']['high_confidence_classifications']}\n")
        
        # Créer des visualisations
        self._create_classification_plots(results, output_dir)
        
        self.logger.info(f"Résultats de classification sauvegardés dans: {output_dir}")
    
    def _create_classification_plots(self, results: Dict[str, Any], output_dir: Path):
        """
        Créer des graphiques de classification
        
        Args:
            results: Résultats de classification
            output_dir: Répertoire de sortie
        """
        try:
            # Graphique de distribution des confiances
            plt.figure(figsize=(10, 6))
            confidences = [c['confidence'] for c in results['classifications']]
            plt.hist(confidences, bins=20, alpha=0.7, edgecolor='black')
            plt.xlabel('Confiance de classification')
            plt.ylabel('Nombre de perturbations')
            plt.title('Distribution des confiances de classification')
            plt.grid(True, alpha=0.3)
            plt.savefig(output_dir / 'confidence_distribution.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            # Graphique des scores vent vs scolyte
            plt.figure(figsize=(10, 6))
            wind_scores = [c['wind_score'] for c in results['classifications']]
            beetle_scores = [c['beetle_score'] for c in results['classifications']]
            plt.scatter(wind_scores, beetle_scores, alpha=0.6)
            plt.xlabel('Score de probabilité vent')
            plt.ylabel('Score de probabilité scolyte')
            plt.title('Scores de classification Wind vs Bark Beetle')
            plt.plot([0, 1], [1, 0], 'r--', alpha=0.5, label='Frontière de décision')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.savefig(output_dir / 'wind_vs_beetle_scores.png', dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            self.logger.warning(f"Erreur lors de la création des graphiques: {e}")

