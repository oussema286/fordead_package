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
Vous pouvez retrouver le guide d'utilisation de cette étape [ici](https://gitlab.com/raphael.dutrieux/fordead_package/-/blob/master/docs/user_guides/01_compute_masked_vegetationindex.md).
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

