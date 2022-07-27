"""
    Configuration file for uploadergui.
    Text values should start and end with " other way app wont be able to run.
    Image suffixes have to be separeted by , and each of the elements has to
    start and end with ".
"""
# Database upload presets for given batch of data. Change these accoring to your liking. Keep the required fields occupied! Type dends on DB settings.

# Target server. Predefined are: "local", "test", "live". If other adress is provided it takes it as target
SERVER = "live"

# Document set name. Eg: "ArcheoPlant - CZ/DE - 2021-09-09"
DOCUMENT_SET = "ArcheoPlant - CZ/DE - 2022-04-01"

# Specifies type of the seed. Valid DB options are Recent and Archeo
TYPE = "Recent"

# Minimal username length accepted by user GUI in jupyter notebook
MIN_USERNAME_LENGTH = 3

# Description where data from which location data have been uploaded (NOT AQUIRED!)
LOCATION_DESCRIPTION = "Uploaded from University Southern Bohemia"

# Any note which should be uploaded with target data for given script task
NOTE = None

# Any extra tags which should be entered along side the seed name
TAGS = None

# Whom belong the originals Eg. "USB" for University Southern Bohemia, "RE" for Regensburg
COLLECTION_ORGANIZATION = "RE"

# If seed has internal number in relation to collection organization it should be filled in as dictionary
INTERNAL_NUMBER = {"RE":{
                        "agrimonia eupatoria":1613,
                        "anthriscus sylvestris":2164,
                        "centauerea scaviosa":3118,
                        "crepis biennis":3192,
                        "gallium mollugo":2387,
                        "knautia arvensis":2817,
                        "lathyrus pratensis":1882,
                        "leontodon autumnalis":3133,
                        "leontodon hispidus":3136,
                        "medicago falcata":1773,
                        "onovrychis viciifolia":1843,
                        "prunella vulgaris":2510,
                        "salvia pratensis":2545,
                        "tragopogon pratensis":3143,
                        "alopecurus pratensis":648,
                        "anthoxanthum odoratum":667,
                        "centaurea jacea":3107,
                        "cznosurus cristatus":533,
                        "dactylis glomerata":530,
                        "festuca pratensis":484,
                        "festuca rubra":"468d",
                        "geranium pratense":1909,
                        "platago lanceolata":2766,
                        "achillea millefolium":2979,
                        "ajuga reptans":2488,
                        "hypericum perforatum":2054,
                        "rumex acetosa":857,
                        "sangiusorba minor":1616,
                        "campanula patula":2844,
                        "campanula rotundifolia":2838,
                        "carum carvi":2199,
                        "daucus carota":2252,
                        "dianthus carthusianorum":979,
                        "galium verum":2390,
                        "leucanthemum vulgare":2999,
                        "lotus corniculatus":1809,
                        "poa pratensis": 523,
                        "ranunculus acris":1118,
                        "ranunculus repens":1114,
                        "rhinanthus alectorolophus":2707,
                        "silene vulgaris":946,
                        "trifolium pratense":1801,
                        "trifolium repens":1789,
                        "trisetum favescens":600,
                        "bormus erectus":472,
                        "festuca rubra":"486g",
                        "heracleum sphondylium":2244,
                        "hippocrepus comosa":1841,
                        "lychnis flos-cuculi":966,
                        "pimpinella major":2202,
                        "none":-1
                        },
                    "USB":{
                        "none":-1
                        }
                    }

# Image suffix names which shall be filtered out from name space.
IMAGE_SUFFIX_NAMES = ["_c1", "_c2", "_c3"]

# Image name additions before numbers
IMAGE_ADDITIONS = ["diaspore", "same", "hülle"]

# additional pad border size for better contour detection in percent of original width
BORDER_SIZE = 0.15

# Thresholds for bcgrnd removal using HUE difference
L_THRESH = 80
H_THRESH = 135

# Thresholds for contour sorting based on area
L_AREA = 8000
H_AREA = 4000000

# Uploader settings
CHUNK_SIZE = 1000000

# Color extraction settings
COLOR_SAMPLE_SIZE = 50
THRESHOLD_PAD = 20
COLOR_CNT_PAD = 2

#erode and dilatate
KERNEL_SIZE = 4
E_ITERS = 3
D_ITERS = 8
