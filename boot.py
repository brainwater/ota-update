import time
import ssl
import gc
import os
import socketpool
import wifi
from storage import remount
from adafruit_requests import Session
from adafruit_binascii import a2b_base64

# Add a secrets.py to your filesystem that has a dictionary called secrets with "ssid" and
# "password" keys with your WiFi credentials. DO NOT share that file or commit it into Git or other
# source control.
# pylint: disable=no-name-in-module,wrong-import-order
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

def connectWifi():
    for i in range(5):
        try:
            wifi.radio.connect(secrets["ssid"], secrets["password"])
            break
        except Exception as ex:
            print(ex)
            time.sleep(0.25)


def getData(session, headers):
    response = session.request(
        "GET", secrets['github_code_url'],
        headers=headers)
    try:
        return response.json()
    except:
        print("Error, response not what expected!")
        print(response)
        print(response.json())

def getFiles(session, headers, tree):
    response = session.request(
        "GET", tree['url'] + "?recursive=true",
        headers=headers)
    return response.json()['tree']

def getContents(session, headers, f):
    response = session.request(
        "GET", f['url'],
        headers=headers)
    return response



def isValidData(data):
    for i in ['sha', 'commit']:
        if i not in data:
            print("Key: '" + i + "' not in response, unable to update!")
            print(data)
            return False
    if 'tree' not in data['commit']:
        print("Key: 'tree' not in response.json()['commit'], unable to update!")
        print(data)
        return False
    if 'url' not in data['commit']['tree']:
        print("Key: 'url' not in response.json()['commit']['tree'], unable to update!")
        print(data)
        return False
    return True
        

def isUpToDate(data):
    try:
        with open('.ota-update', 'r') as otaf:
            latestsha = data['sha']
            mysha = otaf.readline().strip()
            return mysha == latestsha
    except:
        print("Unable to find '.ota-update' file, assuming out-of-date code")
        return False

def main():
    try:
        connectWifi()
        pool = socketpool.SocketPool(wifi.radio)
        session = Session(pool, ssl.create_default_context())
        headers = {}
        if 'github_token' in secrets:
            headers = {'Authorization': 'Bearer ' + secrets['github_token']}
        data = getData(session, headers)
        if not isValidData(data):
            print("Invalid data, not updating")
            return
        if isUpToDate(data):
            print("Up to date, not updating code.")
            return
        tree = data['commit']['tree']
        sha = data['sha']
        del data
        files = [f for f in getFiles(session, headers, tree) if f['type'] is not 'tree']
        # Make github return the raw content instead of a base64 encoded json file with the content
        headers['Accept'] = 'application/vnd.github.raw'
        # Mount filesystem as writeable
        remount('/', False)
        paths = []
        for f in files:
            content_response = getContents(session, headers, f)
            path = "/" + f['path'] + ".new"
            paths.append(path)
            with open(path, 'wb') as fobj:
                for chunk in content_response.iter_content(4096):
                    fobj.write(chunk)
            del content_response
            gc.collect()
        
        print("Downloaded new files!")
        for p in paths:
            os.rename(p, p[:-4])
        with open('.ota-update', 'w') as otaf:
            otaf.write(sha + '\n')
        print("Updated files!")

    except Exception as ex:
        print(ex)
        raise ex

    finally:
        # Always remount filesystem as read-only so we can write to it with the computer
        remount('/', True)

main()
