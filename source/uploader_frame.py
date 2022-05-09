# -*- coding: utf-8 -*-
"""
uploader_frame.py: Creates skeleton for child class of uploader. Prepares
necessary settings and configs.

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
__credits__ = ["Vojtech Barnat", "Ivo Bukovsky", "Jakub Geyer"]

__license__ = "MIT (X11)"
__version__ = "1.0.1"
__maintainer__ = ["Ondrej Budik", "Vojtech Barnat"]
__email__ = ["obudik@prf.jcu.cz", "Vojtech.Barnat@fs.cvut.cz"]
__status__ = "Beta"

__python__ = "3.8.0"

# Import required libs
from datetime import datetime

# UniCatDB import API imports
import unicatdb

# Scripts
def dtformating(datetime):
    """
    Generates string date format accepted by UniCatDB.

    Parameters
    ----------
    datetime : datetime
        Datetime object which should be converted to string.

    Returns
    -------
    datetimestring : str
        String formated in accordance with database datetime format.

    """

    datetimestring = f"{datetime.year}-{datetime.month}-{datetime.day}T{datetime.hour}:{datetime.minute}:{datetime.second}.{datetime.microsecond}"
    return datetimestring

# Connector frame class
class ConnectorFrame:
    """
    Constructs skeleton for commits in children for various database schemas of UniCatDB.
    This class prepares necessary settings and methods for uploader class.
    """
    def __init__(self):
        """
        Constructor of Connector class. For full documentation do see class doc.
        """
        self.config = None
        self.configuration()
        self.setup = {}
        self.load_setup()

    def configuration(self):
        """
        Prepares connector for connection to UniCatDB. Loads library settings
        for server adress and loads user token from api.token file.

        Returns
        -------
        None.

        """
        # Paste your Personal access token from https://account.unicatdb.org/ to api.token file.
        # Can be edited with text editor.
        with open("api.token", "r") as token:
            token = token.read()

        self.config = unicatdb.Configuration(access_token=token,
                                             server=unicatdb.Servers.TEST_UNICATDB_ORG)

    def load_setup(self):
        """
        Loads setup variables from config.py for given upload. Saves them to
        class variable setup.

        Returns
        -------
        None.
        """
        from config import DOCUMENT_SET, LOCATION_DESCRIPTION, NOTE, TAGS
        self.setup["document_set"] = DOCUMENT_SET
        self.setup["date"] = dtformating(datetime.now())
        self.setup["loc_desc"] = LOCATION_DESCRIPTION
        self.setup["note"] = NOTE
        self.setup["tags"] = TAGS

    def commit_one(self, data):
        """
        Commit one of child class.
        """
        pass

    def commit_all(self, data):
        """
        Commit all of child class.
        """
        pass

if __name__ == "__main__":
    print("UploaderFrame is not standalone working class. Please use children with coded commits.")