from setuptools import setup
__version__ = '0.1.1'

setup(name='bibcheck',
      version=__version__,
      packages=['bibcheck'],
      include_package_data=True,
      package_data={'': ['*.json']},
      entry_points={'console_scripts': ['bibcheck = bibcheck.main:main']}
)
