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

## Utilisation
### A partir d'un script

```bash
from fordead.steps.step5_export_results import export_results
export_results(
    data_directory = <data_directory>,
    start_date = <start_date>,
    end_date = <end_date>,
    frequency= <frequency>,
    export_soil = <export_soil>,
    multiple_files = <multiple_files>
    )
```

### A partir de la ligne de commande

```bash
fordead export_results [OPTIONS]
```

Voir documentation détaillée sur le [site](https://fordead.gitlab.io/fordead_package/docs/cli/#export_results)

## Détail du fonctionnement

### Imports des informations sur les traitements précédents et suppression des résultats obsolètes si existants
Les informations relatives aux traitements précédents sont importés (paramètres, chemins des données, dates utilisées...) afin de pouvoir importer l'ensemble des résultats.
> **_Fonctions utilisées :_** [TileInfo()](https://fordead.gitlab.io/fordead_package/reference/fordead/ImportData/#tileinfo), méthodes de la classe TileInfo [import_info()](https://fordead.gitlab.io/fordead_package/reference/fordead/ImportData/#import_info)

### Import des résultats de la détection 
Les résultats des étapes précedentes sont importées.
> **_Fonctions utilisées :_** [import_soil_data()](https://fordead.gitlab.io/fordead_package/reference/fordead/ImportData/#import_soil_data), [import_decline_data()](https://fordead.gitlab.io/fordead_package/reference/fordead/ImportData/#import_decline_data), [import_forest_mask()](https://fordead.gitlab.io/fordead_package/reference/fordead/ImportData/#import_forest_mask)

### Détermination des périodes pour aggréger les résultats
Les résultats seront donné par aggrégation selon la période à laquelle surviennent les premières anomalies à la fois pour la détection de sol et de déperissement. Ces périodes sont déterminées à partir de la fréquence indiquée par le paramètre **frequency**, la date de début **start_date** et la date de fin **end_date**. Les périodes avant la première date SENTINEL utilisée, ou après la dernière, si elles existent, sont retirées puisqu'elles ne peuvent correspondre à aucun résultat.
> **_Fonctions utilisées :_** [get_bins()](https://fordead.gitlab.io/fordead_package/reference/fordead/writing_data/#get_bins)

### Conversion des dates de premières anomalies en nombre de jours depuis 2015-06-23
Les dates de premières anomalies, stockées sous forme d'index parmi les dates utilisées, sont converties en nombre de jours depuis un jour de référence "2015-06-23" correspondant au lancement du premier satellite SENTINEL-2. Ainsi ces dates peuvent être comparées avec les limites des périodes déterminées précedemment.
> **_Fonctions utilisées :_** [convert_dateindex_to_datenumber()](https://fordead.gitlab.io/fordead_package/reference/fordead/writing_data/#convert_dateindex_to_datenumber)

### Si export en plusieurs fichiers :
- Pour chaque période, il est vérifié si le pixel a sa première anomalie avant la fin de la période. On obtient ainsi l'information pour chaque pixel "Sain", ou "Atteint" si **export_soil** vaut False, ou "Sain", "Atteint", "Coupe", Coupe sanitaire" sinon. 
- Cette information est vectorisée en utilisant uniquement la zone étudiée (au sein du masque forêt et disposant d'assez de dates valides pour modéliser l'indice de végétation). Les pixels sains sont également ignorés.
> **_Fonctions utilisées :_** [get_state_at_date()](https://fordead.gitlab.io/fordead_package/reference/fordead/writing_data/#get_state_at_date)
- Ce vecteur est écrit pour chacune des périodes en utilisant comme nom de fichier la date limite de la fin de la période.

## Si export en un seul fichier :
- Les pixels sont aggrégés selon la période durant laquelle survient la première anomalie. 
- Le résultat est vectorisé, en ignorant les pixels en dehors des périodes déterminées et les pixels en dehors de la zone étudiée (au sein du masque forêt et disposant d'assez de dates valides pour modéliser l'indice de végétation).
> **_Fonctions utilisées :_** [get_periodic_results_as_shapefile()](https://fordead.gitlab.io/fordead_package/reference/fordead/writing_data/#get_periodic_results_as_shapefile)
- Le vecteur résultat est écrit en un unique fichier vectoriel donnant les résultats du déperissement.

Si **export_soil** vaut True, la même opération est réalisée en utilisant les résultats de la détection de sol nu et les résultats sont écrits dans un second fichier vectoriel.


