## ÉTAPE 2 : Apprentissage par modélisation de l'indice de végétation pixel par pixel à partir des premières dates
Cette étape permet le calcul d'un modèle à partir des premières dates SENTINEL, considérées comme représentatives du comportement saisonnier normal de l'indice de végétation. Ce modèle permet de prédire la valeur de l'indice de végétation à n'importe quelle date.

#### ENTRÉES
Les paramètres en entrée sont :
- **data_directory** : Le chemin du dossier de sortie dans lequel sera écrit les coefficients du modèle.
- **nb_min_date** : Nombre minimum de dates valides pour calculer un modèle
- **min_last_date_training** : Date au format AAAA-MM-JJ à partir de laquelle les dates SENTINEL ne sont plus utilisées pour l'apprentissage, tant qu'il y a au moins nb_min_date dates valides pour le pixel
- **max_last_date_training** : Date au format AAAA-MM-JJ jusqu'à laquelle les dates SENTINEL peuvent être utilisées pour l'apprentissage afin d'atteindre le nombre de nb_min_date dates valides
- **path_vi** : Chemin du dossier contenant un raster pour chaque date où l'indice de végétation est calculé pour chaque pixel. Inutile de le renseigner si les informations proviennent de l'étape 1, auquel cas le chemin est contenu dans le fichier TileInfo.
- **path_masks** : Chemin du dossier contenant un raster binaire pour chaque date où les pixels masqués valent 1, et les pixels valides 0. Inutile de le renseigner si les informations proviennent de l'étape 1, auquel cas le chemin est contenu dans le fichier TileInfo.
- **correct_vi** : Si activé, l'indice de végétation est corrigé à partir de l'indice de végétation médian des pixels d'intérêts non masqués à l'échelle de la zone complète. Si activé, [l'étape de définition de la zone d'intérêt](https://fordead.gitlab.io/fordead_package/docs/user_guides/french/04_compute_forest_mask/) doit donc être réalisée avant cette étape. Cela permet de corriger des effets s'appliquant à l'ensemble du peuplement, non nécessairement liés à un dépérissement.
Les coefficients du modèle sont calculés pour chaque pixel. Pour chaque pixel, uniquement les dates non masquées sont utilisées. Si il y a nb_min_date dates valides à la date max_last_date_training, l'apprentissage s'arrête à cette date. Si le nombre de date de dates valides atteint nb_min_date entre à une date située entre min_last_date_training et max_last_date_training, l'apprentissage s'arrête à cette date. Si le nombre de date de dates valides n'atteint pas nb_min_date à la date max_last_date_training, le pixel est sorti de l'étude et ne sera pas associé à un modèle.
Cette méthode permet, dans le cas d'une crise sanitaire relativement ancienne comme le scolyte, de commencer la détection dès 2018 si l'on dispose de suffisamment de dates valides au début de l'année, tout permettant l'étude de pixels dans des situations de détection plus délicates simplement en réalisant l'apprentissage sur une période plus longue pour récupérer d'autres dates valides. Il parait difficile de terminer l'apprentissage avant 2018, car le modèle périodique étant annuel, l'utilisation d'au moins deux ans de données SENTINEL-2 parait obligatoire.

#### SORTIES
Les sorties de cette deuxième étape, dans le dossier data_directory, sont :
- Dans le dossier **DataModel**, deux fichiers :
    - **first_detection_date_index.tif**, un raster qui contient l'index de la première date qui sera utilisée pour la détection de déperissement. Il permet de savoir pour chaque pixel quelles dates ont été utilisées pour l'apprentissage et lesquelles sont utilisées pour la détection.
    - **coeff_model.tif**, un stack à 5 bandes, une pour chaque coefficient du modèle de l'indice de végétation.
- Dans le dossier **TimelessMasks**, le raster binaire **sufficient_coverage_mask.tif** qui vaut 1 pour les pixels où le modèle a pu être calculé, 0 si il n'y avait pas assez de dates valides
- Le fichier TileInfo est mis à jour.

## Utilisation
### A partir d'un script

```bash
from fordead.steps.step2_train_model import train_model
train_model(data_directory = <data_directory>)
```

### A partir de la ligne de commande

```bash
fordead train_model [OPTIONS]
```

Voir documentation détaillée sur le [site](https://fordead.gitlab.io/fordead_package/docs/cli/#fordead-train_model)

## Détail du fonctionnement

![Diagramme_step2](Diagrams/Diagramme_step2.png "Diagramme_step2")

### Imports des informations sur les traitements précédents et suppression des résultats obsolètes si existants
Avant tout, si la chaîne de traitement a déjà été utilisée sur la zone, les informations relatives à ces calculs sont importés (paramètres, chemins des données, dates utilisées...). Si les paramètres utilisés ont été modifiés, les résultats des calculs antérieurs sont supprimés et recalculés avec les nouveaux paramètres. Il est possible de commencer le traitement à cette étape si des indices de végétations et masques ont déjà été calculés pour chaque date.
> **_Fonctions utilisées :_** [TileInfo()](docs/API_Reference/fordead/import_data/#tileinfo), méthodes de la classe TileInfo [import_info()](docs/API_Reference/fordead/import_data/#import_info), [add_parameters()](docs/API_Reference/fordead/import_data/#add_parameters), [delete_dirs()](docs/API_Reference/fordead/import_data/#delete_dirs)

### Import de l'ensemble des données d'indices de végétation et masques jusqu'à **min_last_date_training**
> **_Fonctions utilisées :_** [import_stackedmaskedVI()](docs/API_Reference/fordead/import_data/#import_stackedmaskedvi)

### (OPTIONNEL - si **correct_vi** vaut True) Correction de l'indice de végétation à partir de l'indice de végétation médian des pixels d'intérêts non masqués à l'échelle de la zone complète
- Masquage des pixels n'appartenant pas à la zone d'intérêt, ou masqués
- Calcul de la médiane de l'indice de végétation de l'ensemble de la zone pour chaque date jusque **max_last_date_training**
- Ajustement d'un modèle harmonique sur ces médianes, ce modèle doit donc rendre compte du comportement normal de l'indice de végétation sur l'ensemble des peuplements d'intérêt de la zone.
- Calcul d'un terme de correction pour chaque date, par différence entre la prédiction du modèle à la date donnée et la médiane calculée correspondante
- Application des termes de corrections de chaque date en l'ajoutant à la valeur de l'indice de végétation de l'ensemble des pixels de la date.
> **_Fonctions utilisées :_** [model_vi_correction()](docs/API_Reference/fordead/model_vegetation_index/#model_vi_correction)

### Détermination des dates utilisées pour l'apprentissage
La date de début de détection peut être différent entre chaque pixels. Pour chaque pixel, l'apprentissage du modèle doit se faire sur au moins **nb_min_date** dates, et au moins sur l'ensemble des dates antérieures à **min_last_date_training**. Si il n'y a pas au moins **nb_min_date** à la date **max_last_date_training**, le pixel est abandonné. Cela permet de commencer la détection au plus tôt si cela est possible, tout en conservant un maximum de pixels en permettant un début de détection plus tardif sur les zones avec moins de dates valides.
> **_Fonctions utilisées :_** [get_detection_dates()](docs/API_Reference/fordead/model_vegetation_index/#get_detection_dates)

### Modélisation du comportement de l'indice de végétation
Pour chaque pixel, un modèle est ajusté sur les dates d'apprentissage. Le modèle utilisé est le suivant :
```math
a1 + b1\sin{\frac{2\pi t}{T}} + b2\cos{\frac{2\pi t}{T}} + b3\sin{\frac{4\pi t}{T}} + b4\cos{\frac{4\pi t}{T}}
```
Cette étape consiste à déterminer les coefficients a1, b1, b2, b3 et b4 pour chaque pixel.
> **_Fonctions utilisées :_** [model_vi()](docs/API_Reference/fordead/model_vegetation_index/#model_vi)

 ### Ecriture des résultats
Les coefficients du modèle, l'index de la première date utilisée pour la détection et le masque des pixels valides car ayant suffisamment de dates SENTINEL pour le calcul du modèle sont écrits sous forme de rasters.
 > **_Fonctions utilisées :_** [write_tif()](docs/API_Reference/fordead/writing_data/#write_tif)
