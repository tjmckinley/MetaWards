from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize("metawards_c.pyx", language_level="3")
)