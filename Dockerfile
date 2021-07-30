from continuumio/miniconda3:latest
add environment.yml /environment.yml
run ls /
run apt-get update \
    && apt-get install -y gcc g++ git unzip libgtk2.0-0 libsm6 libxft2 curl \
    && conda env create -n fordead -f /environment.yml \
    && conda env list
shell ["/bin/bash", "--login", "-c"]
run conda init bash
run echo "conda activate fordead" > ~/.bashrc
run conda activate fordead && pip install git+https://github.com/RaphaelDutrieux/portray python-markdown-math mdx-breakless-lists mkdocs-click
run conda env list
