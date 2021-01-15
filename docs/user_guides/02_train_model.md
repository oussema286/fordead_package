## ÉTAPE 2 : step2_TrainFordead.py
Cette étape permet le calcul d'un modèle à partir des premières dates SENTINEL, considérées comme représentatives du comportement saisonnier normal de l'indice de végétation. Ce modèle permet de prédire la valeur de l'indice de végétation à n'importe quelle date.

#### ENTRÉES
Les paramètres en entrée sont :
- **data_directory** : Le chemin du dossier de sortie dans lequel sera écrit les coefficients du modèle.
- **nb_min_date** : Nombre minimum de dates valides pour calculer un modèle
- **min_last_date_training** : Date au format AAAA-MM-JJ à partir de laquelle les dates SENTINEL ne sont plus utilisées pour l'apprentissage, tant qu'il y a au moins nb_min_date dates valides pour le pixel
- **max_last_date_training** : Date au format AAAA-MM-JJ jusqu'à laquelle les dates SENTINEL peuvent être utilisées pour l'apprentissage afin d'atteindre le nombre de nb_min_date dates valides
- **path_vi** : Chemin du dossier contenant un raster pour chaque date où l'indice de végétation est calculé pour chaque pixel. Inutile de le renseigner si les informations proviennent de l'étape 1, auquel cas le chemin est contenu dans le fichier TileInfo.
- **path_masks** : Chemin du dossier contenant un raster binaire pour chaque date où les pixels masqués valent 1, et les pixels valides 0. Inutile de le renseigner si les informations proviennent de l'étape 1, auquel cas le chemin est contenu dans le fichier TileInfo.

Les coefficients du modèle sont calculés pour chaque pixel. Pour chaque pixel, uniquement les dates non masquées sont utilisées. Si il y a nb_min_date dates valides à la date max_last_date_training, l'apprentissage s'arrête à cette date. Si le nombre de date de dates valides atteint nb_min_date entre à une date située entre min_last_date_training et max_last_date_training, l'apprentissage s'arrête à cette date. Si le nombre de date de dates valides n'atteint pas nb_min_date à la date max_last_date_training, le pixel est sorti de l'étude et ne sera pas associé à un modèle.
Cette méthode permet, dans le cas d'une crise sanitaire relativement ancienne comme le scolyte, de commencer la détection dès 2018 si l'on dispose de suffisamment de dates valides au début de l'année, tout permettant l'étude de pixels dans des situations de détection plus délicates simplement en réalisant l'apprentissage sur une période plus longue pour récupérer d'autres dates valides. Il parait difficile de terminer l'apprentissage avant 2018, car le modèle périodique étant annuel, l'utilisation d'au moins deux ans de données SENTINEL-2 parait obligatoire.

#### SORTIES
Les sorties de cette deuxième étape, dans le dossier data_directory, sont :
- Dans le dossier **DataModel**, deux fichiers :
    - **first_detection_date_index.tif**, un raster qui contient l'index de la première date qui sera utilisée pour la détection de déperissement. Il permet de savoir pour chaque pixel quelles dates ont été utilisées pour l'apprentissage et lesquelles sont utilisées pour la détection.
    - **coeff_model.tif**, un stack à 5 bandes, une pour chaque coefficient du modèle de l'indice de végétation.
- Dans le dossier **ForestMask**, le raster binaire **valid_area_mask.tif** qui vaut 1 pour les pixels où le modèle a pu être calculé, 0 si il n'y avait pas assez de dates valides
- Le fichier TileInfo est mis à jour.

