#!/usr/bin/env python3
# Include the Dropbox SDK
import dropbox
import os.path
import time
from db_interface import DropboxConnect, DropboxUpload, DropboxDownload
from tar_interface import make_tarfile, extract
import tarfile
import argparse
import sh
import shutil
import hashlib
import json
# Get your app key and secret from the Dropbox developer website
app_key = 'zmuktk74z6ansu7'
app_secret = '9c7vwi5kgmcbo6i'



#connect to dropbox -- app validation etc
client = DropboxConnect(app_key, app_secret)

currentRevision = None


def pull():
	print("PULL REQUEST")
	metadata = DropboxDownload(client, tarball, cloud_path)
	global currentRevision
	currentRevision = metadata["rev"]
	extract(tarball)

	git = sh.git.bake(_cwd=localrepo_path)
	print(git.pull(tempfolder, "master"))


def push():
    print("PUSH REQUEST")
    pull()
    make_tarfile(tarball, localrepo_path)
    metadata = DropboxUpload(client, tarball, cloud_path, revision=currentRevision)
    print(metadata)
    if(metadata['path'] == cloud_path):
        print("SUCCESS")
    else:
        print("RETRYING")
        time.sleep(10)
        push();
#myrepo = Repo(localrepo_path)

def initialize():
    local_dir=input('Please kind Fucker, give the local repository directory: ')
    while  not (os.path.isdir(local_dir)):
        local_dir=input('Dont fuck with me matey, write again')

    cloud_path=input('Please kind Fucker, give the cloud path')
    cloud_archive_name=input('Please kind Fucker, give the cloud tar.fz name')


    configdata={
            "local":{
                "repo":local_dir,
                "tarball":"temp.tar.gz",
                "temp":"temp",
            },
            "cloud":{
                "path" : cloud_path,
                "tarball" : cloud_archive_name,
            }
        }
    with open('g2b.config', 'w') as jsonout:
        json.dump(configdata, jsonout)
    return configdata

def configure():
    try:
        with open('g2b.config') as jsonin:
            configdata=json.load(jsonin)
    except Exception:
        configdata=initialize()
    finally:
        return configdata

parser = argparse.ArgumentParser()
parser.add_argument("--pull", action="store_true")
parser.add_argument("--push", action="store_true")
args = parser.parse_args()
if(args.pull):
	pull()
if(args.push):
	push()

config = configure()
print (config)
if(os.path.exists("temp")):
    shutil.rmtree('temp')
    os.remove(tarball)
