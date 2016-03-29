# py.sh

Shell script to install and manage a standalone Python interpreter and environment.

**Note:** This project makes use of [Anaconda](http://continuum.io/anaconda), a Python distribution by [Continuum Analytics](https://www.continuum.io/). It is expected that the [Anaconda End User License Agreement](https://docs.continuum.io/anaconda/eula) is agreed upon.


## Features

- Create per-project Python installations.
- Supports a large number of 64bit Linux or OSX platforms.
- Supports a large number of [Python versions](https://anaconda.org/anaconda/python/files).
- Supports a large number of precompiled binary dependencies (e.g. [numpy](http://www.numpy.org/), [scipy](http://www.scipy.org/)) from [Anaconda Cloud](https://anaconda.org), as well as any package on [PyPi](https://pypi.python.org/pypi).
- Configure PyPi and Anaconda Cloud dependencies in a single, unified `package.json` file.
- Create a standalone archive of your entire project, including dependencies and Python interpreter, for offline install on another machine of the same operating system and architecture.


# How it works.

A small `py.sh` script is added to the root of your Python project. This is used to bootstrap a standalone Python interpreter in a hidden `.pysh` folder.


## Installation

TODO


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
