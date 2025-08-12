"""Generate the code reference pages in directory API_Reference (after removing dir if exists).
This is here to by compatible with mkdoc-static-i18n: https://github.com/ultrabug/mkdocs-static-i18n/issues/263
This script should be run before `mkdocs build`
"""

from pathlib import Path
import shutil

import mkdocs_gen_files

shutil.rmtree("docs/API_Reference", ignore_errors=True)
for path in sorted(Path("fordead").rglob("*.py")):  #
    module_path = path.relative_to(".").with_suffix("")  #
    doc_path = path.relative_to(".").with_suffix(".md")  #
    full_doc_path = Path("API_Reference", doc_path)  #
    parts = list(module_path.parts)
    
    if parts[-1] == "__init__":  #
        # parts = parts[:-1]
        continue
    elif parts[-1] == "__main__":
        continue


    with mkdocs_gen_files.open(full_doc_path, "w") as fd:  #
        IDENTIFIER = ".".join(parts)  #
        print("::: " + IDENTIFIER)
        print("::: " + IDENTIFIER, file=fd)  #

    mkdocs_gen_files.set_edit_path(full_doc_path, path)