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
conda install scipy
```
Installer le package ForDead_package : 
```bash
pip install git+https://gitlab.com/jbferet/fordead_package.git
```

## Utilisation
La détection du déperissement se fait en trois étapes.
- Le calcul des indices de végétations et des masques
- L'apprentissage par modélisation de l'indice de végétation pixel par pixel à partir des premières dates
- La détection du déperissement par comparaison entre l'indice de végétation prédit par le modèle et l'indice de végétation réel.

### Etape 1 : Main_ComputeMaskedVegetationIndex
L'arborescence nécessaire pour le calcul des indices de végétation et des masques est la suivante :

* Data
    * SENTINEL
        * Tuile1
            * Date1
            * Date2
            * ...
        * Tuile2
        * ...
    * Rasters
        * Tuile1
            * MaskForet_Tuile1.tif (raster binaire (1 pour la foret, en dehors) dont l'extent, la résolution et le CRS correspondent aux bandes SENTINEL à 10m)
        * ...

Le script correspondant est __Main_ComputeMaskedVegetationIndex__ dans __DetectionScolyte__. Une telle arborescence est disponible dans __test__, avec le jeu de donnée test __ZoneTest__.

Il est donc possible de tester ce programme par la commande suivante :
```bash
python Main_ComputeMaskedVegetationIndex.py --InputDirectory CHEMINPERSO/tests/Data/ --OutputDirectory CHEMINPERSO/tests/OutputFordead
```
Il est possible de mettre n'importe quel dossier en sortie. Le dossier OutputFordead dans __tests__ est le résultat de ce script.

### Etape 2 : Main_TrainForDead
L'étape d'apprentissage prend en entrée un dossier avec l'arborescence suivante:
* VegetationIndex 
    * VegetationIndex_YYYY_MM_JJ.tif
    * ...
* Mask
    * Mask_YYYY_MM_JJ.tif
    * ...

Un tel dossier est disponible dans __tests__ sous le nom __OutputFordead__
