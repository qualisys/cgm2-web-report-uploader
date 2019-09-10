# -*- coding: utf-8 -*-
from setuptools import setup,find_packages

#------------------------- INSTALL--------------------------------------------
setup(name = 'qtmWebGaitReport',
    version = "0.0.1",
    author = 'Fabien Leboeuf',
    author_email = 'fabien.leboeuf@gmail.com',
    description = "fork of the qtm web report uploader ",
    keywords = 'gait, mocap',
    packages=find_packages(),
	include_package_data=True,
    license='MIT License',
    install_requires = ['ffmpy>=0.2.2',
                        'requests>=2.7.0'],
    classifiers=['Development Status :: 4 - Beta',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2.7',
                 'Operating System :: Microsoft :: Windows',
                 'Natural Language :: English'],
    )
