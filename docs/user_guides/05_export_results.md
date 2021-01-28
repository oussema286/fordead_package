## ÉTAPE 5 : step5_export_results.py
Cette étape permet de sortir les résultats sous la forme désirée par l'utilisateur, pour la période et fréquence souhaitée. 

#### ENTRÉES
Les paramètres en entrée sont :
- **data_directory** : Le chemin du dossier de sortie dans lequel sera écrit les résultats
- **start_date** : Date de début, au format AAAA-MM-JJ
- **end_date** : Date de fin, au format AAAA-MM-JJ
- **frequency** : Fréquence à laquelle les résultats sont exportés. Peut être "sentinel", auquel cas la fréquence correspond aux dates SENTINEL, ou une fréquence telle qu'acceptée par la fonction pandas.date_range (ex : 'M' (tous les mois), '3M' (tous les trois mois), '15D' (tous les 15 jours)")
- **export_soil** : Si True, les résultats relatifs à la détection de sol nu/coupes sont exportés également.
- **multiple_files** : Si True, un shapefile sera exporté par période, où chaque polygone correspond à l'état de la zone à la fin de la période. Sinon, un seul shapefile est exporté et les polygones contiennent la période à laquelle la première anomalie a été détecté.

#### SORTIES
Les sorties de cette cinquième étape, dans le dossier data_directory/Results, sont :
- si **multiple_files** vaut False :
    - le shapefile periodic_results_decline, dont les polygones contiennent la période à laquelle la première anomalie a été détecté pour les zones dépérissantes. Les zones atteintes avant start_date ou après end_date ne sont pas représentées.
    - si export_soil est activé, le shapefile periodic_results_soil dont les polygones contiennent la période à laquelle la première anomalie de sol a été détecté pour les zones détectées comme sol nu/coupe. Les zones à nu avant start_date ou après end_date ne sont pas représentées.
- si **multiple_files** vaut True :
    - Un shapefile par période dont le nom est la date de fin de la période (par exemple, avec start_date = 2018-01-01, end_date = 2018-04-01 et frequency = "M", on aura les fichiers suivants : 2018-01-30.shp, 2018-02-28.shp et 2018-03-31.shp. Chaque shapefile contient des polygones correspondant à l'état du peuplement à la fin de la période, même si les premières anomalies ont lieu avant start_date. L'état peut être Atteint, Coupe ou Coupe sanitaire si export_soil est activé, ou simplement "Atteint" sinon.
