from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules = [Extension("cards", ["cards.pyx"]),
               Extension("handscore", ["handscore.pyx"]),
               Extension("hand_simulator", ["hand_simulator.pyx"])]

setup(
  name = 'Pokeher core ops',
  cmdclass = {'build_ext': build_ext},
  ext_modules = ext_modules
)
