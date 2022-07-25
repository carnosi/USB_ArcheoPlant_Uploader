# -*- coding: utf-8 -*-
"""
Holds version check script for custom scripts

__doc__ using Sphnix Style
"""

# Copyright 2022 University Southern Bohemia

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__author__ = "Ondrej Budik"
__copyright__ = "<2022> <University Southern Bohemia>"
__credits__ = ["Vojtech Barnat", "Ivo Bukovsky"]

__license__ = "MIT (X11)"
__version__ = "1.0.0"
__maintainer__ = ["Ondrej Budik"]
__email__ = ["obudik@prf.jcu.cz"]
__status__ = "Beta"

__python__ = "3.8.0"

def check_version(lib_version, min_version, lib_name):
    """Checks versions of custom scripts if they are up to date with current UI

    Parameters
    ----------
    lib_version : str
        Version of custom script to check in a form of: "1.0.1"
    min_version : list
        Version expressed as list of numbers. Eg.: [1, 0, 1]
    lib_name : str
        Name of script to check for easy debug error traceback.

    Raises
    ------
    ImportError
        Raises when script version is lower than minimum required.
    """
    lib_version = lib_version.split(".")
    for pos, element in enumerate(lib_version):
        lib_version[pos] = int(element)

    if lib_version[0] < min_version[0]:
        raise ImportError(f"{lib_name} is missing major update! Update your software from github or ask admin to do that.")

    if lib_version[1] < min_version[1] and lib_version[0] <= min_version[0]:
        raise ImportError(f"{lib_name} may be missing important functionality or methods. Update your software from github or ask admin to do that.")

    if lib_version[2] < min_version[2] and lib_version[1] <= min_version[1]:
        print(f"{lib_name} is missing minor update. Consider updating your software to ensure optimal performance and get latest bugfixes.")
