# Accès à Microsoft Planetary Computer

## 1. Modules Python ajoutés

3 modules sont ajoutés pour permettre l'accès aux données de Microsoft Planetary Computer (MPC):

- pystac : module pour gérer les objets STAC
- pystac_client: module pour interroger des catalogues STAC
- planetary_computer: API d'accès au catalogue MPC

## 2. Fonctions modifiées

- fichier `extract_reflectance.py`
    - `extract_reflectance(...)`

- fichier `obs_to_s2_grid.py`
    - `obs_to_s2_grid(...)`

- fichier `validation_module.py` -> `validation_stac_module.py`
    - `get_grid_points(...)`
    - `get_sen_obs_intersection(...)`
    - `get_reflectance_at_points(...)`
    - `extract_raster_values(...)`
    - `get_polygons_from_sentinel_planetComp(...)` [NEW]

- fichier `stac_module.py` [NEW]

## 3. Pour tester 

Pour tester, lancer le script `test_main.py`
n.b. Modifier les chemins d'accès aux fichiers.
