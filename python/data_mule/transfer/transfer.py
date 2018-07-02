"""
Functions to manage download and upload of all files
"""

import boto3
import botocore
import requests
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
import json
import os
import mprinter as mdisp

class Transfer:

  def __init__(self, localServerURL, catalogURL):
    # Display init message
    mdisp.devMsg("Init transfer...")

    self.timestamp = 0
    self.localServerURLformat = localServerURL + '%s'
    self.catalogURLformat = catalogURL + 'changelog/get_changes_after/%s'
    self.catalogDIR = '/tmp/catalog/'
    self.catalogNAME = 'catalog.json'
    self.dataDIR = '/tmp/data/'

    # Ensure that catalogdir and datadir exist
    if not os.path.exists(self.catalogDIR):
      os.makedirs(self.catalogDIR)
    if not os.path.exists(self.dataDIR):
      os.makedirs(self.dataDIR)

    # Set up s3
    client = boto3.client('s3')
    config = boto3.s3.transfer.TransferConfig(multipart_threshold=64*1024,
                                              multipart_chunksize=64*1024,
                                              max_concurrency=1)
    self.transfer = boto3.s3.transfer.S3Transfer(client,config)
    self.bucketname = 'mulenerva-catalog'

    self.reqs = []

    # Display init complete message
    mdisp.devMsg("Init transfer...Done")
    return


  # Get storage capacity
  def getStorage(self):
    st = os.statvfs('/')
    total = st.f_blocks * st.f_frsize
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    try:
      pStorage = float(used)/total
    except ZeroDivisionError:
      pStorage = 0
    return pStorage


  # Get network quality
  def getNetwork(self):
    fw = open('/proc/net/wireless','r')
    pNetwork = float(fw.readlines()[2].split()[2][:-1])/70
    return pNetwork


  # Get battery percentage (currently unavailable)
  def getPower(self):
    return 1.0


  def recvRequests(self):
    # Display action
    mdisp.devMsg('Receive\r\nRequests')

    # DEBUG this is a sample requests file to get
    #fp = open('testdata/sample_requests.json')
    #reqs = json.load(fp)
    #fp.close()
    url = self.localServerURLformat % ('metadata/requested')
    r = requests.get(url)
    reqs = r.json()

    # Display action complete
    mdisp.devMsg('Receive\r\nRequests\r\nDone')
    return reqs


  def setRequests(self, reqs):
    self.reqs = reqs
    return


  def syncTimestamp(self):
    # Display action
    mdisp.devMsg('Sync\r\nTimestamp')

    url = self.localServerURLformat % 'changelog/latest_timestamp'
    r = requests.get(url)
    self.timestamp = int(r.text)

    # Display action complete
    mdisp.devMsg('Sync\r\nTimestamp\r\nComplete')
    return


  def dlCatalog(self):
    """ Get most recent catalog from datastore given timestamp t """
    # Display action
    mdisp.devMsg('Catalog\r\nDownload\r\n%d' % (self.timestamp))

    url = self.catalogURLformat % str(self.timestamp)
    r = requests.get(url)
    catalogFile = open(self.catalogDIR + self.catalogNAME, 'w')
    json.dump(r.json(), catalogFile)
    catalogFile.close()

    # Display action complete
    mdisp.devMsg('Catalog\r\nDownload\r\n%d\r\nDone' % (self.timestamp))
    return


  def dlContent(self, request):
    """ Get the content """
    oid = request['_id']['$oid']
    thumbkey = request['thumbnail_key']
    contentkey = request['content_key']
    # Check if we're downloading nothing
    if len(thumbkey) == 0 or len(contentkey) == 0:
      mdisp.errMsg(1010,'No content')
      return

    # Make directory for oid, if it does not exist
    directory = self.dataDIR + oid + '/'
    if not os.path.exists(directory):
      os.mkdir(directory)
    thumbpath = directory + thumbkey
    contentpath = directory + contentkey
    
    # Handler for monitoring data
    self.sumBytes = 0
    def contentmonitor(txBytes):
      self.sumBytes += txBytes
      progress = float(self.sumBytes)/request['size']
      mdisp.updateMsg(progress, self.getStorage(), self.getNetwork(), self.getPower())
      return

    # Download the data
    try:
      self.transfer.download_file(self.bucketname, thumbkey, thumbpath)
      self.transfer.download_file(self.bucketname, contentkey, contentpath, callback=contentmonitor)
      # Mark as available
      request['is_requested'] = False
      request['is_available'] = True
      # Final status update
      mdisp.updateMsg(1.0, self.getStorage(), self.getNetwork(), self.getPower())
    except botocore.exceptions.ClientError as e:
      mdisp.errMsg(int(e.response['Error']['Code']),'s3 exception')
    return


  def upCatalog(self):
    # Display action
    mdisp.devMsg('Catalog\r\nUpload\r\n%d' % (self.timestamp))

    url = self.localServerURLformat % ('changelog/update')
    j = []
    if os.path.isfile(self.catalogDIR + self.catalogNAME):
      fp = open(self.catalogDIR + self.catalogNAME)
      j = json.load(fp)
      fp.close()
    r = requests.post(url, json=j)

    # Display action complete
    mdisp.devMsg('Catalog\r\nUpload\r\n%d\r\nComplete' % (self.timestamp))
    return


  def upContent(self, request):
    """ Upload content to datastore server """
    oid = request['_id']['$oid']
    thumbkey = request['thumbnail_key']
    contentkey = request['content_key']

    thumbpath = self.dataDIR + oid + '/' + thumbkey
    contentpath = self.dataDIR + oid + '/' + contentkey

    thumburl = self.localServerURLformat % ('image/new')
    contenturl = self.localServerURLformat % ('content/new')

    thumbfid = 'thumb_' + oid
    contentfid = 'content_' + oid

    thumbfile = open(thumbpath, 'rb')
    enc = MultipartEncoder({thumbfid : (thumbkey, thumbfile)})
    mon = MultipartEncoderMonitor(enc)
    r = requests.post(thumburl, data=mon, headers={'Content-Type': mon.content_type})
    thumbfile.close()

    # Upload content
    contentsize = int(request['size'])
    def contentmonitor(monitor):
      progress = float(monitor.bytes_read)/contentsize
      mdisp.updateMsg(progress, self.getStorage(), self.getNetwork(), self.getPower())
      return

    contentfile = open(contentpath, 'rb')
    enc = MultipartEncoder({contentfid : (contentkey, contentfile)})
    mon = MultipartEncoderMonitor(enc,contentmonitor)
    r = requests.post(contenturl, data=mon, headers={'Content-Type': mon.content_type})
    contentfile.close()

    # Trash content once uploaded
    os.remove(thumbpath)
    os.remove(contentpath)
    try:
      os.rmdir(self.dataDIR + oid)
    except:
      mdisp.errMsg(1234,'rmdir fail')

    # Final status update
    mdisp.updateMsg(1.0, self.getStorage(), self.getNetwork(), self.getPower())

    return
