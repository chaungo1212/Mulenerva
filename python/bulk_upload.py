#!/usr/bin/python3
"""A utility for uploading many files to the datastore server."""

import json
import os
import sys

import requests


if __name__ == '__main__':
    if len(sys.argv) < 5:
        print("Usage: bulk_upload.py [url] [config.json] [thumbnail] [content1] ...")

    url = sys.argv[1]
    config_path = sys.argv[2]
    thumbnail_path = sys.argv[3]
    content_paths = sys.argv[4:]

    thumbnail_files = {'image': open(thumbnail_path, 'rb')}
    print("Uploading image...")
    thumbnail_resp = requests.post(url + '/image/new', files=thumbnail_files).json()

    for content_path in content_paths:
        title = os.path.basename(content_path).split('.')[0]

        print("Uploading content: " + title)
        content_files = {'content': open(content_path, 'rb')}
        content_resp = requests.post(url + '/content/new', files=content_files).json()

        print("Adding metadata: " + title)
        metadata = json.load(open(config_path, 'r'))
        metadata['size'] = content_resp['size']
        metadata['thumbnail_key'] = thumbnail_resp['key']
        metadata['content_key'] = content_resp['key']
        metadata['short_desc'] += title
        metadata['title'] = title
        upload_resp = requests.post(url + '/metadata/new', json=metadata)
        data = upload_resp.json()
        print("Upload successful! View metadata here: " + url + '/metadata/' + data['$oid'])
