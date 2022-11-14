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
__version__ = "1.0.3"
__maintainer__ = ["Ondrej Budik"]
__email__ = ["obudik@prf.jcu.cz"]
__status__ = "Beta"

__python__ = "3.8.0"

import struct
from pathlib import Path
import exifread as exr

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
    try:
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
    except Exception as e:
        print("Exception on processing Zeiss meta data!", type(e).__name__, e)
        parsed_meta = __empty_dict__()
        parsed_meta["vendor"] = "Carl Zeiss"
    return parsed_meta

def __keyence_parser__(path_to_tif):
    """
    Processing of KEYENCE microscope meta data. Keyence does not use XML!
    They rather code the data inside of the tif file itself as binary.
    Offsets to data appended to the end of file are stored in MakerNotes exif.

    This parser works with their version 1 (written after KSMFILE identifier).
    If this version does not match, parser will return nulled except the version,
    as the data would most likely be corrupted anyway.

    Parameters
    ----------
    path_to_tif : path or str
        Path to file which should be processed

    Returns
    -------
    parsed_meta : dict
        Dictionary containing desired data
    """
    # Prepare holder for output meta
    parsed_meta = __empty_dict__()

    try:
        # Open file and get makernotes
        tif_file = Path(path_to_tif).resolve()

        # Get makernote position in file
        with open(tif_file, "rb") as file:
            makernote_offset = exr.process_file(file, details=True)['EXIF MakerNote'].field_offset

        # Read makernote on given offset
        with open(tif_file, "rb") as file:
            file.seek(makernote_offset)
            maker_notes_data = file.read()

        # Compose KmsFile from 0:7 byte, if no KmsFile is present, probly no keyence data.
        kmsfile = ""
        for char in range(0, 7):
            kmsfile += chr(maker_notes_data[char])
        # If version does not match, probly its not good idea to process data.
        maker_note_version = maker_notes_data[7]

        # Set flag in one of two identifiers do not match
        if kmsfile != "KmsFile" or maker_note_version != 1:
            print(f"Metadata in given tif file might be corrupted or not taken with Keyence! Processing skipped. KmsFile: {kmsfile}, Version: {maker_note_version}")
            parsed_meta = __empty_dict__()
            parsed_meta['sdk'] = f"{kmsfile} Version: {maker_note_version}"
            parsed_meta["vendor"] = "Keyence"
        else:
            parsed_meta['sdk'] = f"{kmsfile} Version: {maker_note_version}"
            parsed_meta["vendor"] = "Keyence"

            # Gen n tags
            tags_count = maker_notes_data[8]

            # tags dict holder
            maker_notes_tags = {}
            # Offset from start to where keyence data start
            offset = 10
            # Step size for iteration - number of bytes in each tag
            step = 12
            # Extract data according to their tags and keep them in a dict for easy access
            for tag in range(0, tags_count):
                start = offset + step*tag
                end = start + step
                split = maker_notes_data[start:end].hex()
                tagid = split[2:4]+split[0:2]
                maker_notes_tags[tagid] = split[4:]

            # Lens model
            lens_model_tagid = "011f"
            lens_model_tag = __extract_tag_with_offset__(lens_model_tagid, maker_notes_tags)
            lens_model = __lens_tag_parser__(tif_file, lens_model_tag["val_or_offset"], lens_model_tag["n_of_elements"])

            parsed_meta["model"] = lens_model["char_string_area"]

            # Lens magnification name
            lens_mag_tagid = "0010"
            lens__mag_tag = __extract_tag_with_offset__(lens_mag_tagid, maker_notes_tags)
            lens_mag = __lens_tag_parser__(tif_file, lens__mag_tag["val_or_offset"], lens__mag_tag["n_of_elements"])

            parsed_meta["objective"] = lens_mag["char_string_area"]

            # Lens calibration storage method
            lens_cali_tagid = "0011"
            lens_cali_tag = __extract_tag_with_offset__(lens_cali_tagid, maker_notes_tags)
            lens_cali = __lens_calibration_parser__(tif_file, lens_cali_tag["val_or_offset"], lens_cali_tag["n_of_elements"])

            # As of 14.11.2022 Keyence claims to always use um for this value. We can only hope that it will be the case, there is no info about units in meta data.
            # For our app we convert this value to m further down.
            parsed_meta["scalingunit"] = "\u00b5m"

            # Whether magnification-adjustmens calibration adjustment factors must be applied
            lens_magni_adj_tagid = "0143"
            lens_magni_adj_tag = __extract_tag_with_offset__(lens_magni_adj_tagid, maker_notes_tags)
            lens_magni_adj = __lens_calib_adj_parser__(tif_file, lens_magni_adj_tag["val_or_offset"], lens_magni_adj_tag["n_of_elements"])

            # Magnification-adjustment calibration adjustment factor
            if lens_magni_adj["value"]:
                lens_magni_cali_tagid = "0144"
                lens_magni_cali_tag = __extract_tag_with_offset__(lens_magni_cali_tagid, maker_notes_tags)
                lens_magni_cali = __lens_calibration_parser__(tif_file, lens_magni_cali_tag["val_or_offset"], lens_magni_cali_tag["n_of_elements"])
                magni_factor = lens_magni_cali["value"]
            else:
                magni_factor = 1.0

            # Whether filming-size calibration adjustment factors must be applied
            lens_film_adj_tagid = "0147"
            lens_film_adj_tag = __extract_tag_with_offset__(lens_film_adj_tagid, maker_notes_tags)
            lens_film_adj = __lens_calib_adj_parser__(tif_file, lens_film_adj_tag["val_or_offset"], lens_film_adj_tag["n_of_elements"])

            # Filming-size calibration adjustment factor
            if lens_film_adj["value"]:
                lens_film_cali_tagid = "0148"
                lens_film_cali_tag = __extract_tag_with_offset__(lens_film_cali_tagid, maker_notes_tags)
                lens_film_cali = __lens_calibration_parser__(tif_file, lens_film_cali_tag["val_or_offset"], lens_film_cali_tag["n_of_elements"])
                film_factor = lens_film_cali["value"]
            else:
                film_factor = 1.0

            # Whether digital-zoom calibration adjustment factors must be applied
            lens_digi_adj_tagid = "0145"
            lens_digi_adj_tag = __extract_tag_with_offset__(lens_digi_adj_tagid, maker_notes_tags)
            lens_digi_adj = __lens_calib_adj_parser__(tif_file, lens_digi_adj_tag["val_or_offset"], lens_digi_adj_tag["n_of_elements"])

            # Digital-zoom calibration adjustment factor
            if lens_digi_adj["value"]:
                lens_digi_cali_tagid = "0146"
                lens_digi_cali_tag = __extract_tag_with_offset__(lens_digi_cali_tagid, maker_notes_tags)
                lens_digi_cali = __lens_calibration_parser__(tif_file, lens_digi_cali_tag["val_or_offset"], lens_digi_cali_tag["n_of_elements"])
                digi_factor = lens_digi_cali["value"]
            else:
                digi_factor = 1.0

            # Calculate adjusted scaling factor based on equation provided by keyence
            scaling = (lens_cali["value"])/(magni_factor * film_factor * digi_factor)
            # Convert to m from um
            scaling = scaling * 10e-7

            parsed_meta["scaling"]["x"] = scaling
            parsed_meta["scaling"]["y"] = scaling

            #--------------------------------------#
            # 3d calibration
            calibration_3d_tagid = "0118"
            #TODO read out 3d texture processor. Not used in this project, not coded, just marked the tag.

            # 3d height data
            height_3d_data_tagid = "0119"
            #TODO read out 3d texture processor. Not used in this project, not coded, just marked the tag.

            # 3d texture (standard)
            texture_3d_standard_tagid = "011a"
            #TODO read out 3d texture processor. Not used in this project, not coded, just marked the tag.

            # 3d texture (stitched)
            texture_3d_stitch_tagid = "011c"
            #TODO read out 3d texture processor. Not used in this project, not coded, just marked the tag.

            # 3d texture (upper limit increased)
            texture_3d_increased_tagid = "01c9"
            #TODO read out 3d texture processor. Not used in this project, not coded, just marked the tag.
    except Exception as e:
            print("Exception on processing Keyence meta data!", type(e).__name__, e)

    return parsed_meta

def __empty_dict__():
    """
    Generated empty dictionary in case any processing fails.
    Additional data might be filled in for debugging purposes.

    Returns
    -------
    dict
        Empty dictionary with defined keys and value types
    """
    parsed_meta = {}
    parsed_meta['focusmethod'] = "nan"
    parsed_meta['texturemethod'] = "nan"
    parsed_meta['topographymethod'] = "nan"
    parsed_meta['model']= "nan"
    parsed_meta['adapter'] = "nan"
    parsed_meta['objective'] = "nan"
    parsed_meta['pixelaccuracy'] = 0.0
    parsed_meta['pixeldistance'] = [0.0, 0.0]
    parsed_meta['totalmagnification'] = 0.0
    parsed_meta['scalingunit'] = "nan"
    parsed_meta['sdk'] = "nan"
    parsed_meta["scaling"] = {"x" : 0.0, "y" : 0.0, "z" : 0.0}
    parsed_meta["vendor"] = "nan"

    return parsed_meta

def __extract_tag_with_offset__(key, maker_notes_tags):
    """
    Extracts informations from makernotes tags in keyence defined fashion

    Parameters
    ----------
    key : str
        key to process in hex
    maker_notes_tags : dict
        dict with all makernotes tags

    Returns
    -------
    dict
        parsed data for given tag stored in maker notes
    """

    # Prepare holder
    tag = {}
    # Save key
    tag["id"] = key
    # Parse maker notes tag
    hextag = maker_notes_tags[key]
    tag["data_type"] = int(hextag[2:4] + hextag[0:2], 16)
    tag["n_of_elements"] = int(hextag[10:12] + hextag[8:10] + hextag[6:8] + hextag[4:6], 16)
    tag["val_or_offset"] = hextag[18:20] + hextag[16:18] + hextag[14:16] + hextag[12:14]
    return tag

def __lens_tag_parser__(file, offset, number_of_elements):
    """
    Parser for lens model and magnification name.

    Parameters
    ----------
    file : path, str
        path to file from which should the data be retrieved
    offset : hexstr
        offset where data are stored in given file
    number_of_elements : int
        number of bytes which should be retrieved from offset

    Returns
    -------
    dict
        decoded lens namespace values saved in dictionary
    """

    # Prepare holder
    lens = {}
    # Load data
    with open(file, "rb") as file:
        file.seek(int(f"0x{offset}", 16))
        offset_data = file.read()[:number_of_elements]
    # Parse offset data
    lens["crc32"] = swapEndianness(offset_data[0:4].hex())
    lens["vartype"] = int(swapEndianness(offset_data[4:6].hex()), 16)
    lens["GUID"] = swapEndianness(offset_data[6:22].hex())
    lens["reserved"] = offset_data[22]
    lens["buffer_length"] = int(swapEndianness(offset_data[23:27].hex()), 16)
    lens["n_of_actual_characters"] = int(swapEndianness(offset_data[27:31].hex()), 16)
    lens["char_string_area"] = bytes.fromhex(offset_data[31:31+lens['n_of_actual_characters']*2].hex()).decode("utf-16")

    return lens

def __lens_calibration_parser__(file, offset, number_of_elements):
    """
    Parser for lens calibration storage method.

    Parameters
    ----------
    file : path, str
        path to file from which should the data be retrieved
    offset : hexstr
        offset where data are stored in given file
    number_of_elements : int
        number of bytes which should be retrieved from offset

    Returns
    -------
    dict
        decoded lens calibration namespace values saved in dictionary
    """

    # Prepare holder
    cali = {}
    # Load data
    with open(file, "rb") as file:
        file.seek(int(f"0x{offset}", 16))
        offset_data = file.read()[:number_of_elements]
    # Parse offset data
    cali["crc32"] = swapEndianness(offset_data[0:4].hex())
    cali["vartype"] = int(swapEndianness(offset_data[4:6].hex()), 16)
    cali["value"] = struct.unpack('!d', bytes.fromhex(swapEndianness(offset_data[6:14].hex())))[0]

    return cali

def __lens_calib_adj_parser__(file, offset, number_of_elements):
    """
    Whether magnification-adjustment, filming-size, and digital-zoom calibration adjustment factors must be applied

    Parameters
    ----------
    file : path, str
        path to file from which should the data be retrieved
    offset : hexstr
        offset where data are stored in given file
    number_of_elements : int
        number of bytes which should be retrieved from offset

    Returns
    -------
    dict
        decoded lens calibration namespace values saved in dictionary
    """

    # Prepare holder
    magni = {}
    # Load data
    with open(file, "rb") as file:
        file.seek(int(f"0x{offset}", 16))
        offset_data = file.read()[:number_of_elements]
    # Parse offset data
    magni["crc32"] = swapEndianness(offset_data[0:4].hex())
    magni["vartype"] = int(swapEndianness(offset_data[4:6].hex()), 16)
    temp = swapEndianness(offset_data[6:8].hex())
    if temp == "ffff":
        magni["value"] = True
    elif temp == "0000":
        magni["value"] = False
    else:
        magni["value"] = "corrupted values"

    return magni

def swapEndianness(hexstring):
    """
    Swaps endianness in a hexstring

    Parameters
    ----------
    hexstring : str
        hexstring which endianness should be swapped

    Returns
    -------
    str
        hexstring which is swapped from the original order
    """

    ba = bytearray.fromhex(hexstring)
    ba.reverse()
    return ba.hex()

if __name__ == "__main__":
    print(__keyence_parser__(r".\keyence\20220627_181313.tif"))