#!/usr/bin/env python3
# Include the Dropbox SDK
import dropbox
import os.path
import time
from git import Repo
from db_interface import DropboxConnect, DropboxUpload, DropboxDownload
from tar_interface import make_tarfile, extract
import tarfile
import argparse
import sh
import shutil
import hashlib
# Get your app key and secret from the Dropbox developer website
app_key = 'zmuktk74z6ansu7'
app_secret = '9c7vwi5kgmcbo6i'



#connect to dropbox -- app validation etc
client = DropboxConnect(app_key, app_secret)


#Out folders:
cloud_path = "/project/archive.tar.gz"
localrepo_path = os.path.abspath("mycode")
tarball = "tarcode.tar.gz"
tempfolder = os.path.abspath("temp/mycode")
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


parser = argparse.ArgumentParser()
parser.add_argument("--pull", action="store_true")
parser.add_argument("--push", action="store_true")
args = parser.parse_args()
if(args.pull):
	pull()
if(args.push):
	push()
shutil.rmtree('temp')
os.remove(tarball)


