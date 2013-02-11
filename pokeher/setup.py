from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules = [Extension("cards", ["pokeher/cards.py"]),
               Extension("handscore", ["pokeher/handscore.py"])]

setup(
  name = 'Pokeher core ops',
  cmdclass = {'build_ext': build_ext},
  ext_modules = ext_modules
)
