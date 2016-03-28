import os
import shutil
from urllib.request import urlopen


# Filesystem.

def rimraf(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.exists(path):
        os.unlink(path)


def mkdirp(path):
    os.makedirs(path, exist_ok=True)


# Downloads.

def download(url, dest):
    response = urlopen(url)
    mkdirp(os.path.dirname(dest))
    with open(dest, "wb") as handle:
        while True:
            chunk = response.read(8192)
            if not chunk:
                break
            handle.write(chunk)
