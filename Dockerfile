from conda/miniconda3:latest
add environment.yml /environment.yml
run ls /
run apt-get update \
    && apt-get install -y gcc g++ git unzip libgtk2.0-0 libsm6 libxft2 curl \
    && conda env create -n fordead -f /environment.yml \
    && conda env list
run conda init bash \
    && conda activate fordead \
    && conda env list \
    && pip install git+https://github.com/RaphaelDutrieux/portray python-markdown-math mdx-breakless-lists mkdocs-click