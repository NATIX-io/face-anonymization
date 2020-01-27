
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='mtcnn',
    version='0.0.1',
    description='Face detection',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    # TODO TF dependency: tensorflow-gpu not supported on MacOSX
    install_requires=['opencv-python >= 4.1', 'numpy'],
    include_package_data=True
)    
