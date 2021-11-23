from continuumio/miniconda3:latest
add environment.yml /environment.yml
run ls /
run apt-get update \
    && conda env create -n fordead -f /environment.yml \
    && conda env list
shell ["/bin/bash", "--login", "-c"]
run conda init bash
# run echo "conda activate fordead" >> ~/.bashrc # activates fordead by default, avoids starting line by `run conda activate fordead && ...`
run conda env list
run conda activate fordead && conda env list && pip install portray python-markdown-math mdx-breakless-lists mkdocs-click