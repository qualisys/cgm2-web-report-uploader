# -*- coding: utf-8 -*-
import json

from setuptools import find_packages, setup

with open("settings.json", "r") as f:
    settings = json.load(f)

# ------------------------- INSTALL--------------------------------------------
setup(
    name="qtmWebGaitReport",
    version=settings["version"],
    author="Qualisys",
    author_email="support@qualisys.com",
    description=settings["description"],
    keywords="gait, mocap",
    packages=find_packages(),
    include_package_data=True,
    license="MIT License",
    install_requires=["ffmpy>=0.2.2", "requests>=2.7.0"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Operating System :: Microsoft :: Windows",
        "Natural Language :: English",
    ],
)
