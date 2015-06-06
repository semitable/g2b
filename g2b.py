#!/usr/bin/env python3
# Include the Dropbox SDK
import dropbox
import os
import sys
import argparse
import git
import shutil
from db_interface import DropboxAuth, DropboxClient, DropboxDownload, DropboxUpload
#def extract (file, location):
from tar_interface import extract, make_tarfile
 
appkey  = "zmuktk74z6ansu7"
appsecret = "9c7vwi5kgmcbo6i"

LocalRepo = os.getcwd()
tempDir = LocalRepo + "/temp"
extractionDir = LocalRepo + "/extract"
tempTar = LocalRepo + "/temp.tar.gz"
CloudPath = "/project/mycode.tar.gz"
client = None


def clean():
    shutil.rmtree(extractionDir)
    shutil.rmtree(tempDir)
def pull():
    try:
        metadata = DropboxDownload(client, tempTar, CloudPath)
    except dropbox.rest.ErrorResponse as e:
        print("No repository in dropbox")
        raise e
    else:
        print("Dropbox Repository Found. Pulling..")
        if not os.path.exists(tempDir):
            os.makedirs(tempDir)
        if not os.path.exists(extractionDir):
            os.makedirs(extractionDir)
        extract(tempTar, extractionDir)
        git.Git().pull(extractionDir + "/mycode")
        

        
    
def push():
    os.chdir(tempDir)
    extract(tempTar, extractionDir)
    git.Git().clone(extractionDir+ "/mycode")




def connect():
    token = DropboxAuth(appkey, appsecret)
    return DropboxClient(token)



def main(arguments):

    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--push', action='store_true')
    group.add_argument('--pull', action='store_true')
 
    args = parser.parse_args(arguments)
    
    global client
    client = connect()


    if(args.push == True):
        push()
    if(args.pull == True):
        pull()
    
 
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
