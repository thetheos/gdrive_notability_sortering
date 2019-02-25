"""
Usage: Sort files and folder created by the notability app for auto saving the notes.
The source folder/ backup notability folder names must follow these naming rules. 
(The names of the folders created in google drives depends of the names given to the sections in the Notability app)
upper_name.middle_name.lower_name
eg: Q2.Analyse.Exercices
The folder tree in the output file will look like this:
====================
-output_folder
----Q2
-------Analyse
----------Exercices
-------------PDF
-------------Note
====================
The .pdf and .note files are separated in two sub folder
"""

from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient import errors
import argparse

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

parser = argparse.ArgumentParser()
parser.add_argument("--source_id", help="source_id: the google drive id of the source folder")
parser.add_argument("--output_id", help="output_id: the google drive id of the output folder")
args = parser.parse_args()


def list_file(service):
    """
    List all the files/folders contained in the source folder.
    Return a dictionnary of the relations.
    """

    results = service.files().list(q="'{}' in parents".format(source_folder_id), pageSize=1000, fields="nextPageToken, files(id, name)" ).execute()   #list file in source folder
    items = results.get('files', [])


    if not items:
        print('No files found.')
    else:
        print('Files:')
        quadri_dico = {}
        try:
            for item in items:
                if item['name'].split(".")[0] not in quadri_dico:
                    quadri_dico[item['name'].split(".")[0]] = {}
                if item['name'].split(".")[1] not in quadri_dico[item['name'].split(".")[0]]:
                    quadri_dico[item['name'].split(".")[0]][item['name'].split(".")[1]] = []
                quadri_dico[item['name'].split(".")[0]][item['name'].split(".")[1]].append((item['name'].split(".")[2], item['id']))
                #print(u'{0} ({1})'.format(item['name'], item['id']))
        except:
            pass
        for elm in quadri_dico:
            print("Quadri : " + elm)
            for i in quadri_dico[elm]:
                print(" \t cours: " + i)
                for ifile in quadri_dico[elm][i]:
                    print("\t \t fichiers: " + str(ifile))

        return(quadri_dico)
    

def create_files(service,dico):
    """
    Create the folder and copy the files in the output directory following a dictionnary.
    """
    try:
        """
        elm = quadri
        i= cours
        e =  tuple(nom_repertoire, id)
        """
        for elm in dico:
            file = is_already_created(service, elm, output_folder_id) 
            
            if file == False:
                file_metadata = {'name': elm, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [output_folder_id]}
                file = service.files().create(body=file_metadata, fields='id').execute()
             
            for i in dico[elm]:
                print("cours: {} ,parents id: {}".format(i,file.get('id')))
                i_file = is_already_created(service, i, file.get('id')) 
                if i_file == False:
                    file_metadata = {'name': i, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [file.get('id')]}
                    i_file = service.files().create(body=file_metadata, fields='id').execute()
                
                for e in dico[elm][i]:
                    print("sous-cours: {} ,parents id: {}".format(e[0],i_file.get('id')))
                    e_file = is_already_created(service, e[0], i_file.get('id'))
                    #print("i_file obj " + str(i_file))
                    #print("e_file " + str(e_file))
                    if e_file == False:
                        file_metadata = {'name': e, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [i_file.get('id')]}
                        e_file = service.files().create(body=file_metadata, fields='id').execute()
                    try:
                        file_metadata = {'name': "PDF", 'mimeType': 'application/vnd.google-apps.folder', 'parents': [e_file.get('id')]}
                        pdf_file = service.files().create(body=file_metadata, fields='id').execute()
                        file_list = list_files(service, e[1], "application/pdf")
                        for file_in in file_list:
                            copy_file(service, file_in['id'], file_in['name'],pdf_file.get('id'))
                            #print(dico[elm][i][1][1])

                        file_metadata = {'name': "Note", 'mimeType': 'application/vnd.google-apps.folder', 'parents': [e_file.get('id')]}
                        note_file = service.files().create(body=file_metadata, fields='id').execute()
                        file_list = list_files_notes(service, e[1], "application/pdf")
                        for file_in in file_list:
                            copy_file(service, file_in['id'], file_in['name'], note_file.get('id'))
                            
                    except:
                        pass
                    #copy_file(service, e_file.get('id'), e_file.get('name'),)
    except:
        pass                
        #print('Folder ID: %s' % file.get('id'))
    pass


def is_already_created(service, folder_name, parent_id):
    """
    Check if the folder name is already created in a parent folder.
    """
    #print("folder name: {}".format(folder_name))
    results = service.files().list(q="'{}' in parents".format(parent_id), pageSize=1000, fields="nextPageToken, files(id, name, trashed)" ).execute()
    items = results.get('files', [])
    print("folder name: {}".format(folder_name))
    print("Items for {} \n {}".format(folder_name,items))
    for elm in items:
        #print(elm)
        if folder_name == elm['name'] and elm['trashed']!= True:
            print("File already created {}".format(folder_name))
            return elm
    return False


def list_files(service, folder_id, file_type):
    """
    Return all the file with a specific mime type contained in a folder
    """
    #print("ok" + str(folder_id))
    results = service.files().list(q="'{}' in parents and mimeType = '{}'".format(folder_id, file_type),  pageSize=1000, fields="nextPageToken, files(id, name)" ).execute()
    #results.Q = "'12WlA0eBFGuemY9XQsWToYJFLQDLCuDLW' in parents"
    items = results.get('files', [])
    #print(file_type + " " + str(items))
    return items

def list_files_notes(service, folder_id, file_type):
    """
    Return all the file that don't have the specified mime type
    """
    #print("ok" + str(folder_id))
    results = service.files().list(q="'{}' in parents and mimeType != '{}'".format(folder_id, file_type),  pageSize=1000, fields="nextPageToken, files(id, name)" ).execute()
    #results.Q = "'12WlA0eBFGuemY9XQsWToYJFLQDLCuDLW' in parents"
    items = results.get('files', [])
    #print(file_type + " not " + str(items))
    return items

def initiate_service():
    """
    Initiate the drive token
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    return service



def copy_file(service, origin_file_id, copy_title, destination):
    """
    Copy an existing file.

    Args:
        service: Drive API service instance.
        origin_file_id: ID of the origin file to copy.
        copy_title: Title of the copy.

    Returns:
        The copied file if successful, None otherwise.
    """
    copied_file = {'title': copy_title, 'parents': [destination]}
    try:
        return service.files().copy(fileId=origin_file_id, body=copied_file).execute()
    except errors.HttpError as error:
        print('An error occurred: %s' % error)
    return None


if __name__ == '__main__':
    if args.source_id and args.output_id:
        source_folder_id = args.source_id
        output_folder_id = args.output_id
        service = initiate_service()
        dico = list_file(service)
        create_files(service, dico)
        
    else:
        print("No source and folder id precised")
    





