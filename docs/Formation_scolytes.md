# <div align="center"> Détection des foyers de mortalité dans les massifs de conifères par imagerie satellite Sentinel-2 </div>

<div align="center"> Equipe de formation INRAE : Raphaël Dutrieux, Forian de Boissieu, Jean-Baptiste Feret, Kenji Ose </div>

## <div align="center">TP-02 : Utilisation du package `fordead` : détection de déperissement en forêt à partir de séries temporelles SENTINEL-2</div>
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
conda activate ForDeadEnv
```

### Utilisation du package `fordead`

La détection du déperissement permet d'utiliser l'ensemble des données SENTINEL-2 depuis le lancement du premier satellite. Même en prenant une seule tuile, un tel jeu de données pèse plusieurs centaines de gigaoctets et prend plusieurs heures de temps de calcul pour réaliser l'ensemble des étapes de détection du déperissement. Pour cette raison, un jeu de données plus réduit a été préparé pour cette formation. Il contient l'ensemble des données SENTINEL-2 disponible sur une zone d'étude restreinte, en croppant à partir des données de la tuile. Cette zone est touchée par les scolytes, et contient plusieurs polygones de données de validation, ce qui en fait un bon exemple pour l'application de la détection de déperissement et la visualisation des résultats. 

- Créer un script python en créant un nouveau fichier de texte dans le dossier de votre choix, et en le nommant _detection_scolytes.py_ (ou le nom de votre choix, mais avec l'extension .py)
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
- Pour choisir les paramètres en entrée
```bash
input_directory = "<chemin dossier des données SENTINEL de la tuile>"
data_directory = "<chemin dossier d'écriture des résultats>"
```
- Pour lancer la fonction
```bash
compute_masked_vegetationindex(input_directory = input_directory, data_directory = data_directory)
```
Puis lancer le script python depuis l'invité de commande en vous plaçant dans le répertoire du script en utilisant la commande suivante :
```bash
cd <chemin complet du dossier>
```
Puis lancer le script :
```bash
python <nom du script.py>
```
##### Faire tourner l'étape en lançant la fonction depuis l'invité de commande
Il est également possible d'appliquer la même étape en passant par l'invité de commande.
Depuis l'invité de commande, placez vous dans le dossier fordead_package/fordead/steps. La commande suivante permet d'afficher l'aide :
```bash
python step1_compute_masked_vegetationindex.py -h
```
A partir de l'aide, lancez la fonction en appliquant vos paramètres. Exemple :
```bash
python step1_compute_masked_vegetationindex.py -i <chemin dossier des données SENTINEL de la tuile> -o <chemin dossier d'écriture des résultats>
```

---------

Vous remarquerez que si vous avez utilisé les même paramètres dans les deux cas, il s'affiche "0 new SENTINEL dates" et le programme tourne plus rapidement la deuxième fois, car les indices de végétation déjà calculés ne sont pas recalculés. En revanche, si vous changez les paramètres, les résultats précédants seront supprimés et remplacés.
Les paramètres input_directory et data_directory sont les deux seuls à ne pas connaître de valeur par défaut puisqu'elles dépendent de l'emplacement de vos fichiers. Ce sont donc les deux seuls paramètres à renseigner obligatoirement, mais il est tout de même possible de modifier les autres paramètres. A l'aide du guide d'utilisateur, vérifiez que vous comprenez le sens des différents paramètres et n'hésitez pas à poser des questions si ce n'est pas le cas !

L'ensemble des étapes de la détection peuvent se réaliser de manière identique depuis l'invité de commande, ou par import des différentes fonctions dans un script. Dans la suite de ce TD, nous nous focaliseront sur le script en le complétant au fur et à mesure.

##### Observation des sorties
Pour mieux vous représenter les sorties de cette étape, lancez QGIS et ajoutez les rasters VegetationIndex/VegetationIndex_2018-07-27.tif et Mask/Mask_2018-07-27.tif.
+ Ajouter bandes SENTINEL et créer raster virtuel RGB ?
Les rasters dans le dossier DataSoil contiennent les informations relatives à la détection du sol nu. Ce sol détecté peut correspondre à des zones non forestières, à des peuplements feuillus dont le sol est détecté en hiver, ou des coupes rases. Il y a trois rasters, qui ensemblent permettent de reconstituer l'ensemble de l'information, et de la mettre à jour avec l'arrivée de nouvelles dates SENTINEL :
- Le raster count_soil.tif compte le nombre d'anomalies de sol successives.
- Lorsque count_soil atteint 3, pour trois anomalies successives, le raster state_soil.tif passe de 0 à 1. Les pixels avec la valeur 1 correspondent donc à ceux détectés comme sol nu / coupe au bout de l'analyse de l'ensemble des dates.
- Le raster first_date_soil.tif contient l'index de la date de première anomalie de sol. Si state_soil vaut 1, il s'agit alors de la date à partir de laquelle le sol est détectée. 
Ces rasters peuvent être difficiles à analyser puisque, n'étant pas possible de mettre une date dans un raster, le raster first_date_soil contient **l'index** de la date qui peut être interprété par le package dans les étapes suivantes.

Après avoir observé les rasters, il est souhaitable de supprimer les couches dans QGIS afin d'éviter les erreurs si le script python tente de les supprimer alors qu'elles sont en cours d'utilisation.

#### Étape 2 : Modélisation du comportement périodique de l'indice de végétation 
Pour modéliser le comportement normal de l'indice de végétation, on utilise seulement les dates SENTINEL les plus anciennes, en faisant l'hypothèse qu'elles sont antérieures à un possible déperissement. La fonction harmonique suivante est ajustée à ces données :
𝒇(𝒕)=𝒂𝟏+𝒃𝟏.𝐬𝐢𝐧⁡(𝟐𝝅𝒕/𝑇)+𝒃𝟐.𝐜𝐨𝐬⁡(𝟐𝝅𝒕/𝑇)+𝒃𝟑.𝐬𝐢𝐧⁡(𝟒𝝅𝒕/𝑇)+𝒃𝟒.𝐜𝐨𝐬⁡(𝟒𝝅𝒕/𝑇) où T = 365,25
Vous pouvez retrouver le [guide d'utilisation de cette étape](https://gitlab.com/raphael.dutrieux/fordead_package/-/blob/master/docs/user_guides/02_train_model.md).

Pour effectuer cette étape, ajoutez dans le script :
- Pour importer la fonction
```bash
from fordead.steps.step2_TrainFordead import train_model
```
- Pour lancer la fonction
```bash
train_model(data_directory = data_directory)
```
Puis, comme pour l'étape 1, relancez le script depuis l'invité de commande :
```bash
python <nom du script.py>
```

Le reste des paramètres connaissent une valeur par défaut dans la fonction et n'ont pas besoin d'être renseignées. Ces valeurs par défaut ont été déterminées de manière empirique pour la problématique du scolyte et peuvent ne pas être optimales selon la localisation ou la problématique donnée. Le [guide d'utilisation](https://gitlab.com/raphael.dutrieux/fordead_package/-/blob/master/docs/user_guides/02_train_model.md) donne des détails sur les différents paramètres, lisez le et vérifiez que vous comprenez bien leur sens.

> **_NOTE :_** Si l'utilisateur ne souhaite pas utiliser la première étape et choisit de calculer ses propres indices de végétations et masques. Il peut sauter l'étape 1 et simplement donner le chemin de son dossier d'indices de végétation avec le paramètre **path_vi** et son dossier de masques avec **path_masks**. Il suffit simplement que le nom des rasters contiennent la date sous un des formats suivants : AAAA-MM-JJ, AAAA_MM_JJ, AAAAMMJJ, JJ-MM-AAAA, JJ_MM_AAAA ou JJMMAAAA.

##### Observation des sorties
Les résultats de cette étapes sont dans le dossier DataModel. 
Ouvrez le raster coeff_model.tif dans QGIS. Faites un clique droit sur un des pixels, vous pouvez constater qu'il s'agit d'un raster à cinq bandes. QGIS affiche une image en RGB à partir des trois premières bandes. Chacune des bandes correspond à un des coefficients (a1, b1, b2, b3, b4) du modèle (voir équation). On a bien un modèle différent par pixel ce qui permet qu'il soit adapté aux conditions de ce pixel. On peut en effet imaginer que la composition du peuplement, sa surface terrière, sa pente, son exposition ont probablement un rôle à jouer dans la valeur donnée des indices de végétation. A partir de ces coefficients, il est possible de prédire l'indice de végétation à n'importe quelle date, pour un peuplement sain.

Ouvrez maintenant le raster first_detection_date_index.tif. Il permet de connaître pour chaque pixel les dates utilisées pour l'apprentissage du modèle, et celles utilisées pour la détection de déperissement. Il contient l'index de la première date à partir de laquelle le déperissement est détecté. Sur cette zone, il y a assez de dates valides pour que l'ensemble des pixels terminent leur apprentissage avant la première date de 2018 (le paramètre **min_last_date_training** est fixé à 2018-01-01 par défaut ce qui permet d'avoir un recul de deux ans d'images satellites SENTINEL-2), ils ont donc tous la même valeur sauf les zones "sans données" qui correspondent aux zones détectées comme "sol nu / coupe" très tôt, qui sont donc masquées sur la quasi-totalité des dates et qui n'ont donc pas le nombre de dates valides minimum pour le calcul du modèle. 

#### Étape 3 : Détection du déperissement
Lors de cette étape, pour chaque date SENTINEL non utilisée pour l'apprentissage, l'indice de végétation réel est comparé à l'indice de végétation prédit à partir des modèles calculés dans l'étape précèdente. Si la différence dépasse un seuil, une anomalie est détectée. Si trois anomalies successives sont détectées, le pixel est considéré comme dépérissant. Si après avoir été détecté comme déperissant, le pixel a trois dates successives sans anomalies, il n'est plus considéré comme dépérissant. N'hésitez pas à consulter le [guide d'utilisation](https://gitlab.com/raphael.dutrieux/fordead_package/-/blob/master/docs/user_guides/03_decline_detection.md) de cette étape.
