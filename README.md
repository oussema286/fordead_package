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
- **input_directory** : le chemin du dossier correspondant à une tuile ou une zone contenant un dossier par date SENTINEL contenant les différentes bandes. Les dossiers doivent contenir la date correspondante dans leur nom sous un des formats suivants : YYYY-MM-DD, YYYY_MM_DD, YYYYMMDD, DD-MM-YYYY, DD_MM_YYYY ou DDMMYYYY. Les fichiers des bandes doivent contenir le nom de la bande correspondante (B2 ou B02, B3 ou B03, etc...).
- **data_directory** : Le chemin du dossier de sortie, dans lequel seront écrit les indices de végétations et masques
- **lim_perc_cloud** : Le pourcentage maximum de nuages. Si le pourcentage de nuage de la date SENTINEL, calculé à partir de la classification du fournisseur, est supérieur à ce seuil, la date est ignorée.
- **interpolation_order** : Ordre d'interpolation pour le passage des bandes de 20m de résolution à 10m. 0 : plus proche voisin, 1 : linéaire, 2 : bilinéaire, 3 : cubique
- **sentinel_source** : Source des données parmi 'THEIA' et 'Scihub' et 'PEPS'
- **apply_source_mask** : Si True, le masque du fournisseur est utilisé dans le calcul du masque de la date.
- **vi** : Indice de végétation utilisé
- **extent_shape_path** : Chemin d'un shapefile contenant un polygone utilisé pour restreindre les calculs à une zone. Si non renseigné, le calcul est appliqué à l'ensemble de la tuile

Note : **input_directory** et **data_directory** n'ont pas de valeur par défaut et doivent absolument être renseignés. **sentinel_source** doit correspondre au fournisseur de vos données. Le package a presque exclusivement été testé à partir des données THEIA.

Les sorties de cette première étape, dans le dossier data_directory, sont :
- Un fichier TileInfo qui contient les informations relatives à la zone étudiée, dates utilisées, chemins des rasters... Il est importé par les étapes suivantes pour réutilisation de ces informations.
- Dans le dossier **VegetationIndex**, un raster pour chaque date où l'indice de végétation est calculé pour chaque pixel
- Dans le dossier **Mask**, un raster binaire pour chaque date où les pixels masqués valent 1, et les pixels valides 0.
- Dans le dossier **DataSoil**, trois rasters :
    - **count_soil** : le nombre de dates successives avec des anomalies de sol
    - **first_date_soil** : L'index de la première date avec une anomalie de sol de la dernière série d'anomalies de sol
    - **state_soil** : Un raster binaire qui vaut 1 si le pixel est détecté comme sol (Au moins trois anomalies de sol successives)
A partir de state_soil et first_date_soil, il est donc possible de savoir quels pixels sont détectés comme sol nu/coupe, et à partir de quelle date. count_soil permet de mettre à jour ces données en ajoutant de nouvelles dates SENTINEL.

### Deuxième étape : step2_TrainFordead.py
Cette étape permet le calcul d'un modèle à partir des premières dates SENTINEL, considérées comme représentatives du comportement saisonnier normal de l'indice de végétation. Ce modèle permet de prédire la valeur de l'indice de végétation à n'importe quelle date.

Les paramètres en entrée sont :
- **data_directory** : Le chemin du dossier de sortie dans lequel sera écrit les coefficients du modèle.
- **nb_min_date** : Nombre minimum de dates valides pour calculer un modèle
- **min_last_date_training** : Date à partir de laquelle les dates SENTINEL ne sont plus utilisées pour l'apprentissage, tant qu'il y a au moins nb_min_date dates valides pour le pixel
- **max_last_date_training** : Date jusqu'à laquelle les dates SENTINEL peuvent être utilisées pour l'apprentissage afin d'atteindre le nombre de nb_min_date dates valides
- **path_vi** : Chemin du dossier contenant un raster pour chaque date où l'indice de végétation est calculé pour chaque pixel. Inutile de le renseigner si les informations proviennent de l'étape 1, auquel cas le chemin est contenu dans le fichier TileInfo.
- **path_masks** : Chemin du dossier contenant un raster binaire pour chaque date où les pixels masqués valent 1, et les pixels valides 0. Inutile de le renseigner si les informations proviennent de l'étape 1, auquel cas le chemin est contenu dans le fichier TileInfo.

Les coefficients du modèle sont calculés pour chaque pixel. Pour chaque pixel, uniquement les dates non masquées sont utilisées. Si il y a nb_min_date dates valides à la date max_last_date_training, l'apprentissage s'arrête à cette date. Si le nombre de date de dates valides atteint nb_min_date entre à une date située entre min_last_date_training et max_last_date_training, l'apprentissage s'arrête à cette date. Si le nombre de date de dates valides n'atteint pas nb_min_date à la date max_last_date_training, le pixel est sorti de l'étude et ne sera pas associé à un modèle.
Cette méthode permet, dans le cas d'une crise sanitaire relativement ancienne comme le scolyte, de commencer la détection dès 2018 si l'on dispose de suffisamment de dates valides au début de l'année, tout permettant l'étude de pixels dans des situations de détection plus délicates simplement en réalisant l'apprentissage sur une période plus longue pour récupérer d'autres dates valides. Il parait difficile de terminer l'apprentissage avant 2018, car le modèle périodique étant annuel, l'utilisation d'au moins deux ans de données SENTINEL-2 parait obligatoire.

Les sorties de cette première étape, dans le dossier data_directory, sont :
- Dans le dossier **DataModel**, deux fichiers :
    - **first_detection_date_index.tif**, un raster qui contient l'index de la première date qui sera utilisée pour la détection de déperissement. Il permet de savoir pour chaque pixel quelles dates ont été utilisées pour l'apprentissage et lesquelles sont utilisées pour la détection.
    - **coeff_model.tif**, un stack à 5 bandes, une pour chaque coefficient du modèle de l'indice de végétation.
- Dans le dossier **ForestMask**, le raster binaire **valid_area_mask.tif** qui vaut 1 pour les pixels où le modèle a pu être calculé, 0 si il n'y avait pas assez de dates valides
- Le fichier TileInfo est mis à jour.

### Troisième étape : step3_DetectionFordead.py

