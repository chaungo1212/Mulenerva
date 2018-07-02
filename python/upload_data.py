#!/usr/bin/python3
"""A utility for uploading data to the catalog server."""

import json
from bson.json_util import dumps, loads
import sys

import requests


def main():
    environment = sys.argv[1]
    url = sys.argv[2]
    config_path = sys.argv[3]
    thumbnail_path = sys.argv[4]
    content_path = sys.argv[5]

    if environment == 'community':
        #print("Not implemented yet, sorry!")
        print("Adding catalog entry...")
        metadata = json.load(open(config_path, 'r'))
        metadata['size'] = 123
        metadata['thumbnail_key'] = ""
        metadata['content_key'] = ""
        upload_resp = requests.post(url + '/metadata/new', json=metadata)
        data = upload_resp.json()
        print("Upload successful! View metadata here: " + url + "/metadata/" + data["$oid"])
        return True

    elif environment == 'datastore':
        thumbnail_files = {'image': open(thumbnail_path, 'rb')}
        content_files = {'content': open(content_path, 'rb')}

        print("Uploading image...")
        thumbnail_resp = requests.post(url + '/image/new', files=thumbnail_files).json()

        print("Uploading content...")
        content_resp = requests.post(url + '/content/new', files=content_files).json()

        print("Adding catalog entry...")
        metadata = json.load(open(config_path, 'r'))
        metadata['size'] = content_resp['size']
        metadata['thumbnail_key'] = thumbnail_resp['key']
        metadata['content_key'] = content_resp['key']
        upload_resp = requests.post(url + '/metadata/new', json=metadata)
        data = upload_resp.json()
        print("Upload successful! View metadata here: " + url + '/metadata/' + data['$oid'])
        return True

    else:
        return False

if __name__ == '__main__':
    if len(sys.argv) != 6 or not main():
        print("Usage: upload_data.py [community/datastore] [url] [config.json] [thumbnail] [content]")
