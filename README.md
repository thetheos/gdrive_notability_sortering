# gdrive_notability_sortering

DESCRIPTION
---
This is a python script that has for puprose to order in a more logical way the file and folder created by the Notability app in google drive.



Details
---
The source folder is the folder created by Notability wich has a flat folder hierarchy:

```
-Notability
----section_name
-------note/pdf_name
```
The section/source_sub_folder names must follow these naming rules. 

```
upper_name.middle_name.lower_name
```

e.g.: Q2.Analyse.Exercices

PS: The names of the folders created in google drives depends of the names given to the sections in the Notability app

The script rearange the folder hierarchy as shown below
```
-output_folder
----Q2
-------Analyse
----------Exercices
-------------PDF
-------------Note
```
The .pdf and .note files are separated in two sub folders

The script is really not optimized and was first designed only for personnal purpose. 
With more than a 100 files it can take several minutes to achieve.

Be patient :-)

--------

Required packages
---
As described in the google drive api python quickstart

```unix
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

-------

How to use
---
1. Install the required packages
2. modify the run.sh with your folder id or execute the command:
```
python3 gdrive_notab_sortering.py --source_id XXXsource_idXXX --output_id XXXoutput_idXXX
```
3. If the token has not already been created a web page will prompt asking you to authorize the app to access your drive. Authorize it.

------
Credits: Théo Vanden Driessche