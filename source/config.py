"""
    Configuration file for uploadergui.
    Text values should start and end with " other way app wont be able to run.
    Image suffixes have to be separeted by , and each of the elements has to
    start and end with ".
"""
# Database upload presets for given batch of data. Change these accoring to
# your liking, otherway script writes some defaults.
DOCUMENT_SET = "ArcheoPlant - CZ/DE - 2021-09-07"
MIN_USERNAME_LENGTH = 3
LOCATION_DESCRIPTION = "Uploaded from University Southern Bohemia"
NOTE = None
TAGS = None

# Image suffix names which shall be filtered out from name space.
IMAGE_SUFFIX_NAMES = ["_c1", "_c2", "_c3"]

# additional pad border size for better contour detection
# in percent of original width
BORDER_SIZE = 0.01

# Thresholds for bcgrnd removal using HUE difference
L_THRESH = 80
H_THRESH = 135

# Thresholds for contour sorting based on area
L_AREA = 8000
H_AREA = 4000000

# Uploader settings
CHUNK_SIZE = 1000000