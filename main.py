#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import httplib2
import os
import json
import mimetypes
import sys

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python Quickstart'
logs=open('logs.conf','w')

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def getFileList():
    results = service.files().list(
        fields="nextPageToken, files(id, name)").execute()
    
    return results.get('files', [])
    
def getFolderID(name, parent_name=None):
    items=getFileList()
    #If it finds folder, sends the id. If couldn't find it, create a new one.
    for item in items:
        if(item['name']==name):
            if(name==root_name):
                return root_id
            else:
                return item['id']
    else:
        if not parent_name:
            return createFolder(name)
        else:
            return createFolder(name,parent_name)
            
def search(name):
    items=getFileList()
    for item in items:
        if(item['name'] == name):
            return False
    else:
        return True
        
def createFolder(folder_name, parent_name=None):
    if search(folder_name):        
        if not parent_name:
            file_metadata = {
                  'name' : folder_name,
                  'mimeType' : 'application/vnd.google-apps.folder'
                }
        else:
            parent_name=os.path.basename(parent_name)
            file_metadata = {
              'name' : folder_name,
              'parents': [ getFolderID(parent_name) ],
              'mimeType' : 'application/vnd.google-apps.folder'
            }
        
        file = service.files().create(body=file_metadata,
                                            fields='id').execute()
        print('+ Folder : '+folder_name+' created')
        logs.write('+ Folder : '+folder_name+', '+getFolderID(folder_name)+' created\n')
    else:
        print('+ Folder : '+folder_name+' already created')
        logs.write('+ Folder : '+folder_name+', '+getFolderID(folder_name)+' adready created\n')
    return getFolderID(folder_name)

def uploadFile(filepath, folder_name):
    filename=os.path.basename(filepath)
    if search(filename):
        file_metadata = {
          'name' : filename,
          'parents': [ getFolderID(folder_name) ]
        }
        media = discovery.MediaFileUpload(filepath,
                                mimetype=mimetypes.guess_type(filename)[0],
                                          chunksize=1024*1024,
                                resumable=True)

        request = service.files().create(body=file_metadata,
                                            media_body=media)
                                            #fields='id')
        print(' - Folder : '+folder_name+'\n\tFile : '+filename)
        logs.write(' - Folder : '+folder_name+'\n\tFile : '+filename+'\n')
        response = None
        try:
            while response is None:
                status,response = request.next_chunk()
                if status:
                    sys.stdout.write("\r\t\tUploading %d%%" % int(status.progress() * 100))
            sys.stdout.write("\r\t\tUploading 100%")
            print("\n\t# Upload Completed")
            logs.write('\t# Upload Completed \n')
        except:
            print("\n\t# Error occured when uploading file.")
            logs.write('\t# Error occured when uploading file.\n')
    else:
        print(' - Folder : '+folder_name+'\n\tFile : '+filename)
        logs.write(' - Folder : '+folder_name+'\n\tFile : '+filename+'\n')
        print("\n\t# Upload Already Completed")
        logs.write('\t# Upload Already Completed\n')

def main():
    """Shows basic usage of the Google Drive API.

    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    global service
    service = discovery.build('drive', 'v3', http=http)
    
    # CODE AREA
    # - Tek başına klasör oluşturmak.
    #       createFolder('KlasörIsmi')
    # - Bir klasöre alt klasör oluşturmak.
    #       createFolder('NodeFolder1','RootFolder')
    # - Klasörün içine dosya upload etmek.
    #       uploadFile('azkaban.bmp','RootFolder')

    root='/var/www/html/The Coding Train'

    def files(dirname):
        parent_name=os.path.basename(dirname)
        for filename in os.listdir(dirname):
            if os.path.isfile(os.path.join(dirname,filename)):
                uploadFile(os.path.join(dirname,filename),parent_name)

    def check(root):
        #Checks if is there any subfolder in the current folder
        for f in os.listdir(root):
            if os.path.isdir(os.path.join(root,f)):
                return True
        else:
            return False
            
    def folders(root):
        if not check(root):
            return
        else:
            for f in os.listdir(root):
                dirpath=os.path.join(root,f)
                if os.path.isdir(dirpath):
                    createFolder(f,os.path.basename(root))
                    folders(dirpath)
                    files(dirpath)

    # CONCEPT
    # - Tek başına klasör oluşturmak.
    #       createFolder('KlasörIsmi')
    # - Bir klasöre alt klasör oluşturmak.
    #       createFolder('NodeFolder1','RootFolder')
    # - Klasörün içine dosya upload etmek.
    #       uploadFile('azkaban.bmp','RootFolder')


    #PROGRAM START
    global root_name
    global root_id
    root_name=os.path.basename(root)
    root_id='0B_1ah-t9B5bGRGYzV2N1d3hFdUE'
    
    folders(root)
    
    
if __name__ == '__main__':
    main()
