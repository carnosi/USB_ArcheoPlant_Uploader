# USB ArcheoPlant Uploader
 Image uploader into [UniCatDB](https://app.unicatdb.org/) serviced by the cool folks of [University Southern Bohemia (USB)](https://www.prf.jcu.cz/). By default servers as uploader of seed images to predefined schema without the need of knowledge of any programing language. 

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

![clone repository](https://westeurope1-mediap.svc.ms/transform/thumbnail?provider=spo&inputFormat=png&cs=fFNQTw&docid=https%3A%2F%2Fjucb-my.sharepoint.com%3A443%2F_api%2Fv2.0%2Fdrives%2Fb!loZ3dVEfr0a1PIv1TML942SFrURNkP5HvTUBBtFhRG4Ph5BNmUJNSIWTPmj3QlSf%2Fitems%2F014XMPFJB6PXT72BY5CFA35Y7BOHM4V4NZ%3Fversion%3DPublished&access_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJub25lIn0.eyJhdWQiOiIwMDAwMDAwMy0wMDAwLTBmZjEtY2UwMC0wMDAwMDAwMDAwMDAvanVjYi1teS5zaGFyZXBvaW50LmNvbUBjMzVmNWRhNC05YTAzLTQ0ZTYtOGJmOS05MjgzMzYzNGY2YTciLCJpc3MiOiIwMDAwMDAwMy0wMDAwLTBmZjEtY2UwMC0wMDAwMDAwMDAwMDAiLCJuYmYiOiIxNjUyMjcwNDAwIiwiZXhwIjoiMTY1MjI5MjAwMCIsImVuZHBvaW50dXJsIjoibkhEc3J4T3lTbkdjb2pFb2dGSjVYRkVPTDMyL1RaYlN2a1JoMGxObEFuQT0iLCJlbmRwb2ludHVybExlbmd0aCI6IjExNCIsImlzbG9vcGJhY2siOiJUcnVlIiwidmVyIjoiaGFzaGVkcHJvb2Z0b2tlbiIsInNpdGVpZCI6Ik56VTNOemcyT1RZdE1XWTFNUzAwTm1GbUxXSTFNMk10T0dKbU5UUmpZekptWkdVeiIsInNpZ25pbl9zdGF0ZSI6IltcImttc2lcIl0iLCJuYW1laWQiOiIwIy5mfG1lbWJlcnNoaXB8b2J1ZGlrQGpjdS5jeiIsIm5paSI6Im1pY3Jvc29mdC5zaGFyZXBvaW50IiwiaXN1c2VyIjoidHJ1ZSIsImNhY2hla2V5IjoiMGguZnxtZW1iZXJzaGlwfDEwMDMyMDAxNjdlY2ViN2ZAbGl2ZS5jb20iLCJzaWQiOiJiYTU3NDk2OC0zYWJiLTRkNmQtYTc1Yy0xNmQwYTM0ODAyMTgiLCJ0dCI6IjAiLCJ1c2VQZXJzaXN0ZW50Q29va2llIjoiMyIsImlwYWRkciI6IjE2MC4yMTcuMjQ0LjE5MiJ9.U1Z3Y2YvUENiQkxwRFBOVklGZ1ZzeEN5TW9IVXpDT2ZOdFNrUVhnSVJJbz0&cTag=%22c%3A%7BFDE77D3E-1D07-4111-BEE3-E171D9CAF1B9%7D%2C1%22&encodeFailures=1&width=1515&height=872&srcWidth=&srcHeight=) and then unzip downloaded file to your desired location.

for code users, clone this repo as you usually do with
```bash
git clone https://github.com/carnosi/USB_ArcheoPlant_Uploader
```

## Start up
##### Option 1
To make the use of our uploader easier, there is prepared ``.bat`` file, which starts target jupyter notebook for you. Open unzipped folder cloned from GitHub. If everything is installed as it should, double click the ``start.bat``. Terminal will start and new window in your browser will be opened with Jupyter notebook.
![jupyter GUI](https://westeurope1-mediap.svc.ms/transform/thumbnail?provider=spo&inputFormat=png&cs=fFNQTw&docid=https%3A%2F%2Fjucb-my.sharepoint.com%3A443%2F_api%2Fv2.0%2Fdrives%2Fb!loZ3dVEfr0a1PIv1TML942SFrURNkP5HvTUBBtFhRG4Ph5BNmUJNSIWTPmj3QlSf%2Fitems%2F014XMPFJGQCLJDGDQOZFFYN35MH5UG7XHW%3Fversion%3DPublished&access_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJub25lIn0.eyJhdWQiOiIwMDAwMDAwMy0wMDAwLTBmZjEtY2UwMC0wMDAwMDAwMDAwMDAvanVjYi1teS5zaGFyZXBvaW50LmNvbUBjMzVmNWRhNC05YTAzLTQ0ZTYtOGJmOS05MjgzMzYzNGY2YTciLCJpc3MiOiIwMDAwMDAwMy0wMDAwLTBmZjEtY2UwMC0wMDAwMDAwMDAwMDAiLCJuYmYiOiIxNjUyMjcwNDAwIiwiZXhwIjoiMTY1MjI5MjAwMCIsImVuZHBvaW50dXJsIjoibkhEc3J4T3lTbkdjb2pFb2dGSjVYRkVPTDMyL1RaYlN2a1JoMGxObEFuQT0iLCJlbmRwb2ludHVybExlbmd0aCI6IjExNCIsImlzbG9vcGJhY2siOiJUcnVlIiwidmVyIjoiaGFzaGVkcHJvb2Z0b2tlbiIsInNpdGVpZCI6Ik56VTNOemcyT1RZdE1XWTFNUzAwTm1GbUxXSTFNMk10T0dKbU5UUmpZekptWkdVeiIsInNpZ25pbl9zdGF0ZSI6IltcImttc2lcIl0iLCJuYW1laWQiOiIwIy5mfG1lbWJlcnNoaXB8b2J1ZGlrQGpjdS5jeiIsIm5paSI6Im1pY3Jvc29mdC5zaGFyZXBvaW50IiwiaXN1c2VyIjoidHJ1ZSIsImNhY2hla2V5IjoiMGguZnxtZW1iZXJzaGlwfDEwMDMyMDAxNjdlY2ViN2ZAbGl2ZS5jb20iLCJzaWQiOiJiYTU3NDk2OC0zYWJiLTRkNmQtYTc1Yy0xNmQwYTM0ODAyMTgiLCJ0dCI6IjAiLCJ1c2VQZXJzaXN0ZW50Q29va2llIjoiMyIsImlwYWRkciI6IjE2MC4yMTcuMjQ0LjE5MiJ9.U1Z3Y2YvUENiQkxwRFBOVklGZ1ZzeEN5TW9IVXpDT2ZOdFNrUVhnSVJJbz0&cTag=%22c%3A%7B33D212D0-0E0E-4BC9-86EF-AC3F686FDCF6%7D%2C1%22&encodeFailures=1&width=1515&height=872&srcWidth=&srcHeight=)
If notebook did not start by double-click on ``start.bat``, most likely python is not in your system path. See [BugFixMe](#01) for further help.
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
Request api.token by your local uploader admin. (PRF JCU / Katedra Informatiky)
##### Option 2
Log in to  [UniCatDB](https://app.unicatdb.org/), click on your user name right top corner, select API access. Select custom name and desired expiration duration and click on *Create*. Your personal API key will be shown to you, copy it and save it to text file. Once saved, rename the file to ``api.token`` (file suffixes have to be enabled for this change to work). Copy this ``token`` to the ``source`` folder of cloned repository.

<a id='#01'></a>
## BugFixMe
Common error can be fixed by following steps below.
#### Adding python to system PATH
The complete path of ``python.exe`` can be added by:

1. Right-clicking *This PC* and going to *Properties*.

2. Clicking on the *Advanced system settings* in the menu on the left.

3. Clicking on the *Environment Variables* button o​n the bottom right.

4. In the *System variables* section, selecting the *Path* variable and clicking on *Edit*. The next screen will show all the directories that are currently a part of the PATH variable.

5. Clicking on *New* and entering Python’s install directory.
