import os
from setuptools import setup, find_packages


this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='litgen',
    version='0.1.0',
    author='Pascal Thomet',
    author_email='pthomet@gmail.com',
    description='''litgen: pybind11_literate_generator, 
        a pybind11 automated generator for humans who like nice code and API documentation. 
        ''',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/pthom/pybind11_literate_generator',
    packages = find_packages(where='.'),
    zip_safe=False,
)
