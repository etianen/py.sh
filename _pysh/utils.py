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
    mkdirp(os.path.dirname(dest))
    with urlopen(url) as src_handle, open(dest, "wb") as dst_handle:
        shutil.copyfileobj(src_handle, dst_handle)
