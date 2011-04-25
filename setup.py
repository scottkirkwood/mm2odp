#!/usr/bin/env python

from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

# Note to self:
# python setup.py sdist --formats=zip
# To create the zip file

# python setup.py --command-packages=setuptools.command bdist_egg
# To create the egg file

# python setup.py register
# to register with PyPI
# 

# create an egg and upload it
# setup.py register bdist_egg upload

# Set this on command line
# DISTUTILS_DEBUG=true
# 
setup(
    name='mm2odp',
    version='0.1.0',
    description="Convert a FreeMind mind-map (mm) into an OpenOffice Presentation (odp).",
    long_description=
"""This is a simple utility to convert a FreeMind mind-map (.mm) into an OpenOffice presentation (odp).  
The root node becomes the start page and each top level node below that becomes a slide.
Lower level nodes become increasingly nested lists.
""",
    author='Scott Kirkwood',
    author_email='scottakirkwood@gmail.com',
    url='http://code.google.com/mm2odp/',
    download_url='http://mm2odp.googlecode.com/files/mm2odp-0.1.0.zip',
    keywords=['mm', 'odp', 'OpenOffice', 'FreeMind', 'Presentation', 'XML', 'Python'],
    license='GNU GPL',
    platforms=['POSIX', 'Windows'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Database',
        'Topic :: Documentation',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Text Processing :: Markup :: XML',
        'Topic :: Utilities',
    ], 
    packages=['mm2odp'],
    scripts=['scripts/mm2odp'],
)
