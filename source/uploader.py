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
__version__ = "1.0.3"
__maintainer__ = ["Ondrej Budik", "Vojtech Barnat"]
__email__ = ["obudik@prf.jcu.cz", "Vojtech.Barnat@fs.cvut.cz"]
__status__ = "Beta"

__python__ = "3.8.0"

# Import required libs
from datetime import datetime
from pathlib import Path
import json

import numpy as np

from uploader_frame import ConnectorFrame, dtformating
from dataprocess import resolve_path

import unicatdb
from unicatdb.openapi_client import FindingSingleResponse, FindingResourceObject, \
    NewFindingRequestBody, RelationshipResourceIdentifier, ResponseRelationshipOneToOne, \
    FindingResourceObjectRelationships, TaxonomyName, Finding
from pprint import pprint

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

    def commit_one(self, data, uploaderhandler=None, consolecall=False, chunk=unicatdb.Constants.DEFAULT_CHUNK_SIZE):
        """
        Commits one finding for given json data. List of findings should use
        commit_all method, here it will end in an exception.

        Parameters
        ----------
        data : dict
            Dictionary of data to be uploaded. Schema should follow the dataprocess.py
            syntaxe.

        Returns
        -------
        None.

        """
        #print(data)
        # Create a new finding in schema 'Seeds - upload through python script'
        with unicatdb.Client(self.config) as client:
            new_finding = Finding(
                document_name=data["species_name"],
                amount=1,
                document_set=self.setup["document_set"],
                date=self.setup['date'].split("T")[0],
                person=data["user"],
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
                    "date-1644848282666-acquisition-date-and-time": dtformating(datetime.fromtimestamp(data['timestamp'])),
                    "text-1644848104897-focus-method": data['focusmethod'],
                    "text-1644848180434-texture-method": data['texturemethod'],
                    "text-1644848333876-topography-method": data['topographymethod'],
                    "checkbox-group-1645518756057-diaspore-or-seed": data['type'][0],
                    "text-1644848387883-detector-model": data['model'],
                    "text-1644848392167-adapter-model": data['adapter'],
                    "text-1644848396217-objective-model": data['objective'],
                    "number-1652084725954-camera-pixel-accuracy": data['pixelaccuracy'],
                    "text-1644849051111-camera-pixel-distances": str(data['pixeldistance']),
                    "number-1652084729470-total-magnification": data['totalmagnification'],
                    "text-1644849422898-default-scaling-unit": data['scalingunit'],
                    "text-1644849131230-sdk-version": data['sdk'],
                    "number-1652084954836-pixel-to-m-in-x": data['scaling']['x'],
                    "number-1652084976082-pixel-to-m-in-y": data['scaling']['y'],
                    "number-1652085036155-size-of-normalized-seed-in-x": data['x_length'],
                    "number-1652085109693-size-of-normalized-seed-in-y": data['y_length'],
                    "number-1652085136505-area-of-seed": data['area'],
                    "number-1652085164817-seed-to-bounding-box-ratio": data['bound_seed_ratio'],
                    "text-1644850436838-average-seed-color": data['hex_color']

                })
            )
            # assign to schema
            new_finding_relationships = FindingResourceObjectRelationships(
                schema=(ResponseRelationshipOneToOne(
                    data=(RelationshipResourceIdentifier(
                        type="schemas",
                        id="620a6d54303dcf57361dce6d"     # ID of schema 'ArcheoPlant - Seeds (Automatic upload)'
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
                print("Error occured when insering new finding: " + e.__str__())

            # Upload image
            try:
                finding_id = insert_result.data.id

                # get prepared TUS protocol for uplading files
                tus_client = client.get_tus_client_for_finding(workspace_id, finding_id)
                # File size
                file_size = Path(data['img_path']).stat().st_size
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
                # Uploads the entire file.
                # This uploads chunk by chunk.
                uploader.upload()

            except Exception as e:
                print("Error occured when uploading related image to current finding: " + e.__str__())

    def commit_all(self, PATH_TO_JSON, user="Test Script", progresshandler=None, uploaderhandler=None, consolecall=None):
        """
        Commits all files preloaded in given json to database. Commits uploads one by one.
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
        global BREAK

        # Resolve paths for uploads
        PATH = resolve_path(PATH_TO_JSON).resolve()
        PARENT = PATH.parent

        # Load preprocessed data stored in JSON
        with open(PATH, "r") as f:
            file = json.loads(f.read())

        # Get amount of files to process for progression bar vizualization
        ct_max = len(file)+1
        ct = 0

        if progresshandler:
            progresshandler(ct, ct_max=ct_max)

        while not BREAK:
            try:
                payload = file[ct]
                # Resolve path for payload
                if not Path(payload['img_path']).is_absolute():
                    abspath = PARENT / Path(payload['img_path'])
                    payload['img_path'] = abspath.as_posix()
                    payload['user'] = user
                # Upload all elements one by one
                self.commit_one(payload, uploaderhandler)
                # increment loop and progress bar
                ct += 1
                if progresshandler:
                    progresshandler(ct, ct_max=ct_max)

            except IndexError:
                if consolecall:
                    print("All data have been uploaded")
                break
        BREAK = False
        if progresshandler:
            progresshandler(ct, ct_max=ct_max, finished=True)


if __name__ == "__main__":
    connector = Connector()
    with open("../preload_data.json", "r") as f:
        test_j = json.loads(f.read())
    # Commit !st data pack from preloaded json
    one_j = test_j[0]
    one_j['user'] = "Test Script"
    #connector.commit_one(one_j)
    connector.commit_all('../preload_data.json')

#log_func=uploaderhandler if uploaderhandler != None else lambda msg: print(msg)