# The lad repository

Contain number of application for managing clients, store, statistics.


# Installation for development
## Creating a Virtual Environment
You can either create and manage a virtual environment yourself or install pyenv and follow
the instructions below to set up the virtual environment.
- [pyenv](https://github.com/pyenv/pyenv)
- [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)
### Create a virtual environment
```
pyenv virtualenv 3.6.7 lad-common
pyenv virtualenv 3.6.7 lad-crm
```
- Create .python-version file in the root
```bash
echo "lad-common" >> lad-common/.python-version
echo "lad-crm" >> lad-crm/.python-version
```

If pyenv-virtualenv is installed correctly, the virtual environment should be activated
automatically whenever you cd into the project directory.

- Install the dependencies. Each project has it's own dependencies therefore you have to go into
the service where you are going to install dependencies, make sure that virtualenv is activated and do
```
pip install -r requirements/development.txt
```

- Install git hooks to be sure that code is formatted correctly
```bash
pre-commit install -f
```

