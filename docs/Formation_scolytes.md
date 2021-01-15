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
