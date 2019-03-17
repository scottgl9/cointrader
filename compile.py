#!/usr/bin/python
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from Cython.Build import cythonize
import glob
import sys
import os

# scan the 'dvedit' directory for extension files, converting
# them to extension names in dotted notation
def scandir(dir, files=[], ignore=[]):
    for file in os.listdir(dir):
        path = os.path.join(dir, file)
        native_path = os.path.join(dir, 'native', file.replace('.py', '.c'))
        if os.path.isfile(path) and path.endswith(".py"):
            if os.path.basename(path) not in ignore:
                # don't generate .c file if already has native implementation
                if not os.path.isfile(native_path):
                    files.append(path.replace(os.path.sep, ".")[:-3])
        elif os.path.isdir(path):
            if os.path.basename(path) not in ignore:
                scandir(path, files, ignore)
    return files


# generate an Extension object from its dotted name
def makeExtension(extName):
    extPath = extName.replace(".", os.path.sep)+".py"
    return Extension(
        extName,
        [extPath],
        include_dirs = ["."],   # adding the '.' to include_dirs is CRUCIAL!!
        extra_compile_args = ["-O3", "-Wall"],
        extra_link_args = ['-g'],
        #libraries = ["dv",],
        )


# get the list of extensions
extNames = scandir("trader", ignore=["bitstamp", 'FIX42', '__init__.py', 'AccountGDAX.py', 'AccountCobinhood.py', 'OrderBookBase.py', 'RankManager.py'])

# and build up the set of Extension objects
extensions = [makeExtension(name) for name in extNames]

# finally, we can pass all this to distutils
setup(
  name="trader",
  packages=["trader", "trader.indicator", "trader.lib", "trader.signal", "trader.strategy",
            "trader.account", "trader.account.binance", "trader.strategy.trade_size_strategy"],
  ext_modules=extensions,
  cmdclass = {'build_ext': build_ext},
  scripts=['tools/binance_simulate.py']
)
