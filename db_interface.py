import dropbox
import os.path

def DropboxClient(token):
    client = dropbox.client.DropboxClient(token)
    return client


def DropboxAuth(app_key, app_secret):
    if(not os.path.isfile("password")):
        flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)
        # Have the user sign in and authorize this token
        authorize_url = flow.start()
        print ('1. Go to: ' + authorize_url)
        print ('2. Click "Allow" (you might have to log in first)')
        print ('3. Copy the authorization code.')
        code = input("Enter the authorization code here: ").strip()

        # This will fail if the user enters an invalid authorization code
        access_token, user_id = flow.finish(code)
        pswdf  = open("password", "w")
        pswdf.write(access_token)
    else:
        pswdf = open("password", "r")
        access_token = pswdf.read()
    return access_token



def DropboxUpload(client, rfile, path, revision=None):
    f = open(rfile, "rb")
    return client.put_file(path, f, revision)
    
def DropboxForcedUpload(client, rfile, path):
    f = open(rfile, "rb")
    return client.put_file(path, f, overwrite=True)

def DropboxDownload(client, wfile, cloudpath):
    f, metadata = client.get_file_and_metadata(cloudpath)
    out = open(wfile, 'wb')
    out.write(f.read())
    out.close()
    return metadata
