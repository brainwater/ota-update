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
    try:
        wifi.radio.connect(secrets["ssid"], secrets["password"])
        needRetry = False
    except Exception as ex:
        print(ex)


def getTree(session, headers):
    response = session.request(
        "GET", secrets['github_code_url'],
        headers=headers)
    print(response)
    try:
        return response.json()['commit']['tree']
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
    return response.json()['content']

try:
    connectWifi()
    pool = socketpool.SocketPool(wifi.radio)
    session = Session(pool, ssl.create_default_context())
    headers = None
    if 'github_token' in secrets:
        headers = {'Authorization': 'Bearer ' + secrets['github_token']}
    tree = getTree(session, headers)
    files = getFiles(session, headers, tree)
    # Mount filesystem as writeable
    remount('/', False)
    paths = []
    for f in files:
        blob = getContents(session, headers, f)
        data = a2b_base64(bytes(blob, 'utf-8'))
        path = "/" + f['path'] + ".new"
        paths.append(path)
        with open(path, 'wb') as fobj:
            fobj.write(data)
        blob = None
        gc.collect()
    
    print("Downloaded new files!")
    for p in paths:
        os.rename(p, p[:-4])
        """with open(p[:-4], 'wb') as target:
            with open(p, 'rb') as src:
                target.write(src.read())"""
    print("Updated files!")

except Exception as ex:
    print(ex)
    raise ex

finally:
    # Always remount filesystem as read-only so we can write to it with the computer
    remount('/', True)
