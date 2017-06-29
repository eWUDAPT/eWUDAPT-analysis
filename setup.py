import os
from setuptools import setup
import sys

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "eWUDAPT_analysis",
    version = "0.0.1",
    author = "Ronald van Haren, Gijs van den Oort",
    author_email = "r.vanharen@esciencecenter.nl, g.vandenoort@esciencecenter.nl",
    description = ("Tools for eWUDAPT model intercomparison"),
    license = "Apache 2.0",
    keywords = "eWUDAPT model intercomparison",
    url = "https://github.com/eWUDAPT/eWUDAPT-analysis",
    packages=['eWUDAPT_analysis'],
    scripts=['eWUDAPT_analysis/scripts/ewudapt-single',
             'eWUDAPT_analysis/scripts/ewudapt-multiple'],
    package_data={'eWUDAPT_analysis': ['data_request.json']},
    include_package_data=True,
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved ::Apache Software License",
    ],
)
