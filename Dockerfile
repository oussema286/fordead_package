###############
# How to build
###############
# docker build -t fordead:$(date +%y.%m.%d) .
### When all is good
# docker tag fordead:$(date +%y.%m.%d) registry.gitlab.com/fordead/fordead_package:$(date +%y.%m.%d)
# fordead_version=`grep __version__ fordead/_version.py| sed -E 's/.*([0-9]+\.[0-9]+\.[0-9]+).*/\1/'` && \
# docker tag fordead:$(date +%y.%m.%d) registry.gitlab.com/fordead/fordead_package:${fordead_version}
# docker tag fordead:$(date +%y.%m.%d) registry.gitlab.com/fordead/fordead_package:latest
# docker push registry.gitlab.com/fordead/fordead_package:$(date +%y.%m.%d)
# fordead_version=`grep __version__ fordead/_version.py| sed -E 's/.*([0-9]+\.[0-9]+\.[0-9]+).*/\1/'` && \
# docker push registry.gitlab.com/fordead/fordead_package:${fordead_version}
# docker push registry.gitlab.com/fordead/fordead_package:latest

# from condaforge/miniforge3
# add environment.yml /tmp/environment.yml
# run mamba env create -n fordead -f /tmp/environment.yml \
#     && conda env list
# shell ["/bin/bash", "--login", "-c"]
# run conda init bash
# # activates fordead by default, avoids starting line by `run conda activate fordead && ...`
# run echo "conda activate fordead" >> ~/.bashrc
# ENTRYPOINT ["conda", "run", "-n", "fordead", "--live-stream"]

# much smaller than conda-forge/miniforge3
FROM mambaorg/micromamba
COPY --chown=$MAMBA_USER:$MAMBA_USER environment.yml /tmp/environment.yml
ENV ENV_NAME=fordead
RUN micromamba create -y -n ${ENV_NAME} -f /tmp/environment.yml && \
    micromamba install -y -n ${ENV_NAME} -c conda-forge pytest && \
    micromamba clean --all --yes
ARG MAMBA_DOCKERFILE_ACTIVATE=1
ARG FORDEAD_BRANCH=master
RUN micromamba env list
RUN pip install "git+https://gitlab.com/fordead/fordead_package.git@${FORDEAD_BRANCH}" --no-deps