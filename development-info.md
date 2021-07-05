# Installing dependencies

Preferably use a virtual environment. For example conda.
- Create conda enviroment `conda create -n pycgm2 python=3.7`
- Install dependencies with pip `pip install -r requirements-dev.txt`

# Running tests locally

With all dependencies installed run the tests with the following command:
- `pytest Tests`

This will run all the tests in the Tests folder with pytest.

# Updating pyCGM2 Version

It is recommended to create a new branch for updating the version. To update pyCGM2 version we need to change the version inside the [requirements file](requirements-dev.txt), by changing the `tag_or_commit` part of the url
`pyCGM2@git+https://github.com/pyCGM2/pyCGM2.git@tag_or_commit` for example `pyCGM2@git+https://github.com/pyCGM2/pyCGM2.git@version(4.2.0-beta)`

After the update, reinstall dependencies and run the tests.