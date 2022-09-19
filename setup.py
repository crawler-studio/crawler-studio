"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2021/8/21 下午6:44
"""
# !/usr/bin/env python
# coding=utf-8
from os import walk
from os.path import join, isfile
from setuptools import setup, find_packages


def package_files(directories):
    paths = []
    for item in directories:
        if isfile(item):
            paths.append(join('..', item))
            continue
        for (path, directories, filenames) in walk(item):
            for filename in filenames:
                paths.append(join('..', path, filename))
    return paths


setup_args = {
    'name': 'crawler_studio',
    'version': 'V1.2.8',
    'description': 'crawler_studio',
    'author': 'liuxianglong',
    'author_email': '862187570@qq.com',
    'maintainer': 'liuxianglong',
    'maintainer_email': '862187570@qq.com',
    'license': 'BSD License',
    'packages': find_packages(),
    'py_modules': ['crawler_studio.__init__'],
    'package_data': {
        '': package_files([
            'crawler_studio/static',
            'crawler_studio/dist',
        ])
    },
    'platforms': ["all"],
    'classifiers': [
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries'
    ],
    'install_requires': [
        'scrapy', 'django', 'django-rest-framework'
    ],
    'entry_points': {
        'console_scripts': [
            'cs=crawler_studio.cmd:cmd'
        ]
    }
}


setup(**setup_args)
