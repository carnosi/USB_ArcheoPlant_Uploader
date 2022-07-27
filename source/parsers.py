# -*- coding: utf-8 -*-
"""
parsers.py: Method of processing meta data for specific manufacturers and
microscope types. If desired parser is missing, just code it :)

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

# Parsers
def __zeiss_axiocam305c_parser__(meta_dict):
    """
    Processing of ZEISS Axiocam305c microscope meta data. In case ZEIS would change their xml structure, this
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
    # Hardware settings specific for Axiocam 305c
    hardware = meta_dict['ImageMetadata']['HardwareSetting']['ParameterCollection']
    for collection in hardware:
        if collection["@Id"] == 'MTBCamera_MTBTube_Cameraport.Axiocam305c':
            hardware = collection
            break
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
    parsed_meta["vendor"] = "Carl Zeiss"
    return parsed_meta

def __keyence_parser__(meta_dict):
    """
    Processing of KEYENCE microscope meta data. In case KEYENCE would change their xml structure, this
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

    # Logic #TODO
    raise NotImplementedError("We are not there yet..")

    parsed_meta["vendor"] = "Keyence"
    return parsed_meta