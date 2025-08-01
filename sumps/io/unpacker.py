import os.path
import random
import re
import shutil
import string
import tempfile
import zipfile
from os.path import basename


def entropy(length: int) -> str:
    return "".join(random.choice(string.ascii_lowercase) for i in range(length))


def unpack_zipfile(file: str):
    if not os.path.isfile(file):
        raise Exception("Error: file, not found!")

    # Create unique working direction into which the zip file is expanded
    unzip_dir = f"{tempfile.gettempdir()}/{os.path.splitext(basename(file))[0]}_{entropy(6)}"

    def delete(self):
        # delete self.unzip_dir and its contents
        shutil.rmtree(unzip_dir)

    datfilename = ""
    binfilename = ""

    with zipfile.ZipFile(file, "r") as zip:
        files = [item.filename for item in zip.infolist()]
        datfilename = [m.group(0) for f in files for m in [re.search(".*\\.dat", f)] if m].pop()
        binfilename = [m.group(0) for f in files for m in [re.search(".*\\.bin", f)] if m].pop()

        zip.extractall(rf"{unzip_dir}")

    datfile = f"{unzip_dir}/{datfilename}"
    binfile = f"{unzip_dir}/{binfilename}"

    return binfile, datfile, delete
