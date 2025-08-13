from path import Path
import re

md_files = list(Path("docs").absolute().walkfiles("*.md"))

# # make title anchors
# for m in md_files:
#     with open(m, "r") as f:
#         content = f.read()
#     if (not content.startswith("---")) and (not content.startswith("# ")):
#         title = " ".join(m.stem.split("_"))
#         content = f"# {title}\n{content}"
#     with open(m, "w") as f:
#         f.write(content)

url = Path("https://fordead.gitlab.io/fordead_package/docs/user_guides/english/01_compute_masked_vegetationindex/")
url = Path("https://fordead.gitlab.io/fordead_package/docs/Tutorial/02_train_model")
m = Path("/media/DATA/boissieu/git/fordead_package/docs/Tutorials/Dieback_Detection/01_compute_masked_vegetationindex.md")

url_file = url.replace("https://fordead.gitlab.io/fordead_package/", "").absolute().with_suffix(".md")

url_file.relpath(m.dirname())



for m in md_files:
    with open(m, "r") as f:
        content = f.read()

    content = (
        content
        .replace("get_sen_intersection_points", "process_points")
        .replace("get_sen_intersection", "get_sen_obs_intersection")
    )
    # links = re.findall(r"\[(.*)\]\((.*)\)", content)

    pattern = re.compile(r"\[(.*)\]\((.*)\)")
    pattern = re.compile(r"(\[([^\]]*)\])(\(([^\)]+)\)|\[([^\]]+)\])")
    # pattern.findall("> **_Fonctions utilisées :_** [TileInfo()](docs/API_Reference/fordead/import_data/#tileinfo), méthodes de la classe TileInfo [import_info()](docs/API_Reference/fordead/import_data/#import_info), [add_parameters()](docs/API_Reference/fordead/import_data/#add_param)")

    for match in pattern.finditer(content):
        _, _, _, url, _ = match.groups()
        if url is not None and url.startswith("https://fordead.gitlab.io/fordead_package/docs"):
           parts = url.split("#")
           url_file = Path(parts[0]).replace("https://fordead.gitlab.io/fordead_package/", "").absolute().with_suffix(".md")
           if url_file.exists():
            rel_path = url_file.relpath(m.dirname())
            if len(parts) == 2:
                rel_path = f"{rel_path}#{parts[1]}"
            content = content.replace(f"({url})", f"({rel_path})")

        if url is not None and url.startswith("docs/API_Reference/fordead"):
            newurl = re.sub(r"/", ".", url)
            newurl = (
                newurl.replace("#", "")
                .replace("docs.API_Reference.", "")
                .replace("import_data.tileinfo", "import_data.TileInfo")
                .replace("import_data.save_info", "import_data.TileInfo.save_info")
                .replace("import_data.delete_dirs", "import_data.TileInfo.delete_dirs")
                .replace("import_data.import_info", "import_data.TileInfo.import_info")
                .replace(
                    "import_data.add_parameters", "import_data.TileInfo.add_parameters"
                )
                .replace(
                    "import_data.import_stackedmaskedvi",
                    "import_data.import_stackedmaskedVI",
                )
                .replace(
                    "fordead.dieback_detection.prediction_vegetation_index",
                    "fordead.model_vegetation_index.prediction_vegetation_index",
                )
                .replace(
                    "fordead.reflectance_extraction.get_polygons_from_sentinel_planetComp",
                    "fordead.stac.stac_module.get_polygons_from_sentinel_planetComp",
                )
            )
            content = content.replace(f"({url})", f"[{newurl}]")
    with open(m, "w") as f:
        f.write(content)
