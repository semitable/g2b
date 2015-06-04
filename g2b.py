#!/usr/bin/env python3
# Include the Dropbox SDK
import dropbox
import os.path
import time
from db_interface import DropboxConnect, DropboxUpload, DropboxDownload, DropboxAuth
from tar_interface import make_tarfile, extract
import tarfile
import argparse
import sh
import shutil
import hashlib
import json
# Get your app key and secret from the Dropbox developer website

#connect to dropbox -- app validation etc


currentRevision = None

def pull(config):
	print("PULL REQUEST")
	metadata = DropboxDownload(client, config["local"]["tarball"], os.path.join(config["cloud"]["path"],config["cloud"]["tarball"]),)
	global currentRevision
	currentRevision = metadata["rev"]
	extract(config["local"]["tarball"])

	git = sh.git.bake(_cwd=config["local"]["path"])
	print(git.pull(os.path.join(config["local"]["temp"],"mycode"), "master"))


def push(config):
    print("PUSH REQUEST")
    pull(config)
    make_tarfile(config["local"]["tarball"], config["local"]["path"])
    metadata = DropboxUpload(client, config["local"]["tarball"], os.path.join(config["cloud"]["path"],config["cloud"]["tarball"]), revision=currentRevision)
    print(metadata)
    if(metadata['path'] == os.path.join(config["cloud"]["path"],config["cloud"]["tarball"])):
        print("SUCCESS")
    else:
        print("RETRYING")
        time.sleep(10)
        push(config);
#myrepo = Repo(localrepo_path)

def initialize():
    local_dir=os.getcwd()
    cloud_path=input('Please enter the dropbox path to use: ')
    cloud_archive_name= os.path.split(os.getcwd())[1] + ".tar.gz"
    configdata={
            "APP":{
                "key":"zmuktk74z6ansu7",
                "secret":"9c7vwi5kgmcbo6i"
            }
    }
    mytoken = DropboxAuth(configdata)
    configdata={
            "APP":{
                "token": mytoken,
                "key":"zmuktk74z6ansu7",
                "secret":"9c7vwi5kgmcbo6i"
            },
            "local":{
                "path":local_dir,
                "tarball": cloud_archive_name,
                "temp":"temp"
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

config = configure()
client = DropboxConnect(config)
print(config)

if(args.pull):
	pull(config)
if(args.push):
	push(config)


if(os.path.exists(config["local"]["temp"])):
    shutil.rmtree(config["local"]["temp"])
    os.remove(config["local"]["tarball"])
