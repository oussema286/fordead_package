# ENGLISH
# fordead : a python package for forest change detection from SENTINEL-2 images

The `fordead` package has been developed for the detection of changes in forests from SENTINEL-2 time series, in particular in the context of a bark beetle health crisis on spruce trees. Based on functions simplifying the use of SENTINEL-2 satellite data, it allows the mapping of bark beetle forest disturbances since 2018. However, except for the masks used which are certainly too specific to the study of coniferous forests, the rest of the process can probably be used for other issues. 

## Installation
### Conda install (recommended)

From the command prompt, go to the directory of your choice and run the following commands:
```bash
git clone https://gitlab.com/fordead/fordead_package.git
cd fordead_package
conda env create --name fordead_env
conda activate fordead_env
pip install .
```

## Forest disturbance detection

![diagramme_general_english](docs/user_guides/english/Diagrams/Diagramme_general.png "diagramme_general_english")

The detection of Forest disturbance is done in five steps.
- [The calculation of vegetation indices and masks for each SENTINEL-2 date](https://fordead.gitlab.io/fordead_package/docs/user_guides/01_compute_masked_vegetationindex/)
- [The training by modeling the vegetation index pixel by pixel from the first dates](https://fordead.gitlab.io/fordead_package/docs/user_guides/02_train_model/)
- [Detecting anomalies by comparing the vegetation index predicted by the model with the actual vegetation index](https://fordead.gitlab.io/fordead_package/docs/user_guides/03_decline_detection/)
- [Creating a forest mask, which defines the areas of interest](https://fordead.gitlab.io/fordead_package/docs/user_guides/04_compute_forest_mask/)
- [The export of results as shapefiles allowing to visualize the results with the desired time step](https://fordead.gitlab.io/fordead_package/docs/user_guides/05_export_results/)

It is possible to correct the vegetation index using a correction factor calculated from the median of the vegetation index of the large-scale stands of interest, in which case the mask creation step must be performed before the model training step.

All the documentation and user guides for these steps are available at [site](https://fordead.gitlab.io/fordead_package/).

# FRANCAIS
# fordead : un package python pour la détection de changement en forêt à partir d'images SENTINEL-2

Le package `fordead` a été développé pour la détection de changements en forêt à partir de série temporelles SENTINEL-2, en particulier dans un contexte de crise sanitaire du scolyte sur les épicéas. A partir de fonctions simplifiant l'utilisation de données satellites SENTINEL-2, il permet la cartographie des déperissements liés aux scolytes depuis 2018. Cependant, excepté les masques utilisés qui sont certainement trop spécifiques à l'étude de peuplements résineux, le reste des étapes du processus peuvent également être utilisées pour d'autres contextes. 

## Installation
### Installation conda (recommended)

Depuis l'invite de commande, placer vous dans le répertoire de votre choix et lancez les commandes suivantes :
```bash
git clone https://gitlab.com/fordead/fordead_package.git
cd fordead_package
conda env create --name fordead_env
conda activate fordead_env
pip install .
```

## Utilisation pour la détection de déperissement

![diagramme_general_french](docs/user_guides/french/Diagrams/Diagramme_general.png "diagramme_general_french")

La détection du déperissement se fait en cinq étapes.
- [Le calcul des indices de végétation et des masques pour chaque date SENTINEL-2](https://fordead.gitlab.io/fordead_package/docs/user_guides/01_compute_masked_vegetationindex/)
- [L'apprentissage par modélisation de l'indice de végétation pixel par pixel à partir des premières dates](https://fordead.gitlab.io/fordead_package/docs/user_guides/02_train_model/)
- [La détection du déperissement par comparaison entre l'indice de végétation prédit par le modèle et l'indice de végétation réel](https://fordead.gitlab.io/fordead_package/docs/user_guides/03_decline_detection/)
- [La création du masque forêt, qui définit les zones d'intérêt](https://fordead.gitlab.io/fordead_package/docs/user_guides/04_compute_forest_mask/)
- [L'export de sorties permettant de visualiser les résultats au pas de temps souhaité](https://fordead.gitlab.io/fordead_package/docs/user_guides/05_export_results/)

Il est possible de corriger l'indice de végétation à l'aide d'un facteur de correction calculé à partir de la médiane de l'indice de végétation des peuplements d'intérêt à large échelle, auquel cas l'étape de création du masque doit être réalisée avant l'étape d'apprentissage du modèle.

L'ensemble de la documentation ainsi que les guides utilisateurs de ces étapes sont disponibles sur le [site](https://fordead.gitlab.io/fordead_package/).
