# -*- coding: utf-8 -*-
"""
dataprocess.py: Methods of meta data processing. Holds main script for
information extraction. Uses imgprocess.py for image processing. Main script
extracts data from all folders in given directory.

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
__version__ = "1.1.4"
__maintainer__ = ["Ondrej Budik"]
__email__ = ["obudik@prf.jcu.cz"]
__status__ = "Beta"

__python__ = "3.8.0"

# Import sys and pip libs
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import xmltodict

# Import custom scripts
import imgprocess as ip
# Get suffixes to fix file names of images. For more suffixes to filter, change config.py
from config import IMAGE_SUFFIX_NAMES, IMAGE_ADDITIONS

# Check if imgprocess has correct version
from imgprocess import __version__ as __imv__
from parsers import __zeiss_axiocam305c_parser__, __keyence_parser__
from version_check import check_version
check_version(__imv__, [1, 0, 6], "imgprocess.py")
check_version(__imv__, [1, 0, 4], "parsers.py")


# Get current working directory for file management as global var
cwd = Path.cwd()
rcwd = cwd / ".."
rcwd = rcwd.resolve()

# Global for interupting the script
BREAK = False

# clean addition and suffixes
for pos, item in enumerate(IMAGE_SUFFIX_NAMES):
    IMAGE_SUFFIX_NAMES[pos] = item.lower()

for pos, item in enumerate(IMAGE_ADDITIONS):
    IMAGE_ADDITIONS[pos] = item.lower()

# Functions definition
def img_meta_pair(groups, origin):
    """
    Takes subfolder with *.tifs and pairs them together with their meta data in based on their names.
    If names do not match (except suffix), automatic pairing can not be performed and files will be ignored

    Parameters
    ----------
    groups : list of lists with str (paths). The output of get_groups.
        List containing groups of seed image paths
    origin : str
        Name of group origins. Some microscopes save data inside of the image, thus grouping is not necessary.

    Returns
    -------
    groups_holder : list
        Contains list of lists. Each nested list is one group and has 2 paired values. [[[img, meta], [img, meta], ...], [[img, meta], [img, meta], ...]]
    """
    if origin.lower() not in ["keyence"]:
        groups_holder = []
        for group in groups:
            temp_group = []
            for img in group:
                img_path = Path(img)
                # Fix some of their weird naming
                if img_path.stem[-3:] in IMAGE_SUFFIX_NAMES:
                    temp_img_file = img_path.stem[:-3]
                else:
                    temp_img_file = img_path.stem
                # Append meta to path stem
                meta_temp = str(temp_img_file) + "_meta.xml"
                meta_file = img_path.parent / meta_temp
                if not meta_file.is_file():
                    print(f"\nFor image {img_path.stem} in {meta_file.parent} were no meta data found! File is excluded from upload.\n")
                    continue
                temp_group.append([img_path, meta_file])
            groups_holder.append(temp_group)
            temp_group = []
    else:
        groups_holder = []
        for group in groups:
            temp_group = []
            for img in group:
                img_path = Path(img)
                temp_group.append([img_path, img_path])
            groups_holder.append(temp_group)

    return groups_holder

def parse_meta(path, origin='zeiss axiocam 305c'):
    """
    Takes path to xml file with microscope meta data and extracts desired data for specified database.

    Parameters
    ----------
    xml_path : str or pathlib.Path
        Path to target xml file with meta data to parse.
    origin : str, optional
        Origin of meta data. Important for various parsing mechanisms. Defaults to zeiss axiocam 305c.

    Returns
    -----
    parsed_meta : dict
        Dictionary containing parsed data from given xml file.

    Raises
    ------
    IOError
        Raises when unknown meta data parser has been selected.
    """
    # read meta data for specific manufacturer
    if origin.lower() == "zeiss axiocam 305c":
        # Load xml and convert it to dict
        meta_dict = xmltodict.parse(ET.tostring(ET.parse(path).getroot()))
        parsed_meta = __zeiss_axiocam305c_parser__(meta_dict)
    elif origin.lower() == 'keyence':
        parsed_meta = __keyence_parser__(path)
    else:
        raise IOError(f"Unknown meta data origin for {origin}! Please code missing meta parser.")

    # Get creation data
    parsed_meta['timestamp'] = path.stat().st_ctime
    return parsed_meta

def px_to_metric(pixel, scaling_factor, scaling):
    """
    Converts given pixel to desired length. Scaling_factor should be obtained from meta data.

    Parameters
    ----------
    pixel : numeric
        Pixel distance for given length
    scaling_factor : numeric
        Scaling which should be applied per pixel. Can be parsed from microscope meta data
    scaling : str
        Metric unit in which the obtained length should be converted.

    Returns
    -------
    length : numeric
        Length value for given pixel count and meta data factors
    """
    scaling = scaling.lower()
    # Get scaling factor
    if scaling == 'm':
        scale = 1
    elif scaling == 'dm':
        scale = 10
    elif scaling == 'cm':
        scale = 100
    elif scaling == 'mm':
        scale = 1000
    elif scaling == 'um' or scaling == 'µm':
        scale = 1000000
    elif scaling == 'nm':
        scale = 1000000000
    else:
        print("Unknown scaling unit. No scaling applied.")
        scale = 1
    # Calculate real length
    length = pixel * scaling_factor * scale
    return length

def resolve_path(path):
    """
    Resolves given path to normalized format for any system. Relative gets translated to absolute

    Parameters
    ----------
    path : str
        Path to destination folder to resolve

    Returns
    -------
    PATH : pathlib.Path
        Pathlib resolved path. Compatible with any system. Relative path is translated to absolute.
    """
    # Check, if path is relative or has to be cwd
    path = Path(path).parts
    if len(path) == 1:
        PATH = rcwd / path[0]
    elif len(path) > 1:
        PATH = Path(*path)
    else:
        PATH = rcwd
    return PATH

def resolve_folders(path):
    """
    Resolves given path with pathlib. Returns list of all folder subdirectories.

    Parameters
    ----------
    path : str
        Path to folder with nested folders

    Returns
    -------
    IMG_SUBS : list
        list of all subfolders in given folder
    """
    IMG_PATH = resolve_path(path)

    # Get all subfolders
    IMG_SUBS = [f for f in IMG_PATH.iterdir() if f.is_dir()]
    return IMG_SUBS

def get_amount_of_files(path, filetype=["*.tif", "*.tiff"]):
    """
    Loops over entire given folder (including subfolders!) and returns amount of files for given file type.

    Parameters
    ----------
    path : str
        Path to folder with files to be counted. Can have nested folders.
    filetype : str, optional
        File type to count. Defaults to *.tif"

    Returns
    -------
    int
        Number of files in given folder
    """
    path = resolve_path(path)
    files = []
    for ftype in filetype:
        files.extend([f for f in path.rglob(ftype)])
    return len(files)

def parse_file_name_for_seed_image_relations(filepath, seed_delimiter, seed_image_delimiter):
    """Parses file name for determination of seed and its images.
    By default assumes that image name structure is as follows: 'seed shortcut name_SeedNumber--SeedImageNumber.tif

    Parameters
    ----------
    filepath : Pathlib.Path
        Pathlib path to file which should be processed
    seed_delimiter : str
        Delimired which marks the position of seed number. Eg. "_"
    seed_image_delimiter : str
        Delimiter which separetes seed number from image number. Eg. "--"

    Returns
    -------
    seed_nr : str
        Extracted seed number
    img_nr : str
        Extracted image number
    """
    file = filepath.stem # Get filename
    seed_nr_index = file.find(seed_delimiter) # Find seed delimiter, if not found return "none"
    if seed_nr_index == -1:
        seed_nr = "none"
        img_nr = "none"
    else:
        temp = file[seed_nr_index:].split("_")[1]
        # Sometimes biologists decide to put diaspore or other funny words in the name of file, catch it and process it
        if temp.lower() in IMAGE_ADDITIONS:
            temp = file[seed_nr_index:].split("_")[2]

        temp = temp.split(seed_image_delimiter) # Catch if no image number was specified - assume no group
        if len(temp) < 2:
            seed_nr = "none"
            img_nr = "none"
        else:
            seed_nr = temp[0]
            img_nr = temp[1]

    return seed_nr, img_nr

def get_groups(path, seed_delimiter = "_", seed_image_delimiter = "--", filetype=["*.tif", "*.tiff"]):
    """Gets image groups for seeds based on delimiter pattern used on creation

    Parameters
    ----------
    path : str
        Path to folder with files to group by delimiters
    seed_delimiter : str, optional
        Delimired which marks the position of seed number, by default "_"
    seed_image_delimiter : str, optional
        Delimiter which separetes seed number from image number, by default "--"
    filetype : list, optional
        file types which should be considered as images to evaluate, by default [".tif", ".tiff"]

    Returns
    -------
    list
        list of lists with grouped file paths according to seed number
    """
    groups = []
    files = []
    path = resolve_path(path)
    # Load all file's paths for specified filetype
    for ftype in filetype:
        files.extend(path.glob(ftype))

    # Get groups of images for same seed based on delimiters
    current_group , _ = parse_file_name_for_seed_image_relations(files[0], seed_delimiter, seed_image_delimiter)
    if current_group == "none":
        current_group = "0"

    group = []
    for file in files:
        seed_nr, img_nr = parse_file_name_for_seed_image_relations(file, seed_delimiter, seed_image_delimiter)
        if seed_nr == current_group:
            group.append(file.as_posix())
        elif seed_nr == "none":
            if len(group) != 0:
                groups.append(group)
            groups.append([file.as_posix()])
            group = []
        else:
            if len(group) != 0:
                groups.append(group)
            group = [file.as_posix()]
            current_group = seed_nr
    if len(group) != 0:
        groups.append(group) # Append last group to groups

    return groups

def raw_data_processing(pair, origin):
    """Processed one image with its associated meta data.
    Calculates seed dimensions, color, boundingbox ratio.

    Parameters
    ----------
    pair : list
        Pair of image to be processed with associated metadata
    origin : str
        Type of microscope used to aquire data

    Returns
    ------
    dictionary
        Dictionary describing one image file
    """
    # lets process those damn data!
    imag = pair[0]
    meta = pair[1]

    # Parse meta data
    data = parse_meta(meta, origin=origin)

    # Process image data
    max_x_dist, max_y_dist, area, hex_color = ip.preproces_seed_image(imag)
    # Catch if image processing failed
    if max_x_dist == 0 or max_y_dist == 0 or area == 0:
        data['x_length'] = 0
        data['y_length'] = 0
        data['area'] = 0
        data['bound_seed_ratio'] = 0
    else:
        # Convert pixels to um
        data['x_length'] = px_to_metric(max_x_dist, data['scaling']['x'], data['scalingunit'])
        data['y_length'] = px_to_metric(max_y_dist, data['scaling']['y'], data['scalingunit'])
        data['area'] = px_to_metric(area, (data['scaling']['x']+data['scaling']['y'])/2,
                                    data['scalingunit'])
        data['bound_seed_ratio'] = data['area'] / (data['x_length'] * data['y_length'])
    data['hex_color'] = "#"+hex_color
    data['img_path'] = imag
    data['meta_path'] = meta
    return data

def main(path, origin, generator=True, save=False, consolecall=False):
    """
    Checks content of given folder for .tif files and their associated meta data.
    For each image reads relevant data from its meta data and calculates
    size of seed on provided image as well as its average color.

    Parameters
    ----------
    path : str
        Path to folder with seed folders which contain images and meta data
    origin : str
        Origin of images. Important to say, which microscope took the pictures
        Changes the extraction of meta data
    save : Bool, optional
        Changes whether output of processing should be saved as json or not to cwd.
        Defaults to False

    Returns
    -------
    None
    or
    data : dict
        Dictionary containing all extracted informations from both meta data and

    Raises
    ------
    NotImplementedError
        Should never occure, unless you change the code below. Indicates more groups than defined
    """
    IMG_SUBS = resolve_folders(path)
    data_out = []
    # Open folders one by one and process images inside
    for folder in IMG_SUBS:
        # Get species name. Folder naming is important!
        SPECIES_NAME = folder.name.title()
        if consolecall:
            print(f"Now processing {SPECIES_NAME}")
        # Check opened folder has nested folders
        diaspore = [f for f in folder.iterdir() if f.is_dir()]
        if len(diaspore) >= 1:
            # Check if in found folders there is one named diaspore
            for subfolder in diaspore:
                if subfolder.name.lower() == 'diaspore':
                    # If there is one, lets get them in image groups and get img and meta data paths
                    groups = get_groups(subfolder)
                    pairs = img_meta_pair(groups, origin)
                    if pairs is not None:
                        DIASPORE_CONTENT_GROUPS = pairs
                    else:
                        DIASPORE_CONTENT_GROUPS = []
        else:
            DIASPORE_CONTENT_GROUPS = []

        # Lets get seed and meta data paths
        try:
            groups = get_groups(folder)
            pairs = img_meta_pair(groups, origin)
            if pairs is not None:
                SEED_CONTENT_GROUPS = pairs
            else:
                SEED_CONTENT_GROUPS = []
        except IndexError:
            SEED_CONTENT_GROUPS = []

        for nr, groups in enumerate([DIASPORE_CONTENT_GROUPS, SEED_CONTENT_GROUPS]):
            group_temp = []
            for group in groups:
                for pair in group:
                    data = raw_data_processing(pair, origin)
                    # Add species name to data
                    data['species_name'] = SPECIES_NAME
                    # Add seed or diaspore. Diaspore = 0, Seed = 1
                    if nr == 0:
                        data['type'] = ['Diaspore']
                    elif nr == 1:
                        data['type'] = ['Seed']
                    else:
                        raise NotImplementedError("Unexpected type classificator. nr should be only 0 or 1.")

                    group_temp.append(data)
                if generator:
                    yield group_temp
                data_out.append(group_temp)
                group_temp = []
    if save:
        if consolecall:
            print("Saving results...")
        with open(cwd / "preload_data.json", 'w') as fout:
            json.dump(data_out , fout, indent=2)
    if not generator:
        return data_out

def preload_data(input_path, origin, output_path="", save=False, relative=False, consolecall=False, progresshandler=None):
    """
    Prepares data for delayed upload. Extracts all required data from metadata and images and saves
    or returns them as dictionary or json.

    Parameters
    ----------
    input_path : str
        Folder with images which should be prepared for upload.
    origin : str
        Origin microscope where the images were taken. Changes meta data processing
    output_path : str, optional
        Output where json should be stored. Defaults to "" which means cwd.
    save : Bool, optional
        Toggles saving of preloaded data as json. Saves as preload_data.json The default is False.
    relative : Bool, optional
        Toggles whether preloaded directory should be relative or absolute. Relative directory can
        be later uploaded even from different computer. The default is False.
    consolecall : Bool, optional
        Toggles console prints about processing status. Usefull when scrip runs without GUI.
    progresshandler : method
        Method of GUI which manages progressbar. Method has to accept 2 arguments. Numeric count of
        processed file. Bool finished is flag on last execution to let GUI know evertything is done

    Returns
    -------
    list or numeric
        If no saving is enforced, preload_data return list of dictionaries with preloaded data to be
        uploaded. If saving is enforced, returns number of saved elements in generated json
        (file count).
    """
    global BREAK
    # Preload groups in generator
    group_generator = main(input_path, origin=origin, consolecall=consolecall, generator=True)

    if save:
        # Check, if path is relative or has to be cwd
        output_path = Path(output_path).parts
        if len(output_path) == 1:
            output_path = rcwd / output_path[0]
        elif len(output_path) > 1:
            output_path = Path(*output_path)
        else:
            output_path = rcwd

    # Holder for output list
    output_holder = []
    ct = 0
    while not BREAK:
        try:
            # Get one group and process it
            group = next(group_generator)
            temp_group = []
            for data in group:
                if relative:
                    try:
                        data['img_path'] = data['img_path'].relative_to(rcwd).as_posix()
                        data['meta_path'] = data['meta_path'].relative_to(rcwd).as_posix()
                    except ValueError: # Not nices way to catch paths but hey it works
                        data['img_path'] = data['img_path'].as_posix()
                        data['meta_path'] = data['meta_path'].as_posix()
                else:
                    data['img_path'] = data['img_path'].as_posix()
                    data['meta_path'] = data['meta_path'].as_posix()
                temp_group.append(data)
                ct += 1
                if progresshandler:
                    progresshandler(ct, ct_max=None)
            # Append group to output list and reset temp group
            output_holder.append(temp_group)
            temp_group = []
        except StopIteration:
            if consolecall:
                print("All data have been processed.")
            break
    BREAK = False
    if progresshandler:
        progresshandler(ct, ct_max=None, finished=True)
    # If promted save groups as json, else return list of lists with dictionaries
    if save:
        if consolecall:
            print("Saving results...")
        with open(output_path / "preload_data.json", 'w') as fout:
            json.dump(output_holder , fout, indent=2)
        # If saving, returns number of groups in json
        return ct
    else:
        return output_holder

if __name__ == "__main__":
    # Runs this script in current working directory. Looks for folder
    # named to_be_uploaded
    print('main processing function test')

    PATH = "..//JCU_ArcheoPlant_Uploader//test"
    # PATH = r"C:\Users\anonn\Downloads\seeds"
    file = main(PATH, 'zeiss axiocam 305c')

    # PATH = "..//JCU_ArcheoPlant_Uploader//keyence"
    # file = main(PATH, 'keyence', consolecall=True)
    print("Test successful!\n", next(file))

    print("preload_data function test")

    output = preload_data(PATH, "Zeiss Axiocam 305c")
    # output = preload_data(PATH, "Keyence")
    print("Test successful!\n", output)