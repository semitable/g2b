import dropbox
import os.path

def DropboxConnect(config):
	client = dropbox.client.DropboxClient(config["APP"]["token"])
	return client

def DropboxAuth(config):
    if("token" in config["APP"].keys()):
        access_token = config["APP"]["token"]
    else:
        access_token = None
    if(access_token == None):
		    flow = dropbox.client.DropboxOAuth2FlowNoRedirect(config["APP"]["key"], config["APP"]["secret"])

		    # Have the user sign in and authorize this token
		    authorize_url = flow.start()
		    print ('1. Go to: ' + authorize_url)
		    print ('2. Click "Allow" (you might have to log in first)')
		    print ('3. Copy the authorization code.')
		    code = input("Enter the authorization code here: ").strip()

		    # This will fail if the user enters an invalid authorization code
		    access_token, user_id = flow.finish(code)
    return access_token

def DropboxUpload(client, rfile, path, revision=None):
	f = open(rfile, "rb")
	return client.put_file(path, f, revision)

def DropboxDownload(client, wfile, cloudpath):
	f, metadata = client.get_file_and_metadata(cloudpath)
	out = open(wfile, 'wb')
	out.write(f.read())
	out.close()
	return metadata
