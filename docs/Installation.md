
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