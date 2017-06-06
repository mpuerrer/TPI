# coding: utf-8

# Copyright 2017 Michael Puerrer
#
# License:  Standard 3-clause BSD; see "license.txt" for full license terms
#           and contributor agreement.


from __future__ import absolute_import

# an exception just to confirm that the .so file is loaded instead of the .py file
#raise ImportError("__init__.py loaded when __init__.so should have been loaded")
print "__init__.py loaded when __init__.so should have been loaded"