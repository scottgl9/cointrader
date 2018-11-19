#!/usr/bin/python
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import glob
import sys

if sys.platform == 'win32':
    indicator_files=glob.glob("trader\\indicator\\*.py")
    signal_files=glob.glob("trader\\signal\\*.py")
else:
    indicator_files=glob.glob("trader/indicator/*.py")
    signal_files=glob.glob("trader/signal/*.py")

ext_modules = [
    Extension("trader.indicator",  indicator_files),
    Extension("trader.signal",  signal_files),
#   ... all your modules that need be compiled ...
]

setup(
    name = 'trader',
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules
)
