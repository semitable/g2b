#!/usr/bin/env python3
# Include the Dropbox SDK
import dropbox
import os
import sys
import argparse
import git
import shutil
import time
from random import randint
from db_interface import DropboxAuth, DropboxClient, DropboxDownload, DropboxUpload, DropboxForcedUpload
from tar_interface import extract, make_tarfile
 
appkey  = "zmuktk74z6ansu7"
appsecret = "9c7vwi5kgmcbo6i"

LocalRepo = os.getcwd()
tempDir = LocalRepo + "/temp"
extractionDir = LocalRepo + "/extract"
tempTar = LocalRepo + "/temp.tar.gz"
CloudPath = "/project/mycode.tar.gz"
client = None
Revision = None


def destroyCloud():
    try:
        client.file_delete(CloudPath)
    except dropbox.rest.ErrorResponse as e:
        print("No repository found in dropbox. Could not destroy")


def clean():
    if(os.path.exists(extractionDir)):
        shutil.rmtree(extractionDir)
    if(os.path.exists(tempDir)):
        shutil.rmtree(tempDir)
    if(os.path.exists(tempTar)):
        os.remove(tempTar)



def clone():
    try:
        metadata = DropboxDownload(client, tempTar, CloudPath)
    except dropbox.rest.ErrorResponse as e:
        print("No repository in dropbox")
    extract(tempTar, LocalRepo)



def pull():
    try:
        metadata = DropboxDownload(client, tempTar, CloudPath)
    except dropbox.rest.ErrorResponse as e:
        print("No repository in dropbox")
    else:
        print("Dropbox Repository Found. Pulling..")
        global Revision
        Revision = metadata['rev']
        #pulling from directory "extracted" to the local
        if not os.path.exists(extractionDir):
            os.makedirs(extractionDir)
        extract(tempTar, extractionDir)
        
        try:
            print(git.Git().pull(extractionDir + "/mycode"))
        except:
            print("Auto-merging failed. Please merge the files manually, commit and then push again")

        


def put():
    if not os.path.exists(tempDir):
        os.makedirs(tempDir)

    os.chdir(tempDir)
    git.Git().clone(LocalRepo)
    make_tarfile(tempTar, tempDir+"/mycode")

    DropboxForcedUpload(client, tempTar, CloudPath)

def putgently():
    if not os.path.exists(tempDir):
        os.makedirs(tempDir)

    os.chdir(tempDir)
    git.Git().clone(LocalRepo)
    make_tarfile(tempTar, tempDir+"/mycode")
    metadata = DropboxUpload(client, tempTar, CloudPath, revision=Revision)
    returnpath = metadata['path']
    if(returnpath != CloudPath):
        print("There was a conflict while uploading to Dropbox.")
        print("Possibly another used was pushing at the same time.")
        print("Retrying in a few seconds...")
        client.file_delete(returnpath)
        time.sleep(randint(5,10))
        push()


def push():
    pull()
    putgently()



def connect():
    token = DropboxAuth(appkey, appsecret)
    return DropboxClient(token)



def main(arguments):

    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--push', action='store_true')
    group.add_argument('--pull', action='store_true')
    group.add_argument('--put', action='store_true')
    group.add_argument('--destroy', action='store_true')
    group.add_argument('--clone', action='store_true')
 
    args = parser.parse_args(arguments)
    
    global client
    client = connect()

    clean()
    if(args.push):
        push()
    if(args.pull):
        pull()
    if(args.put):
        put()
    if(args.destroy):
        destroyCloud()
    if(args.clone):
        clone()
    clean()
 
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
