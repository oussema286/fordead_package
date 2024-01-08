## Conda install (recommended)

Conda install is recommended as it will include all necessary dependencies (especially GDAL).

### Requirements
It is recommened with [mamba](https://github.com/mamba-org/mamba), that is much faster than conda to solve environment constraints.

If you already have a conda installed, [install mamba in base environment](https://mamba.readthedocs.io/en/latest/installation.html#existing-conda-install):
```bash
conda install mamba -n base -c conda-forge
```

If you do not have conda installed, we recommend installing [mambaforge](https://github.com/conda-forge/miniforge#mambaforge).

### Install

From the anaconda prompt or the miniconda prompt command invite, use the following commands to create a working environment :

```bash
mamba env create -n fordead -f https://gitlab.com/fordead/fordead_package/-/raw/master/environment.yml
conda activate fordead
```

The conda environment can be deleted using the following command :
```bash
conda env remove -n fordead
```

## Using Docker

It is also possible to use this package using a docker. The docker image associated with this package already includes a conda environment with python and required dependencies, allowing to run containers in  which to use this package.
To use this docker image, if you are on windows, you must first install [Docker Desktop](https://www.docker.com/products/docker-desktop).

Then use the following command to pull the docker image from this package's gitlab page.
```bash
docker pull registry.gitlab.com/fordead/fordead_package
```
Now you can create a container from the command line. By default docker containers can't access your directories, for it to be able to read and write data, you must specify a directory with all necessary data, the fordead package, and planned output directories.
```bash
docker run -t -i --name MYCONTAINER -v <YOUR_WORKING_DIRECTORY>:/mnt registry.gitlab.com/fordead/fordead_package /bin/bash
```
The contents of this working directory will be available in the "/mnt" directory inside the container. For example, if you have the directory "E:/fordead/fordead_package", and you use the command `docker run -t -i --name fordead -v E:/fordead:/mnt registry.gitlab.com/fordead/fordead_package /bin/bash`, its absolute path will then be "/mnt/fordead_package" in the container.

Then activate the virtual environment containing all dependencies, and install the fordead package.
```bash
conda activate fordead
```

You can now use all of fordead's [command line functions](https://fordead.gitlab.io/fordead_package/docs/cli/) or run python scripts using fordead functions from there.

When you are done, you can stop the container using `docker stop fordead`.
If you wish to work using this container again, it is already created and already has fordead installed, and you can simply use :
```bash
docker start MYCONTAINER
docker exec -it MYCONTAINER /bin/bash
```
You can detach from the container using CTRL-D, and reattach or attach several times to access it with multiple command lines using `docker exec -it MYCONTAINER /bin/bash`.




