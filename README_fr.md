# fordead : un package python pour la détection d'anomalies de végétation à partir d'images SENTINEL-2

Le package `fordead`, développé pour la détection d'anomalies de végétation à partir de séries temporelles SENTINEL-2, fournit des outils de surveillance pour répondre à la crise sanitaire des scolytes sur les épicéas en France. Il contient de nombreux outils qui simplifient l'utilisation des données satellitaires SENTINEL-2, et qui permettent la détection éventuelle d'anomalies dans d'autres contextes. 

La méthode proposée exploite des séries temporelles complètes SENTINEL-2 et ce, depuis le lancement du premier satellite en 2015. Elle permet de détecter des anomalies à l'échelle du pixel pour analyser des données d'archives ou procéder à une surveillance continue. Les détections sont alors mises à jour à chaque nouvelle acquisition SENTINEL-2.

## Utilisation pour la détection de déperissement

![diagramme_general_french](docs/user_guides/french/Diagrams/Diagramme_general.png "diagramme_general_french")

La détection du déperissement se fait en cinq étapes.
- [Le calcul des indices de végétation et des masques pour chaque date SENTINEL-2](https://fordead.gitlab.io/fordead_package/docs/user_guides/french/01_compute_masked_vegetationindex/)
- [L'apprentissage par modélisation de l'indice de végétation pixel par pixel à partir des premières dates](https://fordead.gitlab.io/fordead_package/docs/user_guides/french/02_train_model/)
- [La détection du déperissement par comparaison entre l'indice de végétation prédit par le modèle et l'indice de végétation réel](https://fordead.gitlab.io/fordead_package/docs/user_guides/french/03_decline_detection/)
- [La création du masque forêt, qui définit les zones d'intérêt](https://fordead.gitlab.io/fordead_package/docs/user_guides/french/04_compute_forest_mask/)
- (FACULTATIF) [Calcul d'un indice de confiance pour classifier selon l'intensité des anomalies](https://fordead.gitlab.io/fordead_package/docs/user_guides/french/05_compute_confidence/)
- [L'export de sorties permettant de visualiser les résultats au pas de temps souhaité](https://fordead.gitlab.io/fordead_package/docs/user_guides/french/06_export_results/)

Il est possible de corriger l'indice de végétation à l'aide d'un facteur de correction calculé à partir de la médiane de l'indice de végétation des peuplements d'intérêt à large échelle, auquel cas l'étape de création du masque doit être réalisée avant l'étape d'apprentissage du modèle.

L'ensemble de la documentation ainsi que les guides utilisateurs de ces étapes sont disponibles sur le [site](https://fordead.gitlab.io/fordead_package/).

Voici un example du résultat sur une zone atteinte par le scolyte :

Période de détection | Classe de confiance
:-------------------------:|:-------------------------:
![gif_results_original](docs/Tutorial/Figures/gif_results_original.gif "gif_results_original") | ![gif_results_confidence](docs/Tutorial/Figures/gif_results_confidence.gif "gif_results_confidence")

## Outils de visualisation

Le package contient également des outils de visualisation, le premier réalise un graphique de la série temporelle de l'indice de végétation pour un pixel en particulier, avec le modèle associé, le seuil de détection d'anomalies et la détection associée.

Pixel sain | Pixel atteint
:-------------------------:|:-------------------------:
![graph_healthy](docs/Tutorial/Figures/graph_healthy.png "graph_healthy") | ![graph_dieback](docs/Tutorial/Figures/graph_dieback.png "graph_dieback")

Le deuxième réalise un "timelapse" sur une petite zone pour visualiser les résultats à chaque date Sentinel-2 utilisée, avec le fond RGB Sentinel-2 et un curseur permettant de naviguer entre les dates. 

![gif_timelapse](docs/Tutorial/Figures/gif_timelapse.gif "gif_timelapse")

## Installation

Vous pourrez retrouver le guide d'installation [ici](https://fordead.gitlab.io/fordead_package/docs/Installation/).

## Tutoriel

Un tutoriel pour bien commencer et tester le package sur un jeu de donnée fourni est disponible [ici](https://fordead.gitlab.io/fordead_package/docs/Tutorial/00_Intro/).
