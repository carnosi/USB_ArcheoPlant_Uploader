# USB ArcheoPlant Uploader
 Image uploader into [UniCatDB](https://app.unicatdb.org/) serviced by the cool folks of [University Southern Bohemia (USB)](https://www.prf.jcu.cz/). By default serves as uploader of seed images to predefined schema without the need of knowledge of any programing language. 

 ## Installation
 After finishing thse steps, you'll be all set to upload all images you collect all by yourself!

## Step 1 - Install Jupyter Lab
If you already have Python installed, run following command in terminal
```bash
pip install jupyterlab
```
Else download python in Anaconda distribution from [here](https://www.anaconda.com/products/distribution). This distribution already has Jupyter Lab preinstalled. During installation make sure that you **ADD PATH** to your system enviroment.

## Step 2 - Clone repository
If you dont feel like using command line for cloning, you can go to top of this repository, click on button that says *Code* and then click on download ZIP. As seen on enclosed image below 

![clone repository](https://lh3.googleusercontent.com/AlxLqiGeSy6QOddA-Q4pn04Sd0CJ6wD7ss-XaRH-8s2_ey-2soYkjxIgZK8fPPW0vZQj4SGic2qGDu_F4SlUVyxE20fvLfYdOGzfYme_l0dAv7wpfxW0RC1zR1X6Nh5ysYxxC8QiBQ=w2400) and then unzip downloaded file to your desired location.

for code users, clone this repo as you usually do with
```bash
git clone https://github.com/carnosi/USB_ArcheoPlant_Uploader
```

## Start up
##### Option 1
To make the use of our uploader easier, there is prepared ``.bat`` file, which starts target jupyter notebook for you. Open unzipped folder cloned from GitHub. If everything is installed as it should, double click the ``start.bat``. Terminal will start and new window in your browser will be opened with Jupyter notebook.
![jupyter GUI](https://lh3.googleusercontent.com/keszy6G-_T1V2LUjcKlIu32_2Gst-3EzYhNtzhBDW_guD5DLWj4lsYNMIDFmdiYcerre6JqJeN27hWYQtCE2sr4pZjfFABLYSquaRbcGbrz-5EPXmZkFEKlBKZpGB9hUeP132DxLrw=w2400)
If notebook did not start by double-click on ``start.bat``, most likely python is not in your system path. See [BugFixMe](#bugfixme) for further help.
##### Option 2
Open terminal, change directory to cloned repository, go to source, start ``IMGuploader.ipynb`` with following commands
```bash
cd <path/to/cloned/unzipped/repository>
cd source
jupyter notebook IMGuploader.ipynb
```
###### Documentation about uploader's functionality is within same notebook as the GUI itself, for further documentation of our uploader, read through the points in that notebook.

## Obtaining API key
API key servers as personal identificator through aplication program interface and replaces the log in which is performed by user. Since this key allows programs to do basically anything they want in associated database, it is recommended to not share it with any other user or damage caused by their API key might be associated with them instead of the evil-doer. 
##### Option 1
Request ``api.token`` by your local uploader admin. (PRF JCU / Katedra Informatiky)
##### Option 2
Log in to  [UniCatDB](https://app.unicatdb.org/), click on your user name right top corner, select API access. Select custom name and desired expiration duration and click on *Create*. Your personal API key will be shown to you, copy it and save it to text file. Once saved, rename the file to ``api.token`` (file suffixes have to be enabled for this change to work). Copy this ``token`` to the ``source`` folder of cloned repository.
## BugFixMe
Common error can be fixed by following steps below.
#### Adding python to system PATH
The complete path of ``python.exe`` can be added by:

1. Right-clicking *This PC* and going to *Properties*.

2. Clicking on the *Advanced system settings* in the menu on the left.

3. Clicking on the *Environment Variables* button o​n the bottom right.

4. In the *System variables* section, selecting the *Path* variable and clicking on *Edit*. The next screen will show all the directories that are currently a part of the PATH variable.

5. Clicking on *New* and entering Python’s install directory.
