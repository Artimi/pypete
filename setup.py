#-*- encoding: utf-8 -*-
from setuptools import setup

setup(name='Pypete',
      version='0.1',
      author='Petr Šebek',
      author_email='petrsebek1@gmail.com',
      keywords='performance tests nose plugin',
      description='Pypete - Python Performance Tests',
      license='MIT',
      install_requires=['nose>=0.10'],
      entry_points={
          'nose.plugins.0.10': [
              'pypete = pypete:Pypete'
          ]
      })
