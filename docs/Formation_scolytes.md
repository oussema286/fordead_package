# <div align="center"> Détection des foyers de mortalité dans les massifs de conifères par imagerie satellite Sentinel-2 </div>

<div align="center"> Equipe de formation INRAE : Raphaël Dutrieux, Forian de Boissieu, Jean-Baptiste Feret, Kenji Ose </div>

## <div align="center">TP-02 : Utilisation du package `fordead` : détection de déperissement en forêt à partir de séries temporelles SENTINEL-2</div>

* [Introduction](#introduction)
    * [Préambule](#préambule)
    * [Objectifs](#objectifs)
    * [Pré-requis](#pré-requis)
* [Création d'un script pour détecter le dépérissement lié au scolyte sur une zone donnée à l'aide du package fordead](#utilisation-du-package-fordead)
    * [Étape 1 : Calcul de l'indice de végétation et du masque pour chaque date SENTINEL](#étape-1-calcul-de-lindice-de-végétation-et-du-masque-pour-chaque-date-sentinel)
    * [Étape 2 : Modélisation du comportement périodique de l'indice de végétation](#étape-2-modélisation-du-comportement-périodique-de-lindice-de-végétation)
    * [Étape 3 : Détection du déperissement](#étape-3-détection-du-déperissement)
    * [Étape 4 : Calcul du masque forêt](#étape-4-calcul-du-masque-forêt)
* [Visualisation des résultats](#visualisation-des-résultats)
    * [Visualisation d'un timelapse](#)
    * [Visualisation de la série temporelle de pixels en particulier](#)
* [Rajouter des dates SENTINEL et mettre à jour la détection](#)
* [Changer les paramètres de la détection](#)
    * [Changer l'indice de végétation](#)
    * [Changer le seuil de détection d'anomalies](#)
    * [Changer de zone d'étude](#)
* [Exporter des résultats adaptés à ses besoins](#)
    * [Étape 5 : Export des résultats](#)

## Introduction
### Préambule

Le monde forestier fait face à une accélération sans précedent des déperissements à large échelle, notamment en lien avec le changement climatique et l'apparition de ravageurs. En particulier, la crise sanitaire du scolyte met en péril la santé des forêts ainsi que la filière bois dans le Nord-Est de la France. Pour répondre à cet enjeu, des travaux R&D ont été menés par l’UMR TETIS (INRAE, anciennement IRSTEA) à la demande du Ministère de l’Agriculture et de l’Alimentation pour mettre au point un outil d’identification des foyers de scolytes par télédétection de manière précoce et en continu. Cet outil prend aujourd'hui la forme du package python `fordead` permettant une cartographie des déperissements à partir d'images SENTINEL-2, potentiellement mise à jour à chaque revisite des satellites SENTINEL-2.

### Objectifs
Les objectifs de ce TD sont les suivants :
- être capable de faire fonctionner l'ensemble des étapes permettant la cartographie des déperissements sur une zone donnée, ainsi que comprendre l'articulation de ces différentes étapes
- Savoir modifier les paramètres de l'outil afin de pouvoir s'adapter selon la problématique  
- Appréhender le potentiel et les limites de l'outil présenté
- Savoir sortir des résultats sous la forme souhaitée
- Visualiser les résultats et savoir les interpréter

### Pré-requis
Si le package n'est pas encore installé, suivre le [guide d'installation](https://gitlab.com/raphael.dutrieux/fordead_package/-/blob/master/docs/user_guides/00_installation.md).

Sinon, lancer l'invité de commande _anaconda prompt_, puis activer l'environnement par la commande : 
```bash
conda activate fordead_env
```

## Création d'un script pour détecter le dépérissement lié au scolyte sur une zone donnée à l'aide du package fordead

La détection du déperissement permet d'utiliser l'ensemble des données SENTINEL-2 depuis le lancement du premier satellite. Même en prenant une seule tuile, un tel jeu de données pèse plusieurs centaines de gigaoctets et prend plusieurs heures de temps de calcul pour réaliser l'ensemble des étapes de détection du déperissement. Pour cette raison, un jeu de données plus réduit a été préparé pour cette formation. Il contient l'ensemble des données SENTINEL-2 disponible sur une zone d'étude restreinte, en croppant à partir des données de la tuile. Cette zone est touchée par les scolytes, et contient plusieurs polygones de données de validation, ce qui en fait un bon exemple pour l'application de la détection de déperissement et la visualisation des résultats. 

- Créer un script python en créant un nouveau fichier de texte dans le dossier <MyWorkingDirectory>/B_PROGRAMS, et en le nommant _detection_scolytes.py_ (ou le nom de votre choix, mais avec l'extension .py)
- Ouvrez ce script avec l'éditeur de votre choix

#### Étape 1 : Calcul de l'indice de végétation et du masque pour chaque date SENTINEL
La première étape consiste à calculer pour chaque date l'indice de végétation, et le masque. Le masque correspond à l'ensemble des données invalides, car ennuagées, enneigées, dans l'ombre, hors de la fauchée du satellite, peuplement déjà coupé...
Vous pouvez retrouver le [guide d'utilisation de cette étape](https://gitlab.com/raphael.dutrieux/fordead_package/-/blob/master/docs/user_guides/01_compute_masked_vegetationindex.md).
##### Faire tourner l'étape à partir du script
Pour effectuer cette étape, ajoutez dans le script :
- Pour importer la fonction
```bash
from fordead.steps.step1_compute_masked_vegetationindex import compute_masked_vegetationindex
```
- Pour choisir les paramètres en entrée :
```bash
input_directory = "<MyWorkingDirectory>/A_DATA/RASTER/SERIES_SENTINEL/ZoneEtude"
data_directory = "<MyWorkingDirectory>/C_RESULTS/ZoneEtude"
```
> **_NOTE :_** Il est préférable d'utiliser "/" plutôt que "\" à l'écriture des chemins afin d'éviter les soucis.

- Pour lancer la fonction
```bash
compute_masked_vegetationindex(input_directory = input_directory, data_directory = data_directory)
```
Puis lancer le script python depuis l'invité de commande en vous plaçant dans le répertoire du script en utilisant la commande suivante :
```bash
cd <MyWorkingDirectory>/B_PROGRAMS
```
Puis lancer le script :
```bash
python detection_scolytes.py
```
##### Faire tourner l'étape en lançant la fonction depuis l'invité de commande
Il est également possible d'appliquer la même étape en passant par l'invité de commande.
Depuis l'invité de commande, placez vous dans le dossier fordead_package/fordead/steps. La commande suivante permet d'afficher l'aide :
```bash
python step1_compute_masked_vegetationindex.py -h
```
A partir de l'aide, lancez la fonction en appliquant vos paramètres. Exemple :
```bash
python step1_compute_masked_vegetationindex.py -i <MyWorkingDirectory>/A_DATA/RASTER/SERIES_SENTINEL/ZoneEtude -o <MyWorkingDirectory>/C_RESULTS/ZoneEtude
```
**-i** permet de définir le paramètre **input_directory** et **-o** le paramètre **data_directory**, ainsi exactement la même fonction est lancée.
---------

Vous remarquerez que si vous avez utilisé les même paramètres dans les deux cas, il s'affiche "0 new SENTINEL dates" et le programme tourne plus rapidement la deuxième fois, car les indices de végétation déjà calculés ne sont pas recalculés. En revanche, si vous changez les paramètres, les résultats précédants seront supprimés et remplacés.
Les paramètres input_directory et data_directory sont les deux seuls à ne pas connaître de valeur par défaut puisqu'elles dépendent de l'emplacement de vos fichiers. Ce sont donc les deux seuls paramètres à renseigner obligatoirement, mais il est tout de même possible de modifier les autres paramètres. A l'aide du guide d'utilisateur, vérifiez que vous comprenez le sens des différents paramètres et n'hésitez pas à poser des questions si ce n'est pas le cas !

L'ensemble des étapes de la détection peuvent se réaliser de manière identique depuis l'invité de commande, ou par import des différentes fonctions dans un script. Dans la suite de ce TD, nous nous focaliseront sur le script en le complétant au fur et à mesure.

##### Observation des sorties
Pour mieux vous représenter les sorties de cette étape, lancez QGIS et ajoutez les rasters VegetationIndex/VegetationIndex_2018-07-27.tif et Mask/Mask_2018-07-27.tif.
+ Ajouter bandes SENTINEL et créer raster virtuel RGB ?
Les rasters dans le dossier DataSoil contiennent les informations relatives à la détection du sol nu. Ce sol détecté peut correspondre à des zones non forestières, à des peuplements feuillus dont le sol est détecté en hiver, ou des coupes rases. Il y a trois rasters, qui, ensemble, permettent de reconstituer l'ensemble de l'information, et de la mettre à jour avec l'arrivée de nouvelles dates SENTINEL :
- Le raster count_soil.tif compte le nombre d'anomalies de sol successives.
- Lorsque count_soil atteint 3, pour trois anomalies successives, le raster state_soil.tif passe de 0 à 1. Les pixels avec la valeur 1 correspondent donc à ceux détectés comme sol nu / coupe au bout de l'analyse de l'ensemble des dates.
- Le raster first_date_soil.tif contient l'index de la date de première anomalie de sol. Si state_soil vaut 1, il s'agit alors de la date à partir de laquelle le sol est détectée. 
Ces rasters peuvent être difficiles à analyser puisque, n'étant pas possible de mettre une date dans un raster, le raster first_date_soil contient **l'index** de la date qui peut être interprété par le package dans les étapes suivantes.

#### Étape 2 : Modélisation du comportement périodique de l'indice de végétation 
Pour modéliser le comportement normal de l'indice de végétation, on utilise seulement les dates SENTINEL les plus anciennes, en faisant l'hypothèse qu'elles sont antérieures à un possible déperissement. La fonction harmonique suivante est ajustée à ces données :
𝒇(𝒕)=𝒂𝟏+𝒃𝟏.𝐬𝐢𝐧⁡(𝟐𝝅𝒕/𝑇)+𝒃𝟐.𝐜𝐨𝐬⁡(𝟐𝝅𝒕/𝑇)+𝒃𝟑.𝐬𝐢𝐧⁡(𝟒𝝅𝒕/𝑇)+𝒃𝟒.𝐜𝐨𝐬⁡(𝟒𝝅𝒕/𝑇) où T = 365,25.
Vous pouvez retrouver le [guide d'utilisation de cette étape](https://gitlab.com/raphael.dutrieux/fordead_package/-/blob/master/docs/user_guides/02_train_model.md).

Pour effectuer cette étape, ajoutez dans le script :
- Pour importer la fonction
```bash
from fordead.steps.step2_train_model import train_model
```
- Pour lancer la fonction
```bash
train_model(data_directory = data_directory)
```
Puis, comme pour l'étape 1, relancez le script depuis l'invité de commande :
```bash
python detection_scolytes.py
```

Le reste des paramètres connaissent une valeur par défaut dans la fonction et n'ont pas besoin d'être renseignées. Ces valeurs par défaut ont été déterminées de manière empirique pour la problématique du scolyte et peuvent ne pas être optimales selon la localisation ou la problématique donnée. Le [guide d'utilisation](https://gitlab.com/raphael.dutrieux/fordead_package/-/blob/master/docs/user_guides/02_train_model.md) donne des détails sur les différents paramètres, lisez le et vérifiez que vous comprenez bien leur sens.

> **_NOTE :_** Si l'utilisateur ne souhaite pas utiliser la première étape et choisit de calculer ses propres indices de végétations et masques. Il peut sauter l'étape 1 et simplement donner le chemin de son dossier d'indices de végétation avec le paramètre **path_vi** et son dossier de masques avec **path_masks**. Il suffit simplement que le nom des rasters contiennent la date sous un des formats suivants : AAAA-MM-JJ, AAAA_MM_JJ, AAAAMMJJ, JJ-MM-AAAA, JJ_MM_AAAA ou JJMMAAAA.

##### Observation des sorties
Dans le dossier DataModel :
- Ouvrez le raster coeff_model.tif dans QGIS. Faites un clique droit sur un des pixels, vous pouvez constater qu'il s'agit d'un raster à cinq bandes. QGIS affiche une image en RGB à partir des trois premières bandes. Chacune des bandes correspond à un des coefficients (a1, b1, b2, b3, b4) du modèle (voir équation). On a bien un modèle différent par pixel ce qui permet qu'il soit adapté aux conditions de ce pixel. On peut en effet imaginer que la composition du peuplement, sa surface terrière, sa pente, son exposition ont probablement un rôle à jouer dans la valeur donnée des indices de végétation. A partir de ces coefficients, il est possible de prédire l'indice de végétation à n'importe quelle date, pour un peuplement sain.

- Ouvrez maintenant le raster first_detection_date_index.tif. Il permet de connaître pour chaque pixel les dates utilisées pour l'apprentissage du modèle, et celles utilisées pour la détection de déperissement. Il contient l'index de la première date à partir de laquelle le déperissement est détecté. Sur cette zone, il y a assez de dates valides pour que l'ensemble des pixels terminent leur apprentissage avant la première date de 2018 (le paramètre **min_last_date_training** est fixé à 2018-01-01 par défaut ce qui permet d'avoir un recul de deux ans d'images satellites SENTINEL-2), ils ont donc tous la même valeur sauf les zones "sans données" qui correspondent aux zones détectées comme "sol nu / coupe" très tôt, qui sont donc masquées sur la quasi-totalité des dates et qui n'ont donc pas le nombre de dates valides minimum pour le calcul du modèle. 

Dans le dossier ForestMask, ouvrez également le raster valid_area_mask.tif. Il s'agit d'un raster binaire qui vaut 1 là où il y avait suffisamment de dates valides pour le calcul du modèle et 0 ailleurs.

#### Étape 3 : Détection du déperissement
Lors de cette étape, pour chaque date SENTINEL non utilisée pour l'apprentissage, l'indice de végétation réel est comparé à l'indice de végétation prédit à partir des modèles calculés dans l'étape précèdente. Si la différence dépasse un seuil, une anomalie est détectée. Si trois anomalies successives sont détectées, le pixel est considéré comme dépérissant. Si après avoir été détecté comme déperissant, le pixel a trois dates successives sans anomalies, il n'est plus considéré comme dépérissant. N'hésitez pas à consulter le [guide d'utilisation](https://gitlab.com/raphael.dutrieux/fordead_package/-/blob/master/docs/user_guides/03_decline_detection.md) de cette étape.

Pour effectuer cette étape, ajouter au script :
- Pour importer la fonction
```bash
from fordead.steps.step3_decline_detection import decline_detection
```
- Pour lancer la fonction
```bash
decline_detection(data_directory = data_directory)
```
Puis, relancez le script depuis l'invité de commande :
```bash
python <nom du script.py>
```

##### Observation des sorties
Pour chaque date postérieure à la date renseignée par le paramètre **min_last_date_training**, un raster Anomalies_<date>.tif est exporté dans le dossier **DataAnomalies**. 
- Ouvrez dans QGIS le raster __Anomalies_2018-07-27.tif__.
- Mettez en regard ces résultats avec l'indice de végétation et le masque calculé pour la date et ouvert précédemment, ainsi que l'image en RGB.
On peut voir que des anomalies sont détectées même là où les données sont masquées, comme pour les nuages sur la gauche de l'image, où les zones détectées comme sol nu. Ces anomalies ne sont bien entendu pas prises en compte. Les anomalies pouvant correspondre à des dégats de scolytes sont celles qui ne sont pas masquées.

Un autre dossier a été crée, DataDecline. Les rasters de ce dossier contiennent les informations relatives à la détection de dépérissement à partir des anomalies observées précédemment. Ces rasters sont exactement sous la même forme que les rasters dans DataSoil observés lors de l'étape 1. La seule différence est que un "retour à la normale" est possible. Une fois que le sol est détecté, l'état "sol nu" est permanent, tandis que pour le dépérissement, un pixel détecté comme dépérissant peut retourner à l'état non-dépérissant s'il y a trois dates successives sans anomalies. Cela permet d'éviter des faux positifs causés par des stress hydriques importants mais temporaires et ne causant pas de dépérissement.
Les informations de ces rasters sont les suivantes :
- le raster state_decline.tif, un raster binaire qui vaut 1 pour les pixels dépérissants, 0 pour les pixels sains
- Le raster count_decline.tif compte le nombre d'anomalies successives pour les pixels sains dans state_decline, ou le nombre de dates sans anomalies successives pour les pixels dépérissants dans state_decline. Quand count_decline atteint trois, le pixel change d'état, de sain à dépérissant ou inversement.
- Le raster first_date_decline.tif contient l'index de la date de première anomalie. Si state_decline vaut 1, il s'agit alors de la date à partir de laquelle le dépérissement est détécté.

#### Étape 4 : Calcul du masque forêt
L'ensemble des calculs précedents sont réalisés sur l'ensemble des pixels de la zone d'étude. Cependant, en particulier lorsqu'on travaille sur de larges zones, il est nécessaire de définir les zones d'intérêts pour ne pas interpréter des résultats sur des zones urbaines, des cultures, etc...
Dans le cas du scolyte, on s'intéresse uniquement aux peuplements forestiers résineux. Cette étape permet de créer le masque forêt correspondant à notre zone d'intérêt. Vous pouvez consulter son [guide d'utilisation](https://gitlab.com/raphael.dutrieux/fordead_package/-/blob/master/docs/user_guides/04_compute_forest_mask.md).

Pour effectuer cette étape, ajouter au script :
- Pour importer la fonction
```bash
from fordead.steps.step4_compute_forest_mask import compute_forest_mask
```
- Pour lancer la fonction
```bash
compute_forest_mask(data_directory, forest_mask_source = 'BDFORET', 
                    dep_path = <MyWorkingDirectory>/A_DATA/VECTOR/departements-20140306-100m.shp,
                    bdforet_dirpath = <MyWorkingDirectory>/A_DATA/VECTOR/BDFORET)
```
Puis, relancez le script depuis l'invité de commande :
```bash
python <nom du script.py>
```

> **_NOTE :_** Il est possible d'utiliser cette étape déconnectée des autres en précisant le paramètre **path_example_raster** avec le chemin d'un raster "exemple" qui donnera son système de projection, sa résolution, son extent au masque produit. Ne pas renseigner ce paramètre ne pose pas de soucis puisque le chemin d'un raster exemple peut être récupéré depuis les étapes précédentes par le biais du fichier TileInfo.

##### Observation des sorties
Cette étape permet d'écrire un uniquement raster, Forest_Mask.tif dans le dossier ForestMask. Ouvrez ce raster. Il s'agit d'un raster binaire qui vaut 1 dans la zone d'intérêt, 0 ailleurs. Avec les paramètres renseignés ici, il est crée à partir de la rasterisation de la BD Forêt de l'IGN en gardant uniquement les peuplements résineux. 

## Visualisation des résultats

Les étapes réalisées précédemment ont permis d'obtenir l'ensemble des résultats relatifs à la détection de scolytes, mais sous une forme difficile à analyser. Le package contient certains outils permettant de visualiser les résultats sous une forme plus digeste.

### Création d'un timelapse

Pour commencer, nous allons créer un timelapse de la détection sur la zone analysée. Pour ce faire, ajouter dans le script :
- Pour importer la fonction
```bash
from fordead.visualisation.create_timelapse import create_timelapse
```
- Pour ajouter les paramètres nécéssaires :
```bash
shape_path = "<MyWorkingDirectory>/A_DATA/VECTOR/Zones_Etude/ZoneEtude.shp"
obs_terrain_path = "<MyWorkingDirectory>/A_DATA/VECTOR/ValidatedScolytes.shp"
```
- Pour lancer la fonction :
```bash
create_timelapse(data_directory = data_directory,shape_path = shape_path, obs_terrain_path = obs_terrain_path)
```

Cette fonction prend en entrée un shapefile avec un champ "id" dans lequel il peut y avoir un ou plusieurs polygones et écrit pour chaque polygone un fichier <id>.html dans le dossier "Timelapses". Elle est plutôt pensée pour visualiser les résultats sur une zone réduite à partir des résultats d'une tuile entière, il est recommandé d'éviter de lancer cette opération avec des polygones de plus d'une vingtaine de km². Cependant, on travaille ici déjà sur une zone réduite, en utilisant un shapefile d'un seul polygone couvrant l'ensemble de la zone. Le timelapse devrait se lancer automatiquement, sinon ouvrez le fichier <id>.html (il est possible que sa lecture fonctionne mieux sous Chrome).

Une fois le timelapse ouvert, faites glisser le slider en bas de l'image pour vous déplacer temporellement dans l'animation. Les polygones noirs correspondent aux zones détectées comme sol nu, les polygones jaunes correspondent aux zones détectées comme dépérissantes et les polygones bleus correspondent aux coupes sanitaires, c'est à dire les zones détectées comme sol-nu/coupe après avoir été détectées comme atteintes.

Les données d'observation sur le terrain sont également affichées, passez la souris sur ces polygones pour obtenir leurs informations : <stade de scolyte> | <organisme à l'origine de la donnée> : <date d'observation>. Sur cette zone, on peut observer des zones saines en vert foncé et des zones scolytées au stade rouge en rouge.

Vous pouvez également zoomer sur la zone souhaitée en maintenant le clique appuyé tout en délimitant une zone. Vous pouvez ensuite dézoomer en double cliquant sur l'image. Passer la souris sur un pixel permet également d'obtenir ses informations :
- x : coordonnées en x
- y : coordonnées en y
- z : [<réflectance dans le rouge>,<réflectance dans le vert>,<réflectance dans le bleu>], c'est à dire la valeur de la bande SENTINEL correspondante à la date donnée.

Les résultats apparaissent à la date de la première anomalie, confirmée par la suite. Les fausses détections liées à un stress hydrique temporaire et corrigées par la suite n'apparaissent pas. De même, pour les dernières dates, il peut y avoir des anomalies n'apparaissant pas encore par manque de dates valides pour confirmer la détection.

Prenez le temps d'explorer cet outil et les résultats de la détection. Vous pouvez remarquer que les polygones observés comme atteints sur le terrain sont détectés comme atteints avant la date d'observation, tandis que les polygones observés comme sains sont encore sains à la date d'observation, mais pas forcément par la suite.

### Visualisation de la série temporelle de pixels en particulier
Lors de la visualisation du timelapse, vous avez pu vous poser des questions sur les résultats de pixels en particulier. L'outil suivant va permettre d'afficher l'ensemble de la série temporelle utilisée pour un pixel en particulier, mis en relation avec les résultats de l'algorithme.
Pour utiliser cet outil, ajouter dans le script :

- Pour importer la fonction
```bash
from fordead.visualisation.vi_series_visualisation import vi_series_visualisation
```
- Pour lancer la fonction :
```bash
vi_series_visualisation(data_directory = data_directory)
```

