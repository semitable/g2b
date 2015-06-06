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
import json


appkey  = "zmuktk74z6ansu7"
appsecret = "9c7vwi5kgmcbo6i"

#LocalRepo = os.getcwd()
#tempDir = LocalRepo + "/temp"
#extractionDir = LocalRepo + "/extract"
#tempTar = LocalRepo + "/temp.tar.gz"
#CloudPath = "/project/mycode.tar.gz"

client = None

config = None

Revision = None

def destroyCloud():
    CloudPath = config['cloud']['archive']
    try:
        client.file_delete(CloudPath)
    except dropbox.rest.ErrorResponse as e:
        print("No repository found in dropbox. Could not destroy")


def clean():
    if(os.path.exists(config['temp']['extract'])):
        shutil.rmtree(config['temp']['extract'])
    if(os.path.exists(config['temp']['folder'])):
        shutil.rmtree(config['temp']['folder'])
    if(os.path.exists(config['temp']['tarball'])):
        os.remove(config['temp']['tarball'])



def clone():
    CloudPath = input("Please enter the archive path in dropbox: ")
    tempTar = "temp.tar.gz"
    try:
        metadata = DropboxDownload(client, tempTar, CloudPath)
    except dropbox.rest.ErrorResponse as e:
        print("No repository in dropbox")
    extract(tempTar, config['local']['path'])
    os.remove(tempTar)



def pull():
    CloudPath = config['cloud']['archive']
    tempTar = config['temp']['tarball']
    extractionDir = config['temp']['extract']
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
    CloudPath =config['cloud']['archive']
    tempTar = config['temp']['tarball']
    tempDir = config['temp']['folder']
    if not os.path.exists(tempDir):
        os.makedirs(tempDir)

    os.chdir(tempDir)
    git.Git().clone(config['local']['path'])
    make_tarfile(tempTar, tempDir+"/mycode")

    DropboxForcedUpload(client, tempTar, CloudPath)

def putgently():
    CloudPath = config['cloud']['archive']
    tempTar = config['temp']['tarball']
    tempDir = config['temp']['folder']

    if not os.path.exists(tempDir):
        os.makedirs(tempDir)

    os.chdir(tempDir)
    git.Git().clone(config['local']['path'])
    make_tarfile(tempTar, tempDir+"/mycode")
    metadata = DropboxUpload(client, tempTar, CloudPath, revision=Revision)
    returnpath = metadata['path']
    if(returnpath != CloudPath):
        print("There was a conflict while uploading to Dropbox.")
        print("Possibly another user was pushing at the same time.")
        print("Retrying in a few seconds...")
        client.file_delete(returnpath)
        clean()
        time.sleep(randint(5,10))
        push()


def push():
    pull()
    putgently()



def connect(token=None):
    if (token==None):
        token = config['APP']['token']
    return DropboxClient(token)


def readconfig():
    if(not os.path.exists('g2b.config')):
        return None
    with open('g2b.config') as jsonin:
        config = json.load(jsonin)
    return config

def configure(write=True):
    config = readconfig()

    if (config == None):
        config = {}

    config['APP'] = {}
    config['local'] = {}
    config['temp'] = {}
    config['cloud'] = {}

    config['APP']['key'] = "zmuktk74z6ansu7"
    config['APP']['secret'] = "9c7vwi5kgmcbo6i"
    #if('token' in config['APP'].keys()):
    config['APP']['token'] = DropboxAuth(config['APP']['key'], config['APP']['secret'])

    config['local']['path'] = os.getcwd()
    config['local']['basename'] = os.path.split(os.getcwd())[1]
    

    config['temp']['extract'] = config['local']['path'] + "/extract"
    config['temp']['folder'] = config['local']['path'] + "/temp"
    config['temp']['tarball'] = config['temp']['folder'] + "/temp.tar.gz"

    config['cloud']['path'] = "/project"
    config['cloud']['archive'] = os.path.join(config['cloud']['path'], config['local']['basename']) + ".tar.gz"

    if(write==True):
        with open('g2b.config', 'w') as jsonout:
            json.dump(config, jsonout)
    return config


def main(arguments):
    global config
    global client
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--push', action='store_true')
    group.add_argument('--pull', action='store_true')
    group.add_argument('--put', action='store_true')
    group.add_argument('--destroy', action='store_true')
    group.add_argument('--clone', action='store_true')
    group.add_argument('--configure', action='store_true')
 
    args = parser.parse_args(arguments)
    #Configuration not required arguments:
    if(args.configure):
        configure()
        return
    if(args.clone):
        config = configure(write=False)
        client = connect()
        clone()
        return

    #Reading the configuration file

    config = readconfig()
    if (config == None):
        print("No configuration file found. Please run --configure first for each directory")
        print("Exiting...")
        return


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

    if(args.configure):
        configure()
    clean()
 
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
