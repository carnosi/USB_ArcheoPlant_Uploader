# -*- coding: utf-8 -*-
"""
all_in_one.py: Connects pre loader and uploader functionality into one
easy to use package. Relies on uploadergui to be managed.

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
__version__ = "1.0.2"
__maintainer__ = ["Ondrej Budik"]
__email__ = ["obudik@prf.jcu.cz"]
__status__ = "Beta"

__python__ = "3.8.0"

# Import required libs
from pathlib import Path

# Import custom libs
import dataprocess as dp
import uploader as up

# Check if uploader and dataprocess has correct versions
from version_check import check_version
check_version(dp.__version__, [1, 1, 0], "dataprocess.py")
check_version(up.__version__, [1, 1, 0], "uploader.py")

# Global for interupting the script
BREAK = False

def all_in_one(path, origin, user="Test User In AiO", progresshandler=None, uploaderhandler=None, consolecall=False):
    """
    Script which uses dataprocessing and uploader to automatically process data in given folder
    and upload them to UniCatDB. Does not save any metadata of processed folders!

    Parameters
    ----------
    path : str
        Path to folder with seed folders which contain images and meta data
    origin : str
        Origin of images. Important to say, which microscope took the pictures
        Changes the extraction of meta data
    user : str, optional
        User name who commits current batch to DB for easy fail detection and rollbacks.
        Defaults to "Test Script".
    progresshandler : method, optional
        Handler for attached GUI of its progressbar. Defaults to None.
    uploadhandler : method, optional
        Handler for attached GUI of its uploadbar. Defaults to None.
    consolecall : bool, optional
        Bool trigger for console prints for easier debugging. Defaults to False

    Returns
    -------
    None.
    """
    # Setup global so this can be stopped on another thread.
    global BREAK

    # Init data generator
    data_generator = dp.main(path, origin=origin, consolecall=False, generator=True)

    # Get amount of files for progress bar and init it
    nr = dp.get_amount_of_files(path)+1
    if progresshandler:
        progresshandler(0, ct_max=nr*2)

    # Init uploader
    uploader = up.Connector()

    ct = 0
    while not BREAK:
        try:
            # Load data
            group = next(data_generator)
            # Change path to str for upload
            temp_group = []
            for data in group:
                data['img_path'] = data['img_path'].as_posix()
                data['meta_path'] = data['meta_path'].as_posix()

                # Update progress bar for processing part
                ct += 1
                if progresshandler:
                    progresshandler(ct)

                # Resolve path for data
                if not Path(data['img_path']).is_absolute():
                    abs_data_path = dp.rcwd / Path(data['img_path'])
                    data['img_path'] = abs_data_path.as_posix()
                # Resolve path for meta
                if not Path(data['meta_path']).is_absolute():
                    abs_meta_path = dp.rcwd / Path(data['meta_path'])
                    data['meta_path'] = abs_meta_path.as_posix()

                # Add user to data
                data['user'] = user
                # Append to temp group
                temp_group.append(data)
            # Upload processed group
            uploader.commit_one_group(temp_group, uploaderhandler)

            # Increment progress bar
            ct += 1
            if progresshandler:
                progresshandler(ct)
        except StopIteration:
            if consolecall:
                print("All data have been processed.")
            break
    BREAK = False
    if progresshandler:
        progresshandler(ct, finished=True)

if __name__ == "__main__":
    # Runs this script in specified PATH. Uploads all species within that folder.
    PATH = ".//test"
    file = all_in_one(PATH, 'zeis')