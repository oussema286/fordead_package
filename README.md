# ForDead_package

## Installation
### Conda install (recommended)
Depuis un terminal, créer un nouvel environnement avec la commande suivante :

```bash
conda create --name ForDeadEnv python=3.7
```
Activer le nouvel environnement :
```bash
conda activate ForDeadEnv
```
Installer les packages numpy, geopandas, rasterio et scipy avec les commandes suivantes:
```bash
conda install numpy
conda install geopandas
conda install rasterio
conda install xarray
conda install scipy
conda install dask
conda install pathlib
```

Install rioxarray : https://corteva.github.io/rioxarray/stable/installation.html

Depuis l'invite de commande, placer vous dans le répertoire de votre choix et lancez les commandes suivantes :
```bash
git clone https://gitlab.com/jbferet/fordead_package.git
cd fordead_package
pip install .
```

## Utilisation
La détection du déperissement se fait en cinq étapes.
- Le calcul des indices de végétation et des masques pour chaque date SENTINEL-2
- L'apprentissage par modélisation de l'indice de végétation pixel par pixel à partir des premières dates
- La détection du déperissement par comparaison entre l'indice de végétation prédit par le modèle et l'indice de végétation réel
- La création du masque forêt, qui définit les zones d'intérêt
- L'export de sorties permettant de visualiser les résultats au pas de temps souhaité

### Première étape : step1_compute_masked_vegetationindex.py
Cette étape permet le calcul d'indices de végétation et de masques pour chaque date SENTINEL-2

Les paramètres en entrée sont :
- input_directory : le chemin du dossier correspondant à une tuile ou une zone contenant un dossier par date SENTINEL contenant les différentes bandes. Les dossiers doivent contenir la date correspondante dans leur nom sous un des formats suivants : YYYY-MM-DD, YYYY_MM_DD, YYYYMMDD, DD-MM-YYYY, DD_MM_YYYY ou DDMMYYYY. Les fichiers des bandes doivent contenir le nom de la bande correspondante (B2 ou B02, B3 ou B03, etc...).

- data_directory : Le chemin du dossier de sortie, dans lequel seront écrit les indices de végétations et masques

- lim_perc_cloud : Le pourcentage maximum de nuages. Si le pourcentage de nuage de la date SENTINEL, calculé à partir de la classification du fournisseur, est supérieur à ce seuil, la date est ignorée.

- sentinel_source : Source des données parmi 'THEIA' et 'Scihub' et 'PEPS'

- apply_source_mask : Si True, le masque du fournisseur est utilisé dans le calcul du masque de la date.

