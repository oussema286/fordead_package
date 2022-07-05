
If you have [git](https://git-scm.com/) installed, then go to the directory of your choice and run the following commands :
```bash
git clone https://gitlab.com/fordead/fordead_package.git
cd fordead_package
```
Or without git, simply download and unzip the package from the [gitlab page](https://gitlab.com/fordead/fordead_package)

### Conda install 
If you have the [anaconda](https://www.anaconda.com/products/individual) python distribution installed, simply run the following commands from the command prompt in the directory of the package :

```bash
conda env create --name fordead_env
conda activate fordead_env
pip install .
```

### Install without conda

If you don't have conda, you can find the required dependencies in the [environment.yml](https://gitlab.com/fordead/fordead_package/-/blob/master/environment.yml) file and install them by hand before running the following command in the package directory :
```bash
pip install .
```

### Using Docker

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
cd <your_fordead_package_directory>
pip install .
```

You can now use all of fordead's [command line functions](https://fordead.gitlab.io/fordead_package/docs/cli/) or run python scripts using fordead functions from there.

When you are done, you can stop the container using `docker stop fordead`.
If you wish to work using this container again, it is already created and already has fordead installed, and you can simply use :
```bash
docker start MYCONTAINER
docker exec -it MYCONTAINER /bin/bash
```
You can detach from the container using CTRL-D, and reattach or attach several times to access it with multiple command lines using `docker exec -it MYCONTAINER /bin/bash`.




