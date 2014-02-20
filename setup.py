from setuptools import setup
__version__ = '0.1.0'

setup(name='bibpy',
      version=__version__,
      packages=['bibpy'],
      include_package_data=True,
      package_data={'': ['*.json']},
      scripts=['bibcheck'])
