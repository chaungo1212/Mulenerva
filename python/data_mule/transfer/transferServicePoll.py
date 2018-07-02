# REQUIRES ROOT PRIVELEGES

import transfer
import os
import signal
import mprinter as mdisp

def signal_handler(signal,frame):
  mdisp.errMsg(signal,"Process\r\nTerminated\r\nip=%s" % (getIP()))
  sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def getIP():
  ip = os.popen("ip addr show wlan0 | awk '/inet / {print $2}' | cut -d/ -f1").readline()
  return ip[:-1]

# Function to monitor core temperature
def coreTemp():
  temp = os.popen('vcgencmd measure_temp').readline()
  ftemp = float(temp.replace('temp=','')[:-3])
  if ftemp >= 80.0:
    mdisp.errMsg(4321,"Overheating\r\nTemp=%.1f C" % (ftemp))
    exit(1)
  return ftemp


communityURL = 'http://mulenerva.bitwisehero.com:5001/'
datastoreURL = 'http://mulenerva.bitwisehero.com:5002/'
t = transfer.Transfer(communityURL, datastoreURL)


def onLocalConnect():
  # 0: Upload catalog update
  t.upCatalog()
  # 1: Get server timestamp
  t.syncTimestamp()
  # 2: Upload content
  for request in t.reqs:
    if request['is_available']:
      t.upContent(request)
  # 3: Update request ledger
  reqs = t.recvRequests()
  t.setRequests(reqs)
  return


def onInternetConnect():
  # 0: Get catalog
  t.dlCatalog()
  # 1: Download content
  for request in t.reqs:
    if not request['is_available']:
      t.dlContent(request)
  return


"""
Poll both servers
"""

import requests
import sys
import time

communityPING = communityURL + 'ping'
datastorePING = datastoreURL + 'ping'
# Ping every n seconds
pingInterval = 5.0

# Repeatedly ping for both servers
try:
  while True:
    # Ping Local
    try:
      connected = False
      mdisp.devMsg('Pinging:\r\n%s\r\nip=%s' % (communityPING,getIP()))
      while not connected:
        try:
          r = requests.get(communityPING, timeout=pingInterval)
          if r.status_code < 400:
            connected = True
        except requests.exceptions.ConnectTimeout:
          mdisp.devMsg('Pinging:\r\n%s\r\n%d\r\nTemp=%.1f C\r\nip=%s' % (communityPING, time.time(), coretemp(), getIP()))
      # Connected Local
      mdisp.devMsg('Connected:\r\n%s' % (communityPING))
      onLocalConnect()

      mdisp.devMsg('Post-Local Rest\r\n%d secs\r\nTemp=%.1f C\r\nip=%s' % (pingInterval, coreTemp(), getIP()))
      time.sleep(pingInterval)
    except requests.exceptions.ConnectionError:
      mdisp.devMsg("Lost Connection")
    except requests.exceptions.ReadTimeout:
      mdisp.devMsg("Lost Connection on read")

    # Ping Datastore
    try:
      connected = False
      mdisp.devMsg('Pinging:\r\n%s\r\nip=%s' % (datastorePING, getIP()))
      while not connected:
        try:
          r = requests.get(datastorePING, timeout=pingInterval)
          if r.status_code < 400:
            connected = True
        except requests.exceptions.ConnectTimeout:
          mdisp.devMsg('Pinging:\r\n%s\r\n%d\r\nTemp=%.1f C\r\nip=%s' % (datastorePING, time.time(), coreTemp(), getIP()))
      # Connected Datastore
      mdisp.devMsg('Connected:\r\n%s' % (datastorePING))
      onInternetConnect()

      mdisp.devMsg('Post-Datastore Rest\r\n%d secs\r\nTemp=%.1f C\r\nip=%s' % (pingInterval, coreTemp(), getIP()))
      time.sleep(pingInterval)
    except requests.exceptions.ConnectionError:
      mdisp.devMsg("Lost connection...")
    except requests.exceptions.ReadTimeout:
      mdisp.devMsg("Lost Connection on read")

except:
  mdisp.errMsg(102,"Uncaught\r\nip=%s" % (getIP()))
  fp = open('crashlog.txt','w')
  fp.write(str(sys.exc_info()[0]))
  fp.close()
  exit(1)
