## ÉTAPE 3 : Détection du dépérissement par comparaison entre l'indice de végétation prédit par le modèle et l'indice de végétation réel
Cette étape permet la détection du déperissement. Pour chaque date SENTINEL non utilisée pour l'apprentissage, l'indice de végétation réel est comparé à l'indice de végétation prédit à partir des modèles calculés dans l'étape précèdente. Si la différence dépasse un seuil, une anomalie est détectée. Si trois anomalies successives sont détectées, le pixel est considéré comme dépérissant. Si après avoir été détecté comme déperissant, le pixel a trois dates successives sans anomalies, il n'est plus considéré comme dépérissant.
Ces périodes entre la détection et le retour à la normale peuvent être enregistrées et associées à un indice de stress.
Cet indice de stress peut être soit la moyenne de la différence entre l'indice de végétation et sa prédiction, soit une moyenne pondérée où pour chaque date utilisée, le poids correspond au numéro de la date à partir de la première anomalie :

![graph_ind_conf](Diagrams/graph_ind_conf.png "graph_ind_conf")

#### ENTRÉES
Les paramètres en entrée sont :
- **data_directory** : Le chemin du dossier de sortie dans lequel sera écrit les résultats de la détection.
- **threshold_anomaly** : Seuil à partir duquel la différence entre l'indice de végétation réel et prédit est considéré comme une anomalie
- **max_nb_stress_periods** : Nombre maximum de périodes de stress, les pixels avec un nombre plus élevé de périodes de stress sont masqués dans les exports.
- **stress_index_mode** : Choix de l'indice de stress, si 'mean', l'indice est la moyenne de la différence entre l'indice de végétation et sa prédiction pour toutes les dates non masquées après la première anomalie confirmée ultérieurement. Si 'weighted_mean', l'indice est une moyenne pondérée, où pour chaque date utilisée, le poids correspond au numéro de la date (1, 2, 3, etc...) à partir de la première anomalie. Si None, les périodes de stress ne sont pas détectées, et aucune information n'est enregistrée.
- **vi** : Indice de végétation utilisé, il est inutile de le renseigner si l'étape [_compute_masked_vegetationindex_]() a été utilisée.
- **path_dict_vi** : Chemin d'un fichier texte permettant d'ajouter des indices de végétations utilisables. Si non renseigné, uniquement les indices prévus dans le package sont utilisable (CRSWIR, NDVI, NDWI). Le fichier [examples/ex_dict_vi.txt](../../examples/ex_dict_vi.txt) donne l'exemple du formattage de ce fichier. Il s'agit de renseigner son nom, sa formule, et "+" ou "-" selon si l'indice augmente en cas de déperissement, ou si il diminue. Il est également inutile de le renseigner si cela a été fait lors de l'étape [_compute_masked_vegetationindex_](../../user_guides/french/01_compute_masked_vegetation_index.md).


#### SORTIES
Les sorties de cette troisième étape, dans le dossier data_directory, sont :
- Dans le dossier **DataDieback**, trois rasters :
    - **count_dieback** : le nombre de dates successives avec des anomalies
	- **first_date_unconfirmed_dieback** : L'indice de la date du dernier changement d'état potentiel du pixel, date de première anomalie si le pixel n'est pas détecté comme un dépérissement, première non-anomalie si le pixel est détecté comme un dépérissement.
    - **first_date_dieback** : L'index de la première date avec une anomalie de la dernière série d'anomalies
    - **state_dieback** : Un raster binaire qui vaut 1 si le pixel est détecté comme déperissant (Au moins trois anomalies successives)
- Dans le dossier **DataStress**, quatre rasters :
    - **dates_stress** : Un raster avec **max_nb_stress_periods***2+1 bandes, contenant les indices de date de la première anomalie, et de retour à la normale pour chaque période de stress.
    - **nb_periods_stress** : Un raster contenant le nombre total de périodes de stress pour chaque pixel. 
    - **cum_diff_stress** : Un raster à **max_nb_stress_periods**+1 bandes contenant pour chaque période de stress la somme de la différence entre l'indice de végétation et sa prédiction, multipliée par le poids si stress_index_mode est "weighted_mean".
	- **nb_dates_stress** : Un raster avec **max_nb_stress_periods**+1 bandes contenant le nombre de dates non masquées de chaque période de stress.
	- **stress_index** : Un raster avec **max_nb_stress_periods**+1 bandes contenant l'indice de stress de chaque période de stress, c'est la moyenne ou la  moyenne pondérée de la différence entre l'indice de végétation et sa prédiction en fonction de **stress_index_mode**, obtenue à partir de cum_diff_stress et nb_dates_stress
	Le nombre de bandes de ces matrices permet de sauvegarder les informations de chaque période de stress potentielle, et de la période du potentiel dépérissement final détecté.
- Dans le dossier **DataAnomalies**, un raster pour chaque date **Anomalies_YYYY-MM-JJ.tif** qui vaut True là où sont détectées les anomalies.
- Si **stress_index_mode** est défini, dans le dossier TimelessMasks, un raster binaire valant 1 pour les pixels dont le nombre de périodes de stress est inférieur ou égal à **max_nb_stress_periods**, sinon 0.

## Utilisation
### A partir d'un script

```bash
from fordead.steps.step3_dieback_detection import dieback_detection
dieback_detection(data_directory = <data_directory>)
```

### A partir de la ligne de commande
```bash
fordead dieback_detection [OPTIONS]
```
Voir documentation détaillée sur le [site](https://fordead.gitlab.io/fordead_package/docs/cli/#fordead-dieback_detection)

## Détail du fonctionnement

![Diagramme_step3](Diagrams/Diagramme_step3.png "Diagramme_step3")

### Imports des informations sur les traitements précédents et suppression des résultats obsolètes si existants
Les informations relatives aux traitements précédents sont importés (paramètres, chemins des données, dates utilisées...). Si les paramètres utilisés ont été modifiés, l'ensemble des résultats à partir de cette étape sont supprimés. Ainsi, à moins que les paramètres aient été modifiés ou que ce soit la première fois que ce traitement est réalisé, la détection du dépérissement est mise à jour uniquement avec les nouvelles dates SENTINEL.
> **_Fonctions utilisées :_** [TileInfo()][fordead.import_data.TileInfo], méthodes de la classe TileInfo [import_info()][fordead.import_data.TileInfo.import_info], [add_parameters()][fordead.import_data.TileInfo.add_parameters], [delete_dirs()][fordead.import_data.TileInfo.delete_dirs]

### Imports des résultats des étapes précédentes
Les coefficients du modèle de prédiction de l'indice de végétation sont importés, ainsi que l'array contenant l'index de la première date utilisée pour la détection. Les arrays contenant les informations liées à la détection de déperissement (État des pixels, nombre d'anomalies successives, index de la date de première anomalie) sont initialisés si l'étape est utilisée pour la première fois, ou importés si il s'agit d'une mise à jour de la détection.
> **_Fonctions utilisées :_** [import_coeff_model()][fordead.import_data.import_coeff_model], [import_first_detection_date_index()][fordead.import_data.import_first_detection_date_index], [initialize_dieback_data()][fordead.import_data.initialize_dieback_data], [import_dieback_data()][fordead.import_data.import_dieback_data]

### Pour chaque date non déjà utilisée pour la détection du dépérissement :

#### Imports de l'indice de végétation calculé et du masque
> **_Fonctions utilisées :_** [import_masked_vi()][fordead.import_data.import_masked_vi]

### (OPTIONNEL - si **correct_vi** vaut True lors de [l'étape précédente de calcul du modèle](https://fordead.gitlab.io/fordead_package/docs/user_guides/03_train_model/) Correction de l'indice de végétation à partir de l'indice de végétation médian des pixels d'intérêts non masqués à l'échelle de la zone complète
- Masquage des pixels n'appartenant pas à la zone d'intérêt, ou masqués
- Calcul de la médiane de l'indice de végétation de l'ensemble de la zone
- Calcul d'un terme de correction, par différence entre la médiane calculée et la prédiction du modèle calculé lors de l'étape précédente à partir de la médiane calculée pour l'ensemble des dates
- Application du terme de correction en l'ajoutant à la valeur de l'indice de végétation de l'ensemble des pixels
> **_Fonctions utilisées :_** [correct_vi_date()][fordead.model_vegetation_index.correct_vi_date]

#### Prédiction de l'indice de végétation à la date donnée.
L'indice de végétation est prédit à partir des coefficients du modèle.
> **_Fonctions utilisées :_** [prediction_vegetation_index()][fordead.model_vegetation_index.prediction_vegetation_index]

#### Détection d'anomalies
Les anomalies sont détectées en comparant l'indice de végétation avec sa prédiction. Sachant si l'indice de végétation est supposé augmenter ou diminuer en cas de déperissement, les anomalies sont détectées là où la différence entre l'indice et sa prédiction est superieure à **threshold_anomaly** dans la direction du changement attendu en cas de déperissement.
> **_Fonctions utilisées :_** [detection_anomalies()][fordead.dieback_detection.detection_anomalies]

#### Détection du dépérissement
Les anomalies successives sont comptées, à partir de trois anomalies successives, le pixel est considéré dépérissant. Si le pixel est considéré dépérissant, les dates successives sans anomalies sont comptées et à partir de trois dates sans anomalies, le pixel n'est plus considéré dépérissant.
> **_Fonctions utilisées :_** [detection_dieback()][fordead.dieback_detection.detection_dieback]

#### Sauvegarde des informations sur les périodes de stress (OPTIONNEL, si stress_index_mode est renseigné)
Les rasters contenant les informations sur les périodes de stress sont mis à jour, le nombre de périodes de stress est mis à jour lorsque les pixels reviennent à la normale. Lorsque les changements d'état sont confirmés, la première date d'anomalie ou de retour à la normale est sauvegardée. Pour chaque date, le nombre de dates dans les périodes de stress est mis à jour si le pixel n'est pas masqué et en période de stress.
La différence entre l'indice de végétation et sa prédiction est ajoutée au raster cum_diff_stress, après avoir été multipliée par le numéro de la date si stress_index_mode est "weighted_mean".
**_Fonctions utilisées:_** [save_stress()][fordead.dieback_detection.save_stress]

### Création d'un masque pour les pixels subissant un nombre trop élevé de périodes de stress
Le nombre de périodes de stress pour chaque pixel est comparé au paramètre **max_nb_stress_periods**, ce qui donne le masque too_many_stress_periods_mask.
Ce masque invalide les données lors des exports et autres sorties.

### L'indice de stress est calculé
Si stress_index_mode est "mean", la trame de l'indice de stress est la trame cum_diff_stress divisée par la trame nb_dates_stress.
Si stress_index_mode est "weighted_mean", le raster stress index est le raster cum_diff_stress divisé par la somme des poids (1+2+3+...+ nb_dates_stress).

 ### Ecriture des résultats
Les informations liées à la détection du dépérissement et les périodes de stress sont écrites. L'ensemble des paramètres, chemins des données et dates utilisées sont aussi sauvegardés.
 > **_Fonctions utilisées :_** [write_tif()][fordead.writing_data.write_tif], méthode TileInfo [save_info()][fordead.import_data.TileInfo.save_info]

