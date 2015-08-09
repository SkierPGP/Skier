from app import gpg

import requests

from cfg import API_VERSION, SKIER_VERSION

def add_key(armored: str):
    gpg.import_keys(armored)

def import_key(keyserver: str, keyid: str):
    # Check to see if the server is a skier server.
    is_skier = False
    try:
        if 'http://' not in keyserver and "https://" not in keyserver:
            keyserver = "http://" + keyserver
        r = requests.post(keyserver + "/skier", data=[API_VERSION,SKIER_VERSION])
        if r.status_code == 200:
            js = r.json()
            # Check the API version to make sure we're compatible.
            if js['api_version'] == API_VERSION:
                is_skier = True
    except:
        pass
    # Lookup the key.
    data = None
    if not is_skier:
        name = keyserver + "/pks/lookup"
        params = {"op": "get", "search": keyid, "options": "mr"}
        try:
            r = requests.get(name, params=params)
        except requests.exceptions.ConnectionError:
            return -2
        else:
            if r.status_code == 200:
                data = r.text
            elif r.status_code == 404:
                return -1
    else:
        name = keyserver + "/api/{}/getkey/{}".format(API_VERSION, keyid)
        try:
            r = requests.get(name)
        except requests.exceptions.ConnectionError:
            return -2
        else:
            if r.status_code == 200:
                data = r.json()['key']
            else:
                return -1

    if data:
        add_key(data)
        return 0
