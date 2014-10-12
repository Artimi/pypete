#-*- encoding: utf-8 -*-
from setuptools import setup
import os.path


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read().strip()


setup(name='pypete',
      packages=['pypete'],
      version='0.1',
      author='Petr Šebek',
      author_email='petrsebek1@gmail.com',
      keywords='performance tests nose plugin',
      description='Pypete - Python Performance Tests',
      license='MIT',
      url='https://github.com/Artimi/pypete',
      install_requires=['nose', 'prettytable'],
      long_description=read('README.rst'),
      entry_points={
          'nose.plugins.0.10': [
              'pypete = pypete:Pypete'
          ]
      }
)