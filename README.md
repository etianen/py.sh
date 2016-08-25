# py.sh

Install and manage a standalone Python interpreter and dependencies.

**Note:** This project makes use of [Anaconda](http://continuum.io/anaconda), a Python distribution by [Continuum Analytics](https://www.continuum.io/). It is expected that the [Anaconda End User License Agreement](https://docs.continuum.io/anaconda/eula) is agreed upon.


## Features

- Create per-project Python installations.
- Create a standalone project archive for offline installation on another machine.
- Supports a large number of 64bit Linux and OSX platforms.
- Supports a large number of [Python versions](https://anaconda.org/anaconda/python/files).
- Supports a large number of precompiled binary dependencies (e.g. [numpy](http://www.numpy.org/), [scipy](http://www.scipy.org/)) from [Anaconda Cloud](https://anaconda.org).


## How it works

A small `py.sh` script is added to the root of your Python project. This is used to bootstrap a standalone Python interpreter in a hidden `.pysh` directory.


## Automated installation

A standalone Python interpreter will be installed into `.pysh`.

``` bash
curl -sL https://raw.githubusercontent.com/etianen/py.sh/master/install.sh | bash
```

**Recommended:** Add `.pysh` to your `.gitignore` file.

**Advanced:** The steps performed by the automated installer are documented in [install.sh](https://github.com/etianen/py.sh/blob/master/install.sh). You can perform them manually if preferred.


## Usage

**Hint:** You can learn a lot from `./py.sh --help` and `./py.sh <command name> --help`.


### Running a command in your environment

Run any command with `./py.sh run <your command>`.

For example, to fire up your standalone Python interpreter:

``` bash
./py.sh run python
```

Or to install and run [flake8](https://flake8.readthedocs.org/en/latest/):

``` bash
./py.sh run pip install flake8
./py.sh run flake8 .
```


### Activating your environment

Rather than prefix every command with `./py.sh run`, you can activate your environment with `./py.sh activate`.

For example, to install and run [flake8](https://flake8.readthedocs.org/en/latest/):

```
./py.sh activate
pip install flake8
flake8 .
```


### Specifying dependencies

Create a `requirements.txt` file in the root of your project.

```
django==1.10
```

**Note:** Whenever you update your `requirements.txt` file, run `./py.sh install` to rebuild your environment with the specified dependencies.


### Specifying dev dependencies

Create a `requirements-dev.txt` file in the root of your project.

Development dependencies will not be installed when using the `--production` flag to `./py.sh install`, and will not be included in the bundle created by `./py.sh dist`.


### Specifying conda dependencies

Create a `requirements-conda.txt` file in the root of your project. Packages will be installed from [Anaconda Cloud](https://anaconda.org).

Large binary packages (e.g. `numpy`, `scipy`) will be pre-compiled for your operating system and install considerably faster than installing via `pip`.

```
python=3.5.2
psycopg2=2.6.2
```

**Hint:** Specify conda dependencies that should only be installed during development by creating a `requirements-conda-dev.txt` file in the root of your project.


### Creating a standalone archive

It's possible to create a standalone archive of your entire project, including dependencies and Python interpreter, for offline installation on another machine.

``` bash
./py.sh dist --output dist/your-project-1.0.0-linux-amd64.zip
```

You will find a zip archive in the `./dist` folder of your project. Copy this to another machine of the same operating system and architecture, then unzip and install your project.

``` bash
unzip your-project-1.0.0-linux-amd64.zip -d your_project
cd your_project
./py.sh install --offline
```

**Note:** Offline installers work best if all binary dependencies (e.g. [numpy](http://www.numpy.org/), [scipy](http://www.scipy.org/)) are obtained from [Anaconda Cloud](https://anaconda.org). Otherwise, large binary dependencies can take an extremely long time to compile during installation.


## FAQ

### Q: Why is this useful?

These things are otherwise difficult to do:

- Run a modern Python interpreter on an outdated version of Linux.
- Produce offline installers for a Python project.
- Run multiple version of Python on the same machine in production.


### Q: Isn't this already done by XXX?

Probably, but I've never heard of XXX, or it didn't support all the features I wanted.

[virtualenv](https://virtualenv.pypa.io/en/latest/) is useful for managing a standalone bunch of PyPy dependencies. It doesn't help with installing Python interpreters not included in your operating system, and large binary dependencies can be a pain to install.

[pyenv](https://github.com/yyuu/pyenv) is useful for managing multiple Python versions in development, but it doesn't help with binary dependencies.

This project is just a convenience wrapper around [Miniconda](http://continuum.io/anaconda), so it hasn't really reinvented anything.


## Build status

This project is built on every push using the Travis-CI service.

[![Build Status](https://travis-ci.org/etianen/py.sh.svg?branch=master)](https://travis-ci.org/etianen/py.sh)


## Support and announcements

Downloads and bug tracking can be found at the [main project website](http://github.com/etianen/py.sh).


## More information

This project was developed by Dave Hall. You can get the code
from the [project site](http://github.com/etianen/py.sh).

Dave Hall is a freelance web developer, based in Cambridge, UK. You can usually
find him on the Internet:

- [Website](http://www.etianen.com/)
- [Google Profile](http://www.google.com/profiles/david.etianen)
