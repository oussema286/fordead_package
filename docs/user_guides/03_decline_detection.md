## ÉTAPE 3 : step3_DetectionFordead.py
Cette étape permet la détection du déperissement. Pour chaque date SENTINEL non utilisée pour l'apprentissage, l'indice de végétation réel est comparé à l'indice de végétation prédit à partir des modèles calculés dans l'étape précèdente. Si la différence dépasse un seuil, une anomalie est détectée. Si trois anomalies successives sont détectées, le pixel est considéré comme dépérissant. Si après avoir été détecté comme déperissant, le pixel a trois dates successives sans anomalies, il n'est plus considéré comme dépérissant.

#### ENTRÉES
Les paramètres en entrée sont :
- **data_directory** : Le chemin du dossier de sortie dans lequel sera écrit les résultats de la détection.
- **threshold_anomaly** : Seuil à partir duquel la différence entre l'indice de végétation réel et prédit est considéré comme une anomalie

#### SORTIES
Les sorties de cette troisième étape, dans le dossier data_directory, sont :
- Dans le dossier **DataDecline**, trois rasters :
    - **count_decline** : le nombre de dates successives avec des anomalies
    - **first_date_decline** : L'index de la première date avec une anomalie de la dernière série d'anomalies
    - **state_decline** : Un raster binaire qui vaut 1 si le pixel est détecté comme déperissant (Au moins trois anomalies successives)

## Utilisation
### A partir d'un script

```bash
from fordead.steps.step3_decline_detection import decline_detection
decline_detection(data_directory = <data_directory>)
```

### A partir de la ligne de commande
```bash
fordead decline_detection [OPTIONS]
```
Voir documentation détaillée sur le [site](https://fordead.gitlab.io/fordead_package/docs/cli/#decline_detection)
