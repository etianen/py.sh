# py.sh

Shell script to install and manage a standalone Python interpreter and environment.

**Note:** This project makes use of [Anaconda](http://continuum.io/anaconda), a Python distribution by [Continuum Analytics](https://www.continuum.io/). It is expected that the [Anaconda End User License Agreement](https://docs.continuum.io/anaconda/eula) is agreed upon.


## Features

- Create per-project Python installations.
- Configure PyPi and Anaconda Cloud dependencies in a single `package.json` file.
- Create a standalone archive of your entire project, including dependencies and Python interpreter, for offline installation on another machine of the same operating system and architecture.
- Supports a large number of 64bit Linux or OSX platforms.
- Supports a large number of [Python versions](https://anaconda.org/anaconda/python/files).
- Supports a large number of precompiled binary dependencies (e.g. [numpy](http://www.numpy.org/), [scipy](http://www.scipy.org/)) from [Anaconda Cloud](https://anaconda.org), as well as any package on [PyPi](https://pypi.python.org/pypi).


# How it works.

A small `py.sh` script is added to the root of your Python project. This is used to bootstrap a standalone Python interpreter in a hidden `.pysh` directory.


## Installation

1.  Download the `py.sh` script.

    ``` bash
    curl -sL https://raw.githubusercontent.com/etianen/py.sh/master/generate.sh | bash > py.sh
    ```

2.  Make it executable.

    ``` bash
    chmod +x py.sh
    ```

3.  Install you a Python, for great good!

    ``` bash
    ./py.sh install
    ```

4.  Add the hidden `.pysh` directory to your `.gitignore` file.

**Note:** Step 1 actually generates a custom py.sh script locked to the latest version of the py.sh helper libraries on GitHub. If you ever need to upgrade py.sh, simply follow these steps again.

**Advanced:** Manual installation can be performed by simply copying the [py.sh](https://github.com/etianen/py.sh/blob/master/py.sh) script from GitHub into your project folder, but you'll have to manually edit the script to lock `$PYSH_HELPERS_URL` to a specific Git commit.


## Usage

**Note:** You can learn a lot from `./py.sh --help`.


### Running a command in your standalone environment

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


### Activating your standalone environment

Rather than prefix every command with `./py.sh run`, you can activate your environment with `./py.sh activate`.

For example, to install and run [flake8](https://flake8.readthedocs.org/en/latest/):

```
./py.sh activate
pip install flake8
flake8 .
```


### Configuring Python version and dependencies

You can specify the Python version, along with any [Anaconda Cloud](https://anaconda.org) and [PyPi](https://pypi.python.org/pypi) dependencies, by creating a `package.json` file in the root of your project.

An example `package.json` file:

``` json
{
  "name": "awesome-package",
  "version": "0.1.0",
  "pysh": {
    "python": {
      "version": "3.5"
    },
    "conda": {
      "dependencies": {
        "psycopg2": "2.6.1"
      },
      "devDependencies": {
        "pytest": "2.8.5"
      }
    },
    "pip": {
      "dependencies": {
        "django": "1.9.2"
      },
      "devDependencies": {
        "flake8": "2.5.4"
      }
    },
    "install": [
      "my-post-install-command.sh"
    ]
  }
}
```

Whenever you update your `package.json` file, simply run `./py.sh install` to rebuild your environment with the specified dependencies.


### Configuring local settings

If you create a `.env` file in the root of your project, it will be sourced by the shell before any `./py.sh run` commands are run, and at the start of a `./py.sh activate` session.

**Note:** It's customary to use this to configure environmental variables for your project, and to exclude the `.env` file from version control.


### Creating a standalone archive

It's possible to create a standalone archive of your entire project, including dependencies and Python interpreter, for offline installation on another machine of the same operating system and architecture.

``` bash
./py.sh dist
```

You will find a zip archive in the `./dist` folder of your project. Copy this to another machine of the same operating system and architecture, then unzip and install your project.

``` bash
unzip your-project-1.0.0.zip -d your_project
cd your_project
./py.sh install --offline
```


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
