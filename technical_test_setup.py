#!/usr/bin/env python3
"""
Script de configuration pour le Technical Test
Early Bark Beetle Detection with Sentinel Data
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Installer les dépendances requises"""
    print("🔧 Installation des dépendances pour le Technical Test...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements_technical_test.txt"
        ])
        print("✅ Dépendances installées avec succès!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'installation: {e}")
        return False

def setup_directories():
    """Créer la structure de répertoires"""
    print("📁 Création de la structure de répertoires...")
    
    directories = [
        "technical_test",
        "technical_test/data",
        "technical_test/data/sentinel2",
        "technical_test/data/disturbance_map",
        "technical_test/data/era5",
        "technical_test/results",
        "technical_test/results/detections",
        "technical_test/results/evaluations",
        "technical_test/notebooks",
        "technical_test/configs",
        "technical_test/logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {directory}")
    
    return True

def create_config_template():
    """Créer un template de configuration"""
    print("⚙️ Création du template de configuration...")
    
    config_content = """# Configuration pour le Technical Test
# Early Bark Beetle Detection with Sentinel Data

# Paramètres généraux
project_name: "bark_beetle_detection"
version: "1.0.0"
log_level: "INFO"

# Paramètres de la région d'intérêt
roi:
  # Format: GeoJSON ou GeoPackage
  file_path: "data/roi.geojson"
  # Ou définir directement les coordonnées
  bbox: [6.0, 45.0, 7.0, 46.0]  # [min_lon, min_lat, max_lon, max_lat]
  crs: "EPSG:4326"

# Paramètres temporels
date_range:
  start_date: "2018-01-01"
  end_date: "2025-12-31"
  # Période d'entraînement pour le modèle harmonique
  training_end: "2018-06-01"

# Paramètres Sentinel-2
sentinel2:
  bands: ["B04", "B08", "B11", "B12"]  # Rouge, NIR, SWIR1, SWIR2
  cloud_coverage: 0.4
  resolution: 10
  source: "THEIA"

# Paramètres fordead
fordead:
  vi: "CRSWIR"  # Indice de végétation
  threshold_anomaly: 0.16
  stress_index_mode: "weighted_mean"
  nb_min_date: 10

# Paramètres ruptures
ruptures:
  model: "rbf"  # Modèle de détection de changements
  penalty: 2
  min_size: 5

# Paramètres ERA5
era5:
  # Variables météorologiques
  variables: ["wind_speed_10m", "wind_direction_10m"]
  # Seuil de vent pour différencier vent/scolytes
  wind_threshold: 15.0  # m/s

# Paramètres d'évaluation
evaluation:
  # Données de référence
  disturbance_map_url: "projects/ee-albaviana/assets/disturbance_agent_v211"
  # Métriques à calculer
  metrics: ["precision", "recall", "f1", "lead_time"]
  # Buffer autour des événements de référence
  buffer_distance: 100  # mètres

# Chemins de sortie
output:
  base_path: "results"
  detections: "results/detections"
  evaluations: "results/evaluations"
  visualizations: "results/visualizations"
"""
    
    with open("technical_test/configs/config_template.yaml", "w") as f:
        f.write(config_content)
    
    print("  ✅ Template de configuration créé")
    return True

def create_readme():
    """Créer un README pour le technical test"""
    print("📝 Création du README...")
    
    readme_content = """# Technical Test - Early Bark Beetle Detection with Sentinel Data

## 🎯 Objectif

Développer un pipeline modulaire et robuste pour la détection précoce des perturbations forestières, avec un focus sur les épidémies de scolytes, en réutilisant et améliorant le package fordead existant.

## 🚀 Fonctionnalités Principales

### 1. Pipeline d'Inférence Modulaire
- Réutilisation du package fordead_package
- Interface CLI paramétrable
- Support des ROI (GeoJSON/GeoPackage)
- Gestion des plages de dates

### 2. Ingestion Sentinel-2 avec PhiDown
- Téléchargement automatique des données Sentinel-2 Level 2A
- Sélection des bandes pertinentes (B4, B8, B11, NDVI)
- Construction de stacks temporels nettoyés

### 3. Détection Précise avec ruptures
- Application de ruptures pour affiner le moment exact du changement
- Transformation "cette année a eu une perturbation" → "le changement s'est produit vers le 23 mai"

### 4. Différenciation Vent vs Scolytes (via ERA5)
- Utilisation de l'European Forest Disturbance Map
- Analyse des données ERA5 pour les vitesses de vent maximales
- Heuristique de classification : vent élevé → Vent, vent faible → Scolytes

## 📁 Structure du Projet

```
technical_test/
├── data/                    # Données d'entrée
│   ├── sentinel2/          # Données Sentinel-2 téléchargées
│   ├── disturbance_map/    # Carte des perturbations européennes
│   └── era5/              # Données météorologiques ERA5
├── results/                # Résultats de l'analyse
│   ├── detections/         # Détections de perturbations
│   └── evaluations/        # Métriques d'évaluation
├── notebooks/              # Notebooks de démonstration
├── configs/                # Fichiers de configuration
└── logs/                   # Fichiers de logs
```

## 🛠️ Installation

1. Installer les dépendances :
```bash
pip install -r requirements_technical_test.txt
```

2. Configurer Google Earth Engine :
```bash
earthengine authenticate
```

3. Exécuter le script de configuration :
```bash
python technical_test_setup.py
```

## 🚀 Utilisation

### Pipeline CLI
```bash
python -m technical_test.pipeline --config configs/config.yaml
```

### Notebook de démonstration
```bash
jupyter notebook notebooks/demo_pipeline.ipynb
```

## 📊 Métriques d'Évaluation

- **Précision/Recall** pour les zones probables de scolytes
- **Temps de détection** (lead time)
- **Courbes ROC et PR**
- **Distribution des temps de détection**

## 🔧 Configuration

Voir `configs/config_template.yaml` pour les paramètres disponibles.

## 📈 Résultats Attendus

- Pipeline modulaire et réutilisable
- Détection précise des perturbations
- Différenciation vent/scolytes
- Métriques de performance complètes
- Visualisations interactives

## 🕒 Estimation du Temps

- **Tâches principales** : ~2 jours complets (16-20h)
- **Bonus** : 0.5-1 jour supplémentaire

## 📝 Notes

- Code modulaire et documenté
- Hypothèses clairement documentées
- Méthodologie et visualisations claires
- Réutilisabilité privilégiée sur la nouveauté
"""
    
    with open("technical_test/README.md", "w", encoding='utf-8') as f:
        f.write(readme_content)
    
    print("  ✅ README créé")
    return True

def main():
    """Fonction principale de configuration"""
    print("🎯 CONFIGURATION DU TECHNICAL TEST")
    print("Early Bark Beetle Detection with Sentinel Data")
    print("=" * 50)
    
    # 1. Installer les dépendances
    if not install_requirements():
        return False
    
    # 2. Créer la structure de répertoires
    if not setup_directories():
        return False
    
    # 3. Créer le template de configuration
    if not create_config_template():
        return False
    
    # 4. Créer le README
    if not create_readme():
        return False
    
    print("\n" + "=" * 50)
    print("✅ CONFIGURATION TERMINÉE AVEC SUCCÈS!")
    print("🎯 Prêt pour le Technical Test!")
    print("=" * 50)
    
    print("\n📋 Prochaines étapes :")
    print("1. Configurer Google Earth Engine : earthengine authenticate")
    print("2. Définir votre ROI dans configs/config_template.yaml")
    print("3. Lancer le pipeline : python -m technical_test.pipeline")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Configuration réussie!")
    else:
        print("\n💥 Erreur lors de la configuration")
