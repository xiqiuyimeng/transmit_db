# -*- coding: utf-8 -*-
from setuptools import setup
_author_ = 'luwt'
_date_ = '2021/9/2 18:30'


setup(
    name='transmitDB',
    version='1.0',
    url='https://github.com/xiqiuyimeng/transmit_db',
    author='xiqiuyimeng',
    author_email='JEET847466569@163.com',
    description='transmit db structure and data',
    license='Apache v2',
    install_requires=['loguru==0.5.3', 'PyMySQL==1.0.2'],
    python_requires='>=3',
    packages=['transmit_db'],
)
