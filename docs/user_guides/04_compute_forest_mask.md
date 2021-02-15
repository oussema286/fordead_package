## ÉTAPE 4 : step4_compute_forest_mask.py
Cette étape permet de calculer le masque forêt et ainsi définir les zones d'intérêt.

#### ENTRÉES
Les paramètres en entrée sont :
- **data_directory** : Le chemin du dossier de sortie dans lequel sera écrit le masque forêt
- **forest_mask_source** : Source du masque forêt, peut être "BDFORET" pour utiliser la BD Forêt de l'IGN,  "OSO" pour utiliser la carte d'occupation des sols du CESBIO, ou None pour ne pas utiliser de masque forêt et étendre la zone d'intérêt à l'ensemble des pixels
- **dep_path** : Chemin d'un shapefile des départements français contenant le code insee dans un champ code_insee, seulement utile si forest_mask_source vaut "BDFORET"
- **bdforet_dirpath** : Chemin du dossier contenant la BD Forêt de l'IGN avec un dossier par département. Seulement utile si forest_mask_source vaut "BDFORET"
- **list_forest_type** : Liste des types de peuplements à garder dans le masque forêt, correspond au CODE_TFV de la BD Forêt. Seulement utile si forest_mask_source vaut "BDFORET"
- **path_oso** : Chemin du raster d'occupation des sols du CESBIO. Seulement utile si forest_mask_source vaut "OSO".
- **list_code_oso** : Liste des valeurs du raster OSO à conserver dans le masque forêt. Seulement utile si forest_mask_source vaut "OSO".
- **path_example_raster** : Chemin d'un raster "example" utilisé pour connaître l'extent, le système de projection, etc... Seulement utile s'il n'y a pas dans le data_directory un fichier TileInfo crée par les étapes précèdentes d'où peuvent être extraites ces informations.

#### SORTIES
Les sorties de cette quatrième étape, dans le dossier data_directory, sont :
- Dans le dossier **ForestMask**, le raster binaire Forest_Mask.tif qui vaut 1 sur les pixels de forêt à étudier et 0 ailleurs.

## Utilisation
### A partir d'un script

```bash
from fordead.steps.step4_compute_forest_mask import compute_forest_mask
compute_forest_mask(data_directory, 
                    forest_mask_source = <forest_mask_source>, 
                    dep_path = <dep_path>,
                    bdforet_dirpath = <bdforet_dirpath>)
```


### A partir de la ligne de commande

```bash
fordead forest_mask [OPTIONS]
```

Voir documentation détaillée sur le [site](https://fordead.gitlab.io/fordead_package/docs/cli/#forest_mask)
