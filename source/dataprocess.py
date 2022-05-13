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
__version__ = "1.0.6"
__maintainer__ = ["Ondrej Budik", "Vojtech Barnat"]
__email__ = ["obudik@prf.jcu.cz", "Vojtech.Barnat@fs.cvut.cz"]
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
from config import IMAGE_SUFFIX_NAMES

# Get current working directory for file management as global var
cwd = Path.cwd()
rcwd = cwd / ".."
rcwd = rcwd.resolve()

# Global for interupting the script
BREAK = False

# Functions definition
def img_meta_pair(subfolder):
    """
    Takes subfolder with *.tifs and pairs them together with their meta data in based on their names.
    If names do not match (except suffix), automatic pairing can not be performed and files will be ignored

    Parameters
    ----------
    subfolder : pathlib.Path
        Pathlib object with specified path destination to desired folder

    Returns
    -------
    groups_holder : list
        Contains list of lists. Each nested list has 2 paired objects. [[img, meta], [img, meta], ...]
    """
    groups_holder = []
    for img_file in subfolder.glob('*.tif'):
        # Fix some of their weird naming
        if img_file.stem[-3:] in IMAGE_SUFFIX_NAMES:
            temp_img_file = img_file.stem[:-3]
        else:
            temp_img_file = img_file
        # Append meta to path stem
        meta_temp = str(temp_img_file) + "_meta.xml"
        meta_file = img_file.parent / meta_temp
        if not meta_file.is_file():
            print(f"\nFor image {img_file.stem} in {meta_file.parent} were no meta data found! File is excluded from upload.\n")
            continue
        groups_holder.append([img_file, meta_file])
    return groups_holder

def __zeis_parser__(meta_dict):
    """
    Processing of ZEIS microscope meta data. In case ZEIS would change their xml structure, this
    processing has to be altered! If more informations are required to extract, this is the place
    to do so.

    Parameters
    ----------
    meta_dict : dict
        XML converted to dictionary for easy data manipulation in python.

    Returns
    -------
    parsed_meta : dict
        Dictionary containing desired data
    """
    # Prepare holder for output meta
    parsed_meta = {}
    # Capture postprocessing methodic
    capture_property = meta_dict['ImageMetadata']['Experiment']['ExperimentBlocks']['AcquisitionBlock']['SubDimensionSetups']['ZStackSetup']['SetupExtensions']['SetupExtension'][0]['ZStackSetupExtension']
    parsed_meta['focusmethod'] = capture_property['FocusMethod']
    parsed_meta['texturemethod'] = capture_property['TextureMethod']
    parsed_meta['topographymethod'] = capture_property['TopographyMethod']
    # Used detector
    detector = meta_dict['ImageMetadata']['Information']['Instrument']['Detectors']['Detector']
    parsed_meta['model']= detector['Manufacturer']['Model']
    parsed_meta['adapter'] = detector['Adapter']['Manufacturer']['Model']
    # Used objective
    objective = meta_dict['ImageMetadata']['Information']['Instrument']['Objectives']['Objective']
    parsed_meta['objective'] = objective['Manufacturer']['Model']
    # Hardware settings
    hardware = meta_dict['ImageMetadata']['HardwareSetting']['ParameterCollection'][1]
    parsed_meta['pixelaccuracy'] = float(hardware['CameraPixelAccuracy'][list(hardware['CameraPixelAccuracy'].keys())[-1]])
    parsed_meta['pixeldistance'] = list(map(float, hardware['CameraPixelDistances'][list(hardware['CameraPixelDistances'].keys())[-1]].split(",")))
    parsed_meta['totalmagnification'] = float(hardware['TotalMagnification'][list(hardware['TotalMagnification'].keys())[-1]])
    parsed_meta['scalingunit'] = hardware['DefaultScalingUnit'][list(hardware['DefaultScalingUnit'].keys())[-1]]
    parsed_meta['sdk'] = hardware['SDKVersion'][list(hardware['SDKVersion'].keys())[-1]]
    # Scaling props
    scaling = meta_dict['ImageMetadata']['Scaling']['Items']['Distance']
    temp_scale = {}
    for scale in scaling:
        temp_scale[scale['@Id'].lower()] = float(scale['Value'])
    parsed_meta["scaling"] = temp_scale
    return parsed_meta

def parse_meta(xml_path, origin='zeis'):
    """
    Takes path to xml file with microscope meta data and extracts desired data for specified database.

    Parameters
    ----------
    xml_path : str or pathlib.Path
        Path to target xml file with meta data to parse.
    origin : str, optional
        Origin of meta data. Important for various parsing mechanisms. Defaults to zeis.

    Returns
    -----
    parsed_meta : dict
        Dictionary containing parsed data from given xml file.
    """
    # Load xml and convert it to dict
    meta_dict = xmltodict.parse(ET.tostring(ET.parse(xml_path).getroot()))

    # read meta data for specific manufacturer
    if origin.lower() == 'zeis':
        parsed_meta = __zeis_parser__(meta_dict)
    elif origin.lower() == 'keyens':
        raise NotImplementedError("We are not there yet..")
    else:
        raise IOError("Unknown meta data origin! Please code missing meta parser.")

    # Get creation data
    parsed_meta['timestamp'] = xml_path.stat().st_ctime
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

def get_amount_of_files(path, filetype=".tif"):
    """
    Loops over entire given folder and returns amount of files for given file type.

    Parameters
    ----------
    path : str
        Path to folder with files to be counted. Can have nested folders.
    filetype : str, optional
        File type to count. Defaults to "*.tif"
    """
    path = resolve_path(path)

    files = [f for f in path.rglob("*.tif")]
    return len(files)


def main(path, origin, save=False, consolecall=False):
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
        Changes whether output of processing should be saved as json or not.
        Defaults to False

    Yields
    -------
    data : dict
        Dictionary containing all extracted informations from both meta data and
    """
    IMG_SUBS = resolve_folders(path)

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
                    # If there is one, lets get img and meta data paths
                    pair = img_meta_pair(subfolder)
                    if pair is not None:
                        DIASPORE_CONTENT_GROUPS = pair
                    else:
                        DIASPORE_CONTENT_GROUPS = []
        else:
            DIASPORE_CONTENT_GROUPS = []

        # Lets get seed and meta data paths
        pair = img_meta_pair(folder)
        if pair is not None:
            SEED_CONTENT_GROUPS = pair
        else:
            SEED_CONTENT_GROUPS = []

        # DATA are now loaded, lets process em!
        for nr, groups in enumerate([DIASPORE_CONTENT_GROUPS, SEED_CONTENT_GROUPS]):
            for group in groups:
                imag = group[0]
                meta = group[1]

                # Parse meta data
                data = parse_meta(meta, origin=origin)
                # Add species name to data
                data['species_name'] = SPECIES_NAME
                # Add seed or diaspore. Diaspore = 0, Seed = 1
                if nr == 0:
                    data['type'] = ['Diaspore']
                elif nr == 1:
                    data['type'] = ['Seed']
                else:
                    raise NotImplementedError("Unexpected classificator. nr should be only 0 or 1.")

                # Process image data
                max_x_dist, max_y_dist, area, hex_color = ip.preproces_seed_image(imag)

                # Convert pixels to um
                data['x_length'] = px_to_metric(max_x_dist, data['scaling']['x'], data['scalingunit'])
                data['y_length'] = px_to_metric(max_y_dist, data['scaling']['y'], data['scalingunit'])
                data['area'] = px_to_metric(area, (data['scaling']['x']+data['scaling']['y'])/2,
                                            data['scalingunit'])
                data['bound_seed_ratio'] = data['area'] / (data['x_length'] * data['y_length'])
                data['hex_color'] = "#"+hex_color
                data['img_path'] = imag
                data['meta_path'] = meta
                yield data

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
    # Init generator
    data_generator = main(input_path, origin=origin, consolecall=consolecall)

    if save:
        # Check, if path is relative or has to be cwd
        output_path = Path(output_path).parts
        if len(output_path) == 1:
            output_path = rcwd / output_path[0]
        elif len(output_path) > 1:
            output_path = Path(*output_path)
        else:
            output_path = rcwd

    output_holder = []
    ct = 0
    while not BREAK:
        try:
            data = next(data_generator)
            if relative:
                try:
                    data['img_path'] = data['img_path'].relative_to(rcwd).as_posix()
                    data['meta_path'] = data['meta_path'].relative_to(rcwd).as_posix()
                except ValueError:
                    data['img_path'] = data['img_path'].as_posix()
                    data['meta_path'] = data['meta_path'].as_posix()
            else:
                data['img_path'] = data['img_path'].as_posix()
                data['meta_path'] = data['meta_path'].as_posix()
            output_holder.append(data)
            ct += 1
            if progresshandler:
                progresshandler(ct, ct_max=None)
        except StopIteration:
            if consolecall:
                print("All data have been processed.")
            break
    BREAK = False
    if progresshandler:
        progresshandler(ct, ct_max=None, finished=True)
    if save:
        if consolecall:
            print("Saving results...")
        with open(output_path / "preload_data.json", 'w') as fout:
            json.dump(output_holder , fout, indent=2)
        return ct
    else:
        return output_holder

if __name__ == "__main__":
    # Runs this script in current working directory. Looks for folder
    # named to_be_uploaded
    PATH = ".//test"
    file = main(PATH, 'zeis')
    print(next(file))