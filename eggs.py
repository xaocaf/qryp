import os
import pkg_resources
import sys
from setuptools.archive_util import unpack_archive

def unpackEgg(module):
    eggs = pkg_resources.require(module)
    for egg in eggs:
        if os.path.isdir(egg.location):
            sys.path.insert(0, egg.location)
            continue
        unpack_archive(egg.location, ".")
    eggpacks = set()
    egg_name = []
    for egg in eggs: egg_name.append(str(egg).split(" ")[0])

    eggpacks.clear()

    return egg_name
