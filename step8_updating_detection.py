#!/usr/bin/env python3
"""
Script pour l'étape 8: Updating detection
Ce script met à jour la détection de dépérissement en ajoutant de nouvelles
acquisitions Sentinel-2 et en relançant le workflow complet.
"""

import shutil
from pathlib import Path
from fordead.steps.step1_compute_masked_vegetationindex import compute_masked_vegetationindex
from fordead.steps.step2_train_model import train_model
from fordead.steps.step3_dieback_detection import dieback_detection
from fordead.steps.step4_compute_forest_mask import compute_forest_mask
from fordead.steps.step5_export_results import export_results
from fordead.visualisation.create_timelapse import create_timelapse
from fordead.visualisation.vi_series_visualisation import vi_series_visualisation

def backup_results():
    """Sauvegarde les résultats actuels"""
    print("=== SAUVEGARDE DES RÉSULTATS ACTUELS ===")
    
    source_dir = Path("tuto_output")
    backup_dir = Path("tuto_output_backup")
    
    if source_dir.exists():
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        shutil.copytree(source_dir, backup_dir)
        print(f"✅ Résultats sauvegardés dans: {backup_dir}")
        return True
    else:
        print("❌ Aucun résultat à sauvegarder")
        return False

def update_data():
    """Met à jour les données avec de nouvelles acquisitions"""
    print("\n=== MISE À JOUR DES DONNÉES ===")
    
    source_dir = Path("fordead_data-main/fordead_data-main/sentinel_data/dieback_detection_tutorial/update_study_area")
    target_dir = Path("fordead_data-main/fordead_data-main/sentinel_data/dieback_detection_tutorial/study_area")
    
    if not source_dir.exists():
        print(f"❌ Dossier source non trouvé: {source_dir}")
        return False
    
    # Compter les nouvelles acquisitions
    new_acquisitions = list(source_dir.glob("SENTINEL*"))
    print(f"📊 Nouvelles acquisitions trouvées: {len(new_acquisitions)}")
    
    # Afficher quelques exemples
    print("Exemples de nouvelles acquisitions:")
    for i, acq in enumerate(sorted(new_acquisitions)[:5]):
        print(f"  {i+1}. {acq.name}")
    if len(new_acquisitions) > 5:
        print(f"  ... et {len(new_acquisitions) - 5} autres")
    
    # Copier les nouvelles acquisitions
    print(f"\n📁 Copie des nouvelles acquisitions vers: {target_dir}")
    for acq in new_acquisitions:
        target_path = target_dir / acq.name
        if not target_path.exists():
            shutil.copytree(acq, target_path)
            print(f"  ✅ Copié: {acq.name}")
        else:
            print(f"  ⚠️  Existe déjà: {acq.name}")
    
    print(f"✅ Mise à jour terminée: {len(new_acquisitions)} acquisitions ajoutées")
    return True

def run_complete_workflow():
    """Exécute le workflow complet avec les données mises à jour"""
    print("\n=== EXÉCUTION DU WORKFLOW COMPLET ===")
    
    input_directory = "fordead_data-main/fordead_data-main/sentinel_data/dieback_detection_tutorial/study_area"
    data_directory = "tuto_output"
    
    print(f"Répertoire d'entrée: {input_directory}")
    print(f"Répertoire de sortie: {data_directory}")
    print()
    
    try:
        # Étape 1: Calcul des indices de végétation masqués
        print("🔄 Étape 1: Calcul des indices de végétation masqués...")
        compute_masked_vegetationindex(
            input_directory=input_directory,
            data_directory=data_directory,
            lim_perc_cloud=0.4,
            interpolation_order=0,
            sentinel_source="THEIA",
            soil_detection=False,
            formula_mask="B2 > 600",
            vi="CRSWIR",
            apply_source_mask=True
        )
        print("✅ Étape 1 terminée")
        
        # Étape 2: Entraînement du modèle harmonique
        print("\n🔄 Étape 2: Entraînement du modèle harmonique...")
        train_model(
            data_directory=data_directory,
            nb_min_date=10,
            min_last_date_training="2018-01-01",
            max_last_date_training="2018-06-01"
        )
        print("✅ Étape 2 terminée")
        
        # Étape 3: Détection des anomalies
        print("\n🔄 Étape 3: Détection des anomalies...")
        dieback_detection(
            data_directory=data_directory,
            threshold_anomaly=0.16,
            stress_index_mode="weighted_mean"
        )
        print("✅ Étape 3 terminée")
        
        # Étape 4: Calcul du masque forestier
        print("\n🔄 Étape 4: Calcul du masque forestier...")
        compute_forest_mask(
            data_directory,
            forest_mask_source="vector",
            vector_path="fordead_data-main/fordead_data-main/vector/area_interest.shp"
        )
        print("✅ Étape 4 terminée")
        
        # Étape 5: Export des résultats
        print("\n🔄 Étape 5: Export des résultats...")
        export_results(
            data_directory=data_directory,
            frequency="M",
            multiple_files=False,
            conf_threshold_list=[0.265],
            conf_classes_list=["Low anomaly", "Severe anomaly"]
        )
        print("✅ Étape 5 terminée")
        
        # Étape 6: Création du timelapse
        print("\n🔄 Étape 6: Création du timelapse...")
        create_timelapse(
            data_directory=data_directory,
            x=643069,
            y=5452565,
            buffer=1500
        )
        print("✅ Étape 6 terminée")
        
        # Étape 7: Création des graphiques
        print("\n🔄 Étape 7: Création des graphiques...")
        vi_series_visualisation(
            data_directory=data_directory,
            shape_path="fordead_data-main/fordead_data-main/vector/points_for_graphs.shp",
            name_column="id",
            ymin=0,
            ymax=2,
            chunks=100
        )
        print("✅ Étape 7 terminée")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution du workflow: {e}")
        return False

def main():
    print("=== ÉTAPE 8: UPDATING DETECTION ===")
    print("Mise à jour de la détection de dépérissement avec de nouvelles données")
    print()
    
    # 1. Sauvegarder les résultats actuels
    if not backup_results():
        return False
    
    # 2. Mettre à jour les données
    if not update_data():
        return False
    
    # 3. Exécuter le workflow complet
    if not run_complete_workflow():
        return False
    
    print("\n🎉 MISE À JOUR TERMINÉE AVEC SUCCÈS!")
    print("📊 Nouvelles données intégrées dans le workflow")
    print("📁 Résultats précédents sauvegardés dans: tuto_output_backup")
    print("📁 Nouveaux résultats dans: tuto_output")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎯 Workflow fordead mis à jour avec succès!")
    else:
        print("\n💥 Échec de la mise à jour")
