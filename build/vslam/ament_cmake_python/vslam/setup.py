from setuptools import find_packages
from setuptools import setup

setup(
    name='vslam',
    version='0.0.0',
    packages=find_packages(
        include=('vslam', 'vslam.*')),
)
