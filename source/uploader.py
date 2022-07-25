# -*- coding: utf-8 -*-
"""
uploader.py: Upload connector to UniCatDB. This uploader support is designed for Seed schema with
python scripts.

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
__version__ = "1.1.0"
__maintainer__ = ["Ondrej Budik"]
__email__ = ["obudik@prf.jcu.cz"]
__status__ = "Beta"

__python__ = "3.8.0"

# Import required libs
from datetime import datetime
from pathlib import Path
import numpy as np
import json

from uploader_frame import ConnectorFrame, dtformating
from dataprocess import resolve_path

import unicatdb
from unicatdb.openapi_client import FindingSingleResponse, FindingResourceObject, \
    NewFindingRequestBody, RelationshipResourceIdentifier, ResponseRelationshipOneToOne, \
    FindingResourceObjectRelationships, TaxonomyName, Finding
from pprint import pprint

# Check if uploader frame has correct version
from uploader_frame import __version__ as __upv__
from version_check import check_version
check_version(__upv__, [1, 0, 2], "uploader_frame.py")

# Global for interupting the script
BREAK = False

# Connector class
class Connector(ConnectorFrame):
    """
    Connector to UniCatDB for ARCHEOPLANT project. Inerhits ConnectorFrame methods
    and setting loader. Custom commit_one and commit_all for archeoplant project database
    is developed in this connector.
    """
    def __init__(self):
        """
        Constructor of Connector class. For full documentation do see class doc.
        """
        # init parent
        super(Connector, self).__init__()

    def commit_one_group(self, group, uploaderhandler=None, consolecall=False, chunk=unicatdb.Constants.DEFAULT_CHUNK_SIZE):
        """
        Commits one finding for given json data. List of findings should use
        commit_all method, here it will end in an exception.

        Parameters
        ----------
        data : dict
            Dictionary of data to be uploaded. Schema should follow the dataprocess.py
            syntax otherway it will result in an error.
        uploaderhandler : method, optional
            Method of uploader progress report. Recieves message by TUS procotol which has to be processed
            in accordance with ones liking (in our GUI it is processed onto progress bar). Defaults to None
        consolecall : Bool, optional
            Toggle if console callbacks are enabled / mostly usefull for debugging
        chunk : int, optional
            Size of chunks which should be uploaded. Current server limit is set around 10MB per request. Defaults to 1MB

        Returns
        -------
        None.

        """
        # Check if uploadhandler has been specified
        if not uploaderhandler:
            uploaderhandler = self.__dummy_uploadhandler__
        # Get common data from group for entire upload
        data = group[0]
        # Create a new finding in defined schema'
        with unicatdb.Client(self.config) as client:
            new_finding = Finding(
                document_name=data["species_name"],
                amount=len(group),
                document_set=self.setup["document_set"],
                date=self.setup['date'].split("T")[0],
                person=data["user"] if "user" in data.keys() else "Raw Script",
                location_description=self.setup["loc_desc"],
                location_gps_point=None,
                location_gps_area=None,
                note=self.setup["note"] if self.setup["note"] != None else "Automatic script upload",
                tags=self.setup["tags"] if self.setup["tags"] != None else data["species_name"].split(" "),
                taxonomy_human_readable=data["species_name"],
                taxonomy_name=(TaxonomyName(
                    kingdom=None,
                    phylum=None,
                    _class=None,
                    order=None,
                    family=None,
                    genus=None,
                    species=None,
                    authorship=None
                )),
                attachment_note="Automatic script upload",
                dynamic_data=({
                    "number-1657784374772-average-max-lenght-m": self.get_average_length(group),
                    "select-1658750400227-type": self.setup['type'],
                    "text-1657785026284-collection-organization": self.setup['organization'],
                    "text-1657784892422-internal-number": self.get_internal_number(data['species_name']),
                    "number-1657784595002-shape-number-by": -1,
                    "nested-1657785596588-imagemetadata": self.create_dynamic_group(group)
                  })
            )
            # assign to schema
            new_finding_relationships = FindingResourceObjectRelationships(
                schema=(ResponseRelationshipOneToOne(
                    data=(RelationshipResourceIdentifier(
                        type="schemas",
                        id="62cfc8e56b1ba989d26fa296"     # ID of schema 'ArcheoPlant - Seeds (Automatic upload)'
                    ))
                ))
            )
            # construct request payload
            create_finding_request = NewFindingRequestBody(data=(
                FindingResourceObject(
                    type="findings",
                    attributes=new_finding,
                    relationships=new_finding_relationships
                )
            ))
            #print(create_finding_request)
            # workspace ID
            workspace_id = "61c1a8c84904bdceecf50f65"

            # Commit finding
            try:
                # insert new finding (make POST API call with request payload)
                insert_result: FindingSingleResponse = client.findings.api_findings_post(
                    workspace_id,
                    new_finding_request_body=create_finding_request
                )

                # pretty-print inserterted finding
                if consolecall:
                    pprint(insert_result)

            except Exception as e:
                # add custom error handling code her
                print("Error occured when insering new finding: " + str(e.__class__.__name__) + " " + e.__str__())

            # Upload image and meta data
            try:
                finding_id = insert_result.data.id

                # get prepared TUS protocol for uplading files
                tus_client = client.get_tus_client_for_finding(workspace_id, finding_id)
                # File size
                for data in group:
                    file_size = Path(data['img_path']).stat().st_size
                    #data['meta_path'] = data['meta_path'].as_posix()
                    # Number of chunks
                    nr_chunks = -(-file_size // chunk)
                    # create uploader for our file, don't forget to provide required metadata
                    uploader = tus_client.uploader(
                        data['img_path'],
                        metadata={
                            "fileName": data['img_path'].split('/')[-1],
                            "contentType": "image/"+data['img_path'].split(".")[-1]
                        },
                        chunk_size=chunk,   # set chunk size in Bytes (1MB is the default)
                        log_func= lambda msg: uploaderhandler(msg, file_size, chunk=chunk, nr_chunks=nr_chunks) ## print the progress to console or to GUI upload handler
                    )
                    # Uploads the entire image file and meta data
                    # This uploads chunk by chunk.
                    uploader.upload()
                    # create uploader for our file, don't forget to provide required metadata
                    tus_client = client.get_tus_client_for_finding(workspace_id, finding_id)
                    uploader = tus_client.uploader(
                        data['meta_path'],
                        metadata={
                            "fileName": data['meta_path'].split('/')[-1],
                            "contentType": "text/"+data['meta_path'].split(".")[-1]
                        },
                        chunk_size=chunk   # set chunk size in Bytes (1MB is the default)
                        )
                    # Uploads the entire image file and meta data
                    # This uploads chunk by chunk.
                    uploader.upload()

            except Exception as e:
                print("Error occured when uploading: " + str(e.__class__.__name__) + " " + e.__str__())

    def get_internal_number(self, species):
        """Gets internal number from setup (config) for given seed. If no internal number is known,
        sets value to predefined "none" in config.

        Parameters
        ----------
        species : str
            Name of seed for which internal number should be obtained

        Returns
        -------
        str
            internal number if specified in config
        """
        species = species.lower()
        int_numbers_set = self.setup["internal_number"][self.setup["organization"].upper()]

        if species in int_numbers_set.keys():
            int_number = int_numbers_set[species]
        else:
            int_number = int_numbers_set["none"]

        return str(int_number)

    def create_dynamic_group(self, group):
        """Creates dynamic group list for upload. Group means all images of one seed.
        Groups are assigned automatically by dataprocessor. Groups are assigned by file names, thefore human error might be a problem.

        Parameters
        ----------
        group : list of dicts
            List of dictionaries containing all processed info about target image files.

        Returns
        -------
        list of dictionaries
            list containing all dynamic data for given upload task
        """
        # Get dynamic group holder
        group_holder = []
        for data in group:
            temp = {
                "text-1657788134621-filename": data['img_path'].split('/')[-1],
                "select-1657785726708-select": data['type'][0],
                "date-1657785708118-acquisition-date-and-time": dtformating(datetime.fromtimestamp(data['timestamp'])),
                "text-1657785710793-focus-method": data['focusmethod'],
                "text-1657785712782-texture-method": data['texturemethod'],
                "text-1657785714605-topography-method": data['topographymethod'],
                "text-1657786114201-detector-vendor": data['vendor'],
                "text-1657786238783-detector-model": data['model'],
                "text-1657786116651-adapter-model": data['adapter'],
                "text-1657786116236-objective-model": data['objective'],
                "select-1657786839385-default-scaling-unit": data['scalingunit'],
                "number-1657786456044-pixel-accuracy": data['pixelaccuracy'],
                "text-1657786573752-pixel-distances": str(data['pixeldistance']),
                "number-1657786783357-total-magnification": data['totalmagnification'],
                "text-1657787250718-sdk-version": data['sdk'],
                "number-1657787350620-pixel-to-m-in-x": data['scaling']['x'],
                "number-1657787355145-pixel-to-m-in-y": data['scaling']['y'],
                "number-1657787354751-size-of-normalized-seed-in-x-m": data['x_length'],
                "number-1657787354379-size-of-normalized-seed-in-y-m": data['y_length'],
                "number-1657787354016-area-of-seed-m": data['area'],
                "number-1657787353571-seed-to-bounding-box-ratio": data['bound_seed_ratio'],
                "text-1657787521336-average-seed-color-hex": data['hex_color']
            }
            group_holder.append(temp)
        return group_holder

    def get_average_length(self, group):
        """Calculates maximal average length for X and Y axis

        Parameters
        ----------
        group : list of dicts
            List of dictionarias which contain processed metadata about images

        Returns
        -------
        numeric
            Maximal average length of given seed
        """

        # Get holders for X and Y. (Preprocessing should always keep X as the longest value, but lets be sure)
        x_length = []
        y_length = []

        for data in group:
            x_length.append(data['x_length'])
            y_length.append(data['y_length'])

        # Always get the highest value
        length_out = np.max([np.mean(x_length), np.mean(y_length)])
        return length_out

    def commit_all(self, PATH_TO_JSON, user="Test Script in uploader", progresshandler=None, uploaderhandler=None, consolecall=None):
        """
        Commits all files preloaded in given json to database. Commits uploads group by group.
        Tries to finish running upload even on interrupt.

        Parameters
        ----------
        PATH_TO_JSON : str
            String path to json with preprocessed data. Will be translated to Pathlib.Path.
        user : str, optional
            User name who commits current batch to DB for easy fail detection and rollbacks.
            Defaults to "Test Script".
        progresshandler : method, optional
            Handler for attached GUI of its progressbar. Defaults to None.
        uploaderhandler : method, optional
            Handler for attached GUI of its uploadbar. Defaults to None.
        consolecall : bool, optional
            Bool trigger for console prints for easier debugging. Defaults to False

        Returns
        -------
        None.

        """
        # Global for interrupts
        global BREAK

        # Resolve paths for uploads
        PATH = resolve_path(PATH_TO_JSON).resolve()
        PARENT = PATH.parent

        # Load preprocessed data stored in JSON
        with open(PATH, "r") as f:
            file = json.loads(f.read())

        # Get amount of files to process for progression bar vizualization
        progress_counter_max = sum([len(listElem) for listElem in file])+1
        progress_counter = 0

        if progresshandler:
            progresshandler(progress_counter, ct_max=progress_counter_max)

        for group in file:
            if BREAK:
                break
            try:
                for pair in group:
                    # Resolve path for payload
                    if not Path(pair['img_path']).is_absolute():
                        abspath = PARENT / Path(pair['img_path'])
                        pair['img_path'] = abspath.as_posix()
                    if not Path(pair['meta_path']).is_absolute():
                        abspath = PARENT / Path(pair['meta_path'])
                        pair['meta_path'] = abspath.as_posix()

                    pair['user'] = user
                # Upload all elements one by one
                self.commit_one_group(group, uploaderhandler)
                # increment loop and progress bar
                progress_counter += len(group)
                if progresshandler:
                    progresshandler(progress_counter, ct_max=progress_counter_max)

            except Exception as e:
                print("Undefined Error in commit all occured:" + str(e.__class__.__name__) + " " + e.__str__())
                break
        print("All data have been uploaded.")
        BREAK = False
        if progresshandler:
            progresshandler(progress_counter, ct_max=progress_counter_max, finished=True)

    def __dummy_uploadhandler__(self, msg, file_size, chunk=0, nr_chunks=0):
        """
        Dummy for uploadhandler, in case none is provided. Prints progress into console.
        """
        print(msg)


if __name__ == "__main__":
    connector = Connector()
    with open("../preload_data.json", "r") as f:
        test_j = json.loads(f.read())
    # Commit !st data pack from preloaded json
    one_j = test_j[0]
    one_j['user'] = "Test Script"
    #connector.commit_one(one_j)
    connector.commit_all('../preload_data.json')
