# -*- coding: utf-8 -*-
"""
uploadergui.py: Jupyter GUI constructor and handler for image uploader scripts.
Creates GUI in jupyter notebook and eases the use of any scripts for without
the need of programming knowledge.

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
__version__ = "1.0.9"
__maintainer__ = ["Ondrej Budik", "Vojtech Barnat"]
__email__ = ["obudik@prf.jcu.cz", "Vojtech.Barnat@fs.cvut.cz"]
__status__ = "Beta"

__python__ = "3.8.0"

# Import required libs
try:
    import threading
    import numpy as np
    from ipywidgets import Button, Dropdown, Text, HBox, VBox, HTML, FloatProgress, Layout
    from IPython.display import display, clear_output
    from ipyfilechooser import FileChooser

    # Import custom scripts
    import dataprocess as dp
    import uploader as up
    import all_in_one as aio

    # Import setting from config
    from config import MIN_USERNAME_LENGTH

except ModuleNotFoundError:
    # If there are missing libraries, install those.
    print("There are some libraries missing... Installing...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "opencv-python"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "scipy"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "xmltodict"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ipywidgets"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ipyfilechooser"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "unicatdb==2.2b1"])
    print("Instalation finished.")

    import threading
    import numpy as np
    from ipywidgets import Button, Dropdown, Text, HBox, VBox, HTML, FloatProgress, Layout
    from IPython.display import display, clear_output
    from ipyfilechooser import FileChooser

    # Import custom scripts
    import dataprocess as dp
    import uploader as up
    import all_in_one as aio

    # Import setting from config
    from config import MIN_USERNAME_LENGTH

class GUI():
    """
    Jupyter GUI constructor and executor. Constructs uploader GUI for UniCatDB.
    Uses ipywidgets with which even non-coders will be able to upload their
    folders of images in the database.
    """
    def __init__(self):
        """
        Jupyter GUI constructor and executor. Constructs uploader GUI for UniCatDB.
        Uses ipywidgets with which even non-coders will be able to upload their
        folders of images in the database.
        """
        # Ipywidgets
        self.top_html = None
        self.user = None
        self.finder = None
        self.path = None
        self.origin = None
        self.mode = None
        self.butt = None
        self.prog = None
        self.uplo = None
        self.bothtml = None
        self.bot_html = None
        # File chooser
        self.fc = None
        # Create gui
        self.construct_gui()
        self.link_gui()
        self.running = False
        # Class holders for progress bars
        self.pb_ar = np.zeros((0,))
        self.pb_up = np.zeros((0,))
        self.PATH = ""
        self.thread = None

    def construct_gui(self):
        """
        Constructs GUI elements with jupyter notebook widgets and displays them in defined layout

        Returns
        -------
        None.

        """
        # Htlm GUI top
        tophtml = "Welcome to jupyter notebook seed image uploader!"
        self.top_html = HTML(value=tophtml)

        # Username
        self.user = Text(value="", placeholder="User name", description="User name", disabled=False, layout=Layout(width="35%"))

        # Path finder
        self.finder = Button(description="Path:", buttonstyle="", tooltip="Select path with path finder", icon="folder", layout=Layout(width="15%"))

        # Path field
        self.path = Text(value="", placeholder="Path to file or folder", description="", disabled=False, layout=Layout(width="65%"))

        # Empty space
        emptiness = HTML(value=" ")

        # Microscope origin dropdown
        self.origin = Dropdown(options=["Zeis", "Keyence"], value="Zeis", description="Microscope:", disabled=False, layout=Layout(width="50%"))

        # Select if uploader or preloader
        self.mode = Dropdown(options=["Uploader", "Pre Loader", "All-in-One"], value="Pre Loader", description="Mode:", disabled=False, layout=Layout(width="50%"))

        # Starting button
        self.butt = Button(description="Start", buttonstyle='', tooltip="Start task in given mode", icon='check', disabled=True, layout=Layout(width="30%"))

        # Progression bar
        self.prog = FloatProgress(value=0, min=0, max=10, description="Total: ", barstyle="info", style={"bar_color": "#180cb3"}, orientation="horizontal", layout=Layout(width="95%"))

        # Upload bar - shown only when in uploader or AiO mode
        self.uplo = FloatProgress(value=0, min=0, max=10, description="Upload: ", barstyle="info", style={"bar_color":'#32A718'}, orientation="horizontal", layout=Layout(width="95%", visibility="hidden"))

        # Html GUI bottom
        self.bothtml = f"<br>GUI version: {__version__} | Data processing version: {dp.__version__} | Image processing version: {dp.ip.__version__} <br> Uploader version: {up.__version__} | All-in-One version: {aio.__version__} | UniCatDB version: {up.unicatdb.openapi_client.__version__}"
        self.bot_html = HTML(value=self.bothtml)

        #Layout setting
        top = HBox([self.user, emptiness, self.finder, emptiness, self.path])
        middle = HBox([self.origin, self.mode])
        bars = VBox([self.prog, self.uplo], layout=Layout(width='90%', overflow='hidden'))
        bottom = HBox([self.butt, bars])
        self.layout = VBox([self.top_html, top, middle, bottom, self.bot_html],  layout=Layout(width='80%', border='solid'))
        # Showlayout
        display(self.layout)

    def __on_button_click__(self, ide):
        """
        Event handler for on button click. On click starts or stops image and meta data processing
        tasks. Processing is executed in separete thread, do not kill main app unexpectedly.

        Parameters
        ----------
        ide : list
            Description of caller. Not used as there is only one button,
            yet required by ipywidgets.

        Returns
        -------
        None.

        """

        if self.running:
            # Lock button during safe exit
            self.butt.disabled = True
            # Change global for another thread to stop
            dp.BREAK = True
            up.BREAK = True
            # Let user know something is going on
            self.bot_html.value = "<b style='color:orange;'>Stopping...</b>" + self.bothtml
            # Prepare class for another start
            self.pb_ar = np.zeros((0,))
            # Wait for thread to finish and exit safely
            self.thread.join()
            # Change running state
            self.running = False
            # Change button and update text
            self.bot_html.value = "<b style='color:red;'>Processing stopped</b>" + self.bothtml
            self.butt.description = 'Start'
            self.butt.icon = 'check'
            self.butt.tooltip = "Start task in given mode"
            # Unlock UI
            self.butt.disabled = False
            self.mode.disabled = False
            self.user.disabled = False
            self.path.disabled = False
            self.finder.disabled = False
            self.origin.disabled = False

        else:
            # Extract settings from GUI
            self.PATH = self.path.value
            origin = self.origin.value
            mode = self.mode.value
            # Change state to running
            self.running = True
            # Change button and update text
            self.bot_html.value = "<b style='color:green;'>Processing started</b>" + self.bothtml
            self.butt.description = "Stop"
            self.butt.icon = 'fa-times'
            self.butt.tooltip = "Stop running task"
            # Disable interactive widgets so they can not be changed during job
            self.mode.disabled = True
            self.user.disabled = True
            self.path.disabled = True
            self.finder.disabled = True
            self.origin.disabled = True
            # Start propper processing depending on mode in seperate thread (for GUI reasons)
            try:
                # Start in UPLOADER mode
                if mode == "Uploader":
                    # Check if target path leads to json (file chooser should allow only propper )
                    if not self.PATH.lower().endswith((".txt",".json")):
                        self.bot_html.value("<b style='color:green;'> Expected path has to lead to json. Change path and try again.</b>" + self.bothtml)
                    else:
                        self.bot_html.value = "<b style='color:green;'>Processing started</b>" + self.bothtml
                    self.thread = threading.Thread(target=up.Connector().commit_all, args=(self.PATH,),
                                                   kwargs={'progresshandler':self.__progressbar__,
                                                           'uploaderhandler':self.__uploadbar__,
                                                           'user':self.user.value})
                    self.thread.start()
                # Start in PRE LOADER mode
                elif mode == "Pre Loader":
                    self.thread = threading.Thread(target=dp.preload_data, args=(self.PATH, origin,),
                                                   kwargs={'progresshandler':self.__progressbar__,
                                                           'relative':True,
                                                           'save':True})
                    self.thread.start()
                # Start in All-in-One mode
                elif mode == "All-in-One":
                    self.thread = threading.Thread(target=aio.all_in_one, args=(self.PATH, origin,),
                                                   kwargs={'progresshandler':self.__progressbar__,
                                                           'uploaderhandler':self.__uploadbar__,
                                                           'user':self.user.value})
                    self.thread.start()
                else:
                    raise NotImplementedError("Desired mode is not implemented.")
            except Exception as e:
                self.bot_html.value = "<b style='color:red;'>Exception - "+str(e.__class__.__name__)+"</b>: "+ str(e) + self.bothtml
                self.__reseter__(exception=True)

    def __progressbar__(self, ct, ct_max=None, finished=False):
        """
        Progressbar update callback from processing scripts. If not finished ct updates index of
        prepared steps. If finished, move progress to last position and let user know that all
        is done.

        Parameters
        ----------
        ct : int
            Integer value used as index to iterate over prepared progression bar steps.
            Ct increases after each image which get successfuly processed.
        finished : Bool, optional
            Trigger for last tread task update. The default is False.

        Returns
        -------
        None.

        """
        if not finished:
            # Dynamically determine steps for progress bar (Uploader, Preloader work slightly different).
            if self.pb_ar.shape[0] < 1:
                if ct_max == None:
                    nr = dp.get_amount_of_files(self.PATH)+1
                else:
                    nr = ct_max
                self.pb_ar = np.linspace(self.prog.min, self.prog.max, nr)
                self.prog.value = self.pb_ar[ct]
            else:
                # Check if processing has been compromised and interrupt current job
                if self.pb_ar.shape[0] < ct:
                    print("Files have been modified since start! Corruption might occure. Stopping...")
                    dp.BREAK = True
                    self.prog.value = self.prog.max
                else:
                    # Move progress bar
                    self.prog.value = self.pb_ar[ct]
        # On completed job reset attributes and let user know everything is done.
        elif finished and self.running:
            self.prog.value = self.prog.max
            self.bot_html.value = "<b style='color:blue;'>Processing FINISHED</b>" + self.bothtml
            self.pb_ar = np.zeros((0,))
            self.mode.disabled = False
            self.user.disabled = False
            self.path.disabled = False
            self.finder.disabled = False
            self.origin.disabled = False
            self.running = False
            self.butt.description = 'Start'
            self.butt.icon = 'check'
            self.butt.tooltip = "Start task in given mode"
        else:
            self.prog.value = self.prog.min

    def __uploadbar__(self, msg, bitmax, chunk, nr_chunks):
        """
        Uploadbar update callback from uploader scripts. If not finished, ct updates index of
        prepared steps. If finished, move progress to last position. Global notification is
        done by progress bar, as this uploader vizualizes every single image and text could be
        extensive.

        Parameters
        ----------
        ct : int
            Integer value used as index to iterate over prepared progression bar steps.
            Ct increases after each image which get successfuly processed.
        bitmax: int
            Size of image to be uploaded for progression array preparation. Each image gets its own
        finished : Bool, optional
            Trigger for last tread task update. The default is False.

        Returns
        -------
        None.

        """
        # Process text callback by upload script. If it changes in new UniCatDB - UPDATE THIS #TODO
        step = msg.split(" ")[0]
        # Last callback recapts upload, we dont need that for progress bar
        if step != "maximum":
            # Calculate step based on chunk size and current upload
            ct = -(-int(step) // chunk)
            # Create progress bar steps dynamically for each file
            if self.pb_up.shape[0] < 1:
                self.pb_up = np.linspace(self.uplo.min, self.uplo.max, nr_chunks)
                self.uplo.value = self.pb_up[0]
            # Check if data is not corrupted
            if self.pb_up.shape[0] < ct:
                print("Upload has been compromised. Please restarat current file")
                self.uplo.value = self.uplo.min
                up.BREAK = True
            else:
                # Move progress bar
                self.uplo.value = self.pb_up[ct-1]
        # Use last callback as end marker and reset attributes for next progress
        elif step == "maximum" and self.running:
            self.uplo.value = self.uplo.max
            self.pb_up = np.zeros((0,))
        else:
            raise IOError("Callback of upload has been changed! Update __uploadbar__")

    def __reseter__(self, exception=False):
        """
        Resets UI elements and some class attributes for clean start of next
        job.

        Returns
        -------
        None.

        """
        self.prog.value = self.prog.min
        self.uplo.value = self.uplo.min
        self.pb_ar = np.zeros((0,))
        self.pb_up = np.zeros((0,))
        self.running = False
        self.mode.disabled = False
        self.user.disabled = False
        self.path.disabled = False
        self.finder.disabled = False
        self.origin.disabled = False
        self.butt.description = 'Start'
        self.butt.icon = 'check'
        self.butt.tooltip = "Start task in given mode"
        if not exception:
            self.bot_html.value = self.bothtml

    def __on_path_button__(self, ide):
        """
        Opens file dialog and returns path to class attribute. Uses 3rd party library ipyfilechooser.
        If there should be some problems in near future, this one will have to
        be coded from 0 in a custom manner.

        Parameters
        ----------
        ide : int
            ID identification of event callback. (Required by parent)

        Returns
        -------
        None.
        """
        if self.fc == None:
            # Init Layout of file chooser
            self.fc = FileChooser(dp.rcwd)
            # Set up file chooser for selected more
            if self.mode.value == "Uploader":
                self.fc.title = '<b>Select preprocessed json file</b>'
                self.fc.filter_pattern = ['*.txt', '*.TXT', '*.json', '*.JSON']
            else:
                self.fc.title = '<b>Select folder with images</b>'
                self.fc.show_only_dirs = True
            # Register call back for path str read out
            self.fc.register_callback(self.__path_callback__)
            # Show file chooser
            display(self.fc)
        else:
            # Close file chooser and clear display
            self.fc.close()
            self.fc = None
            clear_output()
            display(self.layout)

    def __path_callback__(self, change):
        """
        Path callback register upon selecting path with ipyfilechooser.
        Saves path to class variable

        Parameters
        ----------
        change : str
            Change which occured in drop down menu (Required by callback func)

        Returns
        -------
        None.

        """
        self.path.value = self.fc.selected

    def __user_entry_start__(self, change):
        """
        Upon begining of entering user name, enables start button. Locks if left empty

        Parameters
        ----------
        change : str
            Change which occured in drop down menu (Required by callback func)

        Returns
        -------
        None.

        """
        # Disable button if text field has less than defined user name length
        # default = 3 characters
        if len(self.user.value) < MIN_USERNAME_LENGTH or len(self.path.value) == 0:
            self.butt.disabled = True
        else:
            self.butt.disabled = False

    def __mode_observer__(self, change):
        """
        Changes UI elemets based on selected mode.

        Parameters
        ----------
        change : str
            Change which occured in drop down menu (Required by callback func)

        Returns
        -------
        None.

        """
        if self.mode.value == "Pre Loader":
            # Hide upload progress bar
            self.path.value = ""
            self.uplo.layout.visibility = "hidden"
            # Reset file chooser
            if self.fc:
                self.fc.close()
                self.fc = None
                clear_output()
                display(self.layout)
        elif self.mode.value in ["Uploader", "All-in-One"]:
            # Show upload progress bar
            self.path.value = ""
            self.uplo.layout.visibility = "visible"
            # Reset file chooser
            if self.fc:
                self.fc.close()
                self.fc = None
                clear_output()
                display(self.layout)
        # Reset class instance state
        self.__reseter__()

    def link_gui(self):
        """
        Links GUI elements with their associated callback functions.

        Returns
        -------
        None.
        """
        self.butt.on_click(self.__on_button_click__)
        self.finder.on_click(self.__on_path_button__)
        self.user.observe(self.__user_entry_start__, names='value')
        self.path.observe(self.__user_entry_start__, names='value')
        self.mode.observe(self.__mode_observer__, names="value")

if __name__ == "__main__":
    # Starts GUI in jupyter notebook
    GUI()