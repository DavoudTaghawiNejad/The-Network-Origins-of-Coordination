from distutils.core import setup
from Cython.Build import cythonize

setup(
  name = 'players',
  ext_modules = cythonize("players.pyx"),
)
