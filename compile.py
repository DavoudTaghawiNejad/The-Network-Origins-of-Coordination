from distutils.core import setup
from Cython.Build import cythonize

setup(
  name = 'players2',
  ext_modules = cythonize("players2.pyx"),
)
