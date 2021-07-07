#! /usr/bin/env python
import os

from setuptools import setup

CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: BSD License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

README_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md")
with open(README_PATH, "r", encoding="utf8") as f:
    README = f.read()

setup(
    name="ariadne-relay",
    author="General Intelligence Inc.",
    author_email="info@g18e.com",
    description=(
        "Ariadne-Relay provides a toolset for implementing GraphQL servers "
        "in Python that conform to the Relay specification, using the "
        "Ariadne library."
    ),
    long_description=README,
    long_description_content_type="text/markdown",
    license="BSD",
    version="0.1.0a2",
    url="https://github.com/g18e/ariadne-relay",
    packages=["ariadne_relay"],
    include_package_data=True,
    install_requires=[
        "ariadne>=0.13.0",
        "graphql-relay>=3.1.0",
    ],
    extras_require={},
    classifiers=CLASSIFIERS,
    platforms=["any"],
    zip_safe=False,
)
