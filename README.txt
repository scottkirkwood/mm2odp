MM to ODP
=========

This is a simple utility to convert a FreeMind mind-map (.mm) into an OpenOffice
Presentation Document (.odp).  
The root node becomes the start page and each top level node below that becomes
a slide.
Lower level nodes become increasingly nested lists.

Links
-----
FreeMind: http://freemind.sourceforge.net/wiki/index.php/Main_Page
OpenOffice.org: http://openoffice.org

Install
-------

# python setup.py install

or

# easy_install.py mm2odp

Prerequesites
-------------

Requires Python 2.3 or greater
Requires elementtree (included in Python 2.5)

License
-------

GNU GPL http://www.gnu.org/copyleft/gpl.html
