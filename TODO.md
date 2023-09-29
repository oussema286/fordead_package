
# Faire un test gitlab-ci avec stac
Raphael a eu qq problèmes lors de l'installation (packages manquant, channel pas prioritaire, ...)
Un test en CI d'installation de l'environnement dev et du script de test stac pourrait vérifier si tout y est.

# Fonctions et classes

Dans la description ci-dessous, les input ont les dimensions nécessaires, voir s'il est possible de garder les mêmes fonctions mais avec des dimensions extra, i.e. en propageant les dimensions supplémentaires au résultat: apply along ou boucle for.

```python
compute_mask(xr[x, y, band], formula="B2>700, use_CLM=True) -> xr[x,y,band="FORDEAD_MASK"]

compute_soil(xr[x, y, band], formula="B5>700") -> xr[x,y,band="FORDEAD_SOIL"]

compute_vi(xr[x, y, band], vi="CRSWIR", formula=None) -> xr[x,y,band="FORDEAD_VI_{indice}"]
    si indice is None:
        Error("vi name must be specified")
    
    si indice in indice_db:
        si formula not None:
            Error("Indice name already in indice_db")
        sinon
            formula = indice_db[indice]
    
mask_vi(xr[x,y,band], vi="CRSWIR", mask_bands=["MASK"]) -> xr[x,y]

train_model(xr[x, y, band, t], vi="CRSWIR", ...) -> xr[x,y, band=[alpha_1, alpha_2, ..., enddate]] raster of parameters of the model and enddate
    mask_vi(xr[x,y,band,t], vi="CRSWIR", mask_bands=["MASK", "SOIL"])
    ...

predict(xr[x, y, band]) -> xr[x,y] anomaly raster
    mask_vi(xr[x,y,band,t], vi="CRSWIR", mask_bands=["MASK"])

add_asset(coll, xr[x,y,band,time], output_dir, band_parser):
    for t in xr.time:
        item = coll.filter(datetime=t)[0]
        for b in xr.band:
            band_file = write_tif(xr.sel(band=b), output_dir / item.id+f'_{b}.tif')
            asset = band_parser(band_file)
            item.add_asset(asset)


# en cours de construction
Class FordeadApp(config, coll=None):

    def __init__(self)
        if coll is not None:
            self.coll=coll
            config.pop("input_dir", None)
        self.config = config

    @class_method
    def from_file(cls, config_file):

        config = load(config_file)
        coll = load_coll
```

