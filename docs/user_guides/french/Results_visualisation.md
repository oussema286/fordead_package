# Visualisation des résultats
Le package contient également deux outils de visualisation des résultats. Le premier permet de réaliser un timelapse permettant de visualiser les résultats à chaque date Sentinel-2 utilisée, avec en fond les données Sentinel-2 en RGB, avec un slider pour naviguer entre les différentes dates.
Le deuxième permet de visualiser pour un pixel en particulier la série temporelle de l'indice de végétation avec le modèle associé, le seuil de détection d'anomalies et les détections associées.

## Créer des timelapses
#### ENTRÉES
Les paramètres en entrée sont :

- **data_directory** : Le chemin du dossier dans lequel sont écrits les résultats déjà calculés, et dans lequel seront sauvegardés les timelapses
- **shape_path** : Chemin d'un shapefile contenant des polygones ou des points utilisés pour définir la zone des timelapses
- **name_column** : Nom de la colonne contenant l'identifiant ou nom unique du polygone ou point si **shape_path** est utilisé. (Par défault : "id")
- **x** : Coordonnée x dans le système de projection de la tuile Sentinel-2. Pas utilisé si le timelapse est défini à partir d'un shapefile par le paramètre **shape_path**.
- **y** : Coordonnée y dans le système de projection de la tuile Sentinel-2. Pas utilisé si le timelapse est défini à partir d'un shapefile par le paramètre **shape_path**.
- **buffer** : Zone tampon autour des polygones ou des points pour définir l'étendue du timelapse.
- **vector_display_path** : Optionnel, chemin d'un vecteur à afficher dans le timelapse, peut contenir des points, des lignes et des polygones.
- **hover_column_list** : String ou liste de strings correspondant aux colonnes du fichier **vector_display_path**, dont les informations seront affichées en plaçant la souris sur ses objects. A utiliser seulement si **vector_display_path** est utilisé
- **max_date** : Exclut du timelapse l'ensemble des dates Sentinel-2 après cette date (format : "AAAA-MM-JJ"). Par défaut, le timelapse utilise l'ensemble des dates Sentinel-2 disponibles.
- **show_confidence_class** : Si True, le dépérissement détecté est indiqué avec la classe de confiance, indicative de l'état du pixel à la dernière date utilisée, telle que vectorisé à l'étape [05_export_results](05_export_results.md)
- **zip_results** : Si True, les fichiers html contenant les timelapses sont transférés dans un fichier zip compressé.

Les paramètres indispensables sont **data_directory** ainsi que **shape_path** ou **x** et **y**.

#### SORTIES
Les sorties sont dans le dossier data_directory/Timelapses, avec pour chaque polygone ou point un fichier .html avec comme nom de fichier la valeur dans la colonne **name_column** si réalisés à partir de **shape_path**, ou x_y.html si réalisé à partir de coordonnées.
Si zip_results vaut True, les timelapses crées sont zippés dans un fichier Timelapses.zip. Zipper les fichiers html réduit leur poids de 70%.

Cet outil peut ne pas fonctionner sur des zones trop larges, il est recommandé d'éviter de lancer cette opération sur des zones de plus d'une vingtaine de km².

#### ANALYSE
Le slider permet de se déplacer temporellement de date SENTINEL en date SENTINEL
L'image correspond aux bandes RGB des données SENTINEL
Les résultats apparaissent sous forme de polygones :
- Le déperissement détecté apparait en blanc, ou du blanc au rouge selon la classe de confiance si **show_confidence_class** vaut True.
Si la détection inclu la détection de sol nu (see [01_compute_masked_vegetationindex](https://fordead.gitlab.io/fordead_package/docs/user_guides/french/01_compute_masked_vegetationindex/)) :
- Polygones noirs : sol nu
- Polygones bleus : zones détectées comme coupe sanitaire (zones détectées comme sol-nu après avoir été détectées comme dépérissantes)

Les pixels hors du masque végétation utilisé, ou invalides car n'ayant pas assez de dates pour calculer un modèle d'indice de végétation, ou ayant trop de périodes de stress, apparaissent en gris avec la légende "Permanently masked pixels".

Une légende est incluse, un clic sur un élément de la légende permet de le rendre invisible, un double clic en fait le seul élément visible sur le graphique.

Les résultats apparaissent à partir de la première anomalie, confirmée par la suite. Les fausses détections liées à un stress hydrique temporaire et corrigées par la suite n'apparaissent pas. De même, pour les dernières , il peut y avoir des anomalies n'apparaissant pas encore par manque de  valides pour confirmer la détection.

Si **vector_display_path** est renseigné, les points, lignes ou polygones à l'intérieur du shapefile sont affichés en violet foncé. L'utilisateur peut déplacer la souris sur les objets pour obtenir les informations des colonnes listées dans **hover_column_list**.
Il est également possible de zoomer sur la zone souhaitée en maintenant le clic enfoncé tout en délimitant une zone. Il est ensuite possible de faire un zoom arrière en double-cliquant sur l'image. Passer la souris sur un pixel permet également d'obtenir ses informations :

- x : coordonnées en x
- y : coordonnées en y
- z : `[<réflectance dans le rouge>,<réflectance dans le vert>,<réflectance dans le bleu>]`, c'est à dire la valeur de la bande SENTINEL correspondante à la date donnée.

## Utilisation
### A partir d'un script
#### A partir d'un shapefile contenant les zones d'intérêt
```bash
from fordead.visualisation.create_timelapse import create_timelapse
create_timelapse(data_directory = <data_directory>,shape_path = <shape_path>, buffer = 100, name_column = "id")
```
#### A partir de coordonnées
```bash
from fordead.visualisation.create_timelapse import create_timelapse
create_timelapse(data_directory = <data_directory>, x = <x>, y = <y>, buffer = 100)
```
### A partir de l'invité de commande
```bash
fordead timelapse [OPTIONS]
```
Voir documentation détaillée sur le [site](../../cli.md#fordead-timelapse)

***

## Créer des graphes montrant l'évolution de la série temporelle
#### ENTRÉES
Les paramètres en entrée sont :

- **data_directory** : Le chemin du dossier dans lequel sont écrits les résultats déjà calculés, et dans lequel seront sauvegardés les graphes
- **x** : Coordonnée x dans le système de projection de la tuile Sentinel-2. Pas utilisé si le les points sont définis à partir d'un shapefile par le paramètre **shape_path**.
- **y** : Coordonnée y dans le système de projection de la tuile Sentinel-2. Pas utilisé si le les points sont définis à partir d'un shapefile par le paramètre **shape_path**.
- **shape_path** : Chemin d'un shapefile contenant les points où les graphiques seront réalisés. Pas utilisé si le les points sont définis à partir des paramètres **x** et **y**.
- **name_column** : Nom de la colonne contenant l'identifiant ou nom unique du point (Par défaut : "id") si **shape_path** est utilisé.
- **ymin** : ymin limite du graphe, à adapter à l'indice de végétation utilisé (Par défaut : 0)
- **ymax** : ymax limite du graphe, à adapter à l'indice de végétation utilisé (Par défaut : 2)
- **chunks** : int, Si les résultats utilisés ont été calculés à large échelle, donner une taille de chunks (ex : 1280) permet d'importer les données de manière à sauvegarder la RAM. 

#### SORTIES
Les sorties sont dans le dossier data_directory/TimeSeries, avec pour chaque point un fichier .png avec comme nom de fichier la valeur dans la colonne **name_column**, ou le format *Xx_coord_Yy_coord.png* si les coordonnées sont utilisées.

## Utilisation
### A partir d'un script
#### A partir d'un shapefile contenant les zones d'intérêt
```bash
from fordead.visualisation.vi_series_visualisation import vi_series_visualisation
vi_series_visualisation(data_directory = <data_directory>, shape_path = <shape_path>, name_column = "id", ymin = 0, ymax = 2, chunks = 100)
```
#### A partir de coordonnées
Les coordonnées doivent être fournies dans le système de projection de la tuile Sentinel-2.
```bash
from fordead.visualisation.vi_series_visualisation import vi_series_visualisation
vi_series_visualisation(data_directory = <data_directory>, x = <x_coord>, y = <y_coord>, ymin = 0, ymax = 2, chunks = 100)
```


#### Depuis boucle prompt
Si ni **x** et **y**, ni **shape_path** ne sont donnés, l'utilisateur sera invité à donner soit des coordonnées X et Y dans le système de projection des données Sentinel-2 utilisées, soit les indices de pixels à partir de (xmin,ymax) de toute la zone, ce qui peut être utile si un timelapse a été créé sur toute la zone calculée, auquel cas l'indice correspond aux coordonnées dans le timelapse.
Après chaque tracé, l'utilisateur est invité à donner de nouvelles coordonnées. Entrez X = -1 pour terminer la boucle. Entrez <ENTER> pour qu'un pixel aléatoire dans la zone d'intérêt soit choisi.

```bash
from fordead.visualisation.vi_series_visualisation import vi_series_visualisation
vi_series_visualisation(data_directory = <data_directory>, ymin = 0, ymax = 2, chunks = 100)
```

> **_NOTE :_** Le paramètre **chunks** peut être ignoré seulement si la zone calculée est petite.

### A partir de l'invité de commande
```bash
fordead graph_series [OPTIONS]
```
Voir documentation détaillée sur le [site](../../cli.md#fordead-graph_series)

#### EXEMPLE
![anomaly_detection_X642135_Y5452255](Diagrams/anomaly_detection_X642135_Y5452255.png "anomaly_detection_X642135_Y5452255")
