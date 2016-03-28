from setuptools import setup
from _pysh import __version__


setup(
    name="_pysh",
    version=".".join(map(str, __version__)),
    license="BSD",
    description="Helper module for py.sh.",
    author="Dave Hall",
    author_email="dave@etianen.com",
    url="https://github.com/etianen/py.sh",
    packages=["_pysh"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
    ],
)
