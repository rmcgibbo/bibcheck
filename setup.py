from setuptools import setup

setup(name='bibpy',
      packages=['bibpy'],
      include_package_data=True,
      package_data={'': ['*.json']},
      scripts=['bibcheck'])
