import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pile",
    version = "0.0.1",
    author = "Heinrich Hartmann",
    author_email = "Heinrich@HeinrichHartmann.com",
    description = ("A document manager."),
    license = "GPL",
    keywords = "example documentation tutorial",
    url = "",
    packages=[],
    py_modules = ['pile'],
    long_description=read('README.md'),
    scripts = ['bin/pile'],
    install_requires = [ "click" ],
)
