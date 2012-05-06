import os
from setuptools import setup

itaushopline = __import__('itaushopline', {}, {}, [''])

def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read()

setup(
    name = "itaushopline",
    version = itaushopline.__version__,
    author = "Pote Interativo",
    author_email = "gabriel@poteinterativo.com.br",
    description = ("python client for itau shopline"),
    long_description=read('README.md'),
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    license = itaushopline.__license__,
    keywords = ["itau", "shopline"],
    url = "https://github.com/gabrielgaliaso/pyitaushopline",
    packages=['itaushopline',],
    install_requires=['requests >= 0.10',]
)