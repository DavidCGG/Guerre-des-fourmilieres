from setuptools import setup, find_packages

setup(
    name='arcade',
    version='2.6.17',
    description='Arcade game engine for Python',
    packages=find_packages(),
    install_requires=[
        'pyglet',
        'pillow'
    ]

)