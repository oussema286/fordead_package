# 1. Introduction

## 1.1. Préambule et contexte

Les problèmes sanitaires observés au cours des années passées dans les massifs forestiers français, européens et sur les autres continents, s’expliquent en partie par les changements climatiques qui s’accompagnent d’un dérèglement des précipitations et d’épisodes de sécheresse intense. Dans la région Grand-Est, ces épisodes de stress climatique répétés rendent les massifs particulièrement vulnérables aux attaques par des pathogènes et ravageurs, tels que le scolyte du pin, qui touche notamment très fortement les massifs d’épicéa ainsi que d’autres conifères.

Pour répondre aux enjeux de détection précoce et suivi des massifs touchés par ces problèmes sanitaires conduisant à une forte mortalité et se répétant depuis plusieurs années, des méthodes s’appuyant sur les données et outils d’observation de la Terre sont en préparation pour une mise en place opérationnelle d’un outil de suivi. L’analyse de données d’imagerie optique multispectrales satellite issue des capteurs Sentinel-2 apparaît comme particulièrement pertinente pour répondre à ces enjeux, mais soulève aussi un certain nombre de défis techniques pour la mise en place d’une méthode opérationnelle.

Plusieurs approches sont envisageables pour tirer parti des informations issues des données Sentinel-2 :

- Les méthodes ‘classiques’ d’analyse d’image basées sur une classification supervisée différenciant massifs sains et avec différents niveaux de dépérissement, appliquées à des acquisitions individuelles sont techniquement simples à mettre en œuvre, mais très limitées en raison du besoin en échantillons d’apprentissage représentatifs des différentes classes à identifier. De plus, dans leur implémentation la plus courante, ces méthode ne tirent pas parti de la dimension temporelle et ne permettent donc pas d’identifier les changements, à moins d'être répétées à différentes dates, pour pouvoir ensuite étudier l'évolution des cartes de classification, ce qui nécessite la mise à jour systématique de la base d’apprentissage.  
- Les méthodes s’appuyant sur les différences radiométriques observées entre deux dates (‘analyse diachronique’), appliquées à des indices de diversité appropriés, sont aussi très répandues. Cependant, comme pour les approches supervisées, la détection automatique doit s’appuyer sur un jeu d’apprentissage représentatif des différentes classes à identifier, et le choix des deux dates est à la fois déterminant, et limitant pour les phénomènes continus tels que le dépérissement des massifs forestiers. 
- Les méthodes permettant de tirer parti de tout ou partie d’une série temporelle d’indicateurs dérivés d’acquisition effectuées au cours d’une saison, d’une année, de plusieurs années. Ces méthodes sont particulièrement adaptées au suivi dynamique des massifs forestiers, et à la détection d’anomalies. Elles sont cependant plus complexes à mettre en œuvre, en raison du volume de données et des ressources informatiques nécessaires au calcul de ces séries temporelles, du travail de préparation et de filtrage des données, et des méthodes d’analyse de ces séries temporelles.

## 1.2. Objectifs
Les objectifs de ces travaux pratiques sont les suivants :

- Explorer les données disponibles à l’aide de plateformes de visualisation en ligne
- Accéder au téléchargement des données d’imagerie Sentinel-2 et préparer l’automatisation de cette tâche
- Préparer les données d’imagerie Sentinel-2 pour la mise en place de traitements pour la détection des foyers de scolytes : 
    - extraction d’une zone d'étude
    - empilement des couches
    - calcul d’indices de végétation
- Appliquer les méthodes les plus accessibles de détection de changement (classification supervisée & comparaison d’indices entre deux acquisitions a un an d’intervalle)
- Découvir des methods plus poussées permettant de tirer partie des series temporelles Sentinel-2, potentiellement plus puissantes mais aussi beaucoup plus demandeuses en termes de moyens de calcul et technicité. 
---
