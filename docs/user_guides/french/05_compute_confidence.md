## (FACULTATIF) ETAPE 5 : Calcul d'un indice de confiance pour classifier selon l'intensité des anomalies
Cette étape calcule un indice de confiance destiné à évaluer l'intensité des dépérissements détectés. L'indice est une moyenne pondérée de la différence entre l'indice de végétation et l'indice de végétation prédit pour toutes les dates non masquées après la première anomalie ultérieurement confirmée. Pour chaque date, le poids correspond au nombre de dates non masquées depuis la première anomalie.
En cas de dépérissement, l'intensité des anomalies est supposée augmenter, c'est pourquoi les dates ultérieures ont plus de poids.
Ensuite, les pixels sont classés en fonction de la discrétisation de l'indice de confiance à l'aide d'une liste de seuils. Les pixels présentant seulement trois anomalies sont classés dans la classe la plus basse, car 3 anomalies ne sont pas considérées comme suffisantes pour calculer un indice significatif. Les résultats sont vectorisés et sauvegardés dans le répertoire data_directory/Confidence_Index.
Cette étape est facultative et peut être sautée si elle inutile ou non pertinente.

#### INPUTS
Les paramètres d'entrée sont :
- **data_directory** : Le chemin du dossier de sortie où seront écrits les résultats.
- **threshold_list** : Liste des seuils utilisés pour discrétiser l'indice de confiance en plusieurs classes.
- **classes_list** : Liste des noms des classes, si threshold_list a n valeurs, classes_list doit donc avoir n+1 valeurs
- **chunks** : Taille du chunk pour calculer en utilisant dask permettant la parallélisation et l'économie de RAM. Doit être utilisé pour les grands jeux de données tels qu'une tuile Sentinel entière.

#### OUTPUTS
Les sorties de cette étape, dans le dossier data_directory/Confidence_Index, sont deux rasters et un shapefile :
- **confidence_index.tif** : L'indice de confiance calculé
- **nb_dates.tif** : le nombre de dates non masquées depuis la première anomalie confirmée pour chaque pixel
- **confidence_class.shp** : Un shapefile résultant de la discrétisation de l'indice de confiance, sur tous les pixels avec des dépérissements confirmées par 3 dates successives, excluant les zones hors du masque forêt, là où aucun modèle n'a pu être calculé, et les pixels détectés comme sol nu si la détection de sol nu a été effectuée (voir [01_compute_masked_vegetationindex](https://fordead.gitlab.io/fordead_package/docs/user_guides/french/01_compute_masked_vegetationindex/).

## Utilisation
### A partir d'un script

``bash
from fordead.steps.step5_compute_confidence_index import compute_confidence_index
compute_confidence_index(data_directory = <data_directory>, 
						threshold_list = <liste_seuils>,
						classes_list = <list_seuils>,
						chunks = 1280)
```

### A partir de la ligne de commande
```bash
fordead ind_conf [OPTIONS] (en anglais)
```
Voir la documentation détaillée sur le [site](https://fordead.gitlab.io/fordead_package/docs/cli/#fordead-ind_conf)

## Détail du fonctionnement

### Importation des informations sur les processus précédents et suppression des résultats obsolètes s'ils existent
Les informations sur les processus précédents sont importées (paramètres, chemins de données, dates utilisées...). Si les paramètres utilisés ont été modifiés, tous les résultats à partir de cette étape sont supprimés. Ainsi, en l'absence de nouvelles dates Sentinel-2 depuis un précédant usage, l'indice de confiance est importé à partir des résultats précédants.
**_Fonctions utilisées:_** [TileInfo()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#tileinfo), méthodes de la classe TileInfo [import_info()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#import_info), [add_parameters()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#add_parameters), [delete_dirs()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#delete_dirs), [delete_attributes()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#delete_attributes)

### Importation des résultats des étapes précédentes
Les coefficients du modèle de prédiction de l'indice de végétation sont importés ainsi que les informations relatives à la détection des dépérissements (état des pixels, date de première anomalie...)., les informations relatives à la détection de sol nu si elle a été réalisée, et l'indice de confiance s'il a déjà été calculé et qu'il n'y a pas de nouvelles dates Sentinel-2.
> **_Fonctions utilisées:_** [import_coeff_model()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#import_coeff_model), [import_dieback_data()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#import_dieback_data), [soil_data()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#soil_data), [initialize_confidence_data()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#initialize_confidence_data), [import_confidence_data()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#import_confidence_data)

### Pour chaque date à partir de la première date utilisée pour la détection des dépérissements :

#### Importation de l'indice de végétation calculé et du masque.
**_Fonctions utilisées:_** [import_masked_vi()](https://fordead.gitlab.io/fordead_package/reference/fordead/import_data/#import_masked_vi)

#### (FACULTATIF - si **correct_vi** est True dans [étape de calcul du modèle](https://fordead.gitlab.io/fordead_package/docs/user_guides/03_train_model/)
- Le terme de correction calculé dans les étapes précédentes est ajouté à la valeur de l'indice de végétation de chaque pixel.
**_Fonctions utilisées:_** [correct_vi_date()](https://fordead.gitlab.io/fordead_package/reference/fordead/model_vegetation_index/#correct_vi_date)

#### Prédiction de l'indice de végétation à la date donnée.
L'indice de végétation est prédit à partir des coefficients du modèle.
**_Fonctions utilisées:_** [prediction_vegetation_index()](https://fordead.gitlab.io/fordead_package/reference/fordead/dieback_detection/#prediction_vegetation_index)

#### Calcul de l'intensité des anomalies
La différence entre l'indice de végétation et sa prédiction est calculée. Si l'indice de végétation augmente en cas de perturbation, la prédiction est soustraite à la valeur réelle ; si l'indice de végétation diminue, l'indice de végétation est soustrait à sa prédiction. De cette façon, la valeur de la différence augmente pour les anomalies plus intenses.

### Calcul de l'indice de confiance à partir de la différence entre l'indice de végétation et sa prédiction
La différence entre la végétation et sa prédiction, si elle n'est pas masquée, est multipliée par un poids associé, puis la somme est réalisée. Le poids est le nombre de dates Sentinel-2 non masquées depuis de la première anomalie confirmée.
Cette somme est ensuite divisée par la somme des poids, le résultat est l'indice de confiance utilisé. Le graphique suivant illustre la formule utilisée :

![graph_ind_conf](Diagrammes/graph_ind_conf.png "graph_ind_conf").

### Discrétisation et vectorisation des résultats
L'indice de confiance est discrétisé en utilisant la liste de seuils **threshold_list**. Les pixels ayant seulement trois dates de la première anomalie, le nombre minimum de dates pour la détection du dépérissement, sont affectés au premier groupe. 
Ensuite, ces résultats sont vectorisés et affectés avec les classes de la liste **classes_list**.
Les pixels sont ignorés s'ils se trouvent en dehors du masque forestier, ou si aucun modèle n'a pu être calculé, ou encore s'ils ont été détectés comme sol nu si une telle détection a eu lieu.
**_Fonctions utilisées:_** [vectorizing_confidence_class()](https://fordead.gitlab.io/fordead_package/reference/fordead/writing_data/#vectorizing_confidence_class),

#### Écriture des résultats
Le nombre de dates depuis la première anomalie et l'indice de confiance continu sont écrits sous forme de rasters.
Le shapefile vectoriel discrétisé est également écrit.
**_Fonctions utilisées:_** [write_tif()](https://fordead.gitlab.io/fordead_package/reference/fordead/writing_data/#write_tif)
