""" Display handler for transfer """

import sys
sys.path.append('/home/pi/mulenerva/python/data_mule/pimon/opt/pimon/monitor/modules/')
import monitor

m = monitor.Monitor()

def updateMsg(pTransfer,pStorage,pNetwork,pPower):
  m.update(pTransfer,pStorage,pNetwork,pPower)

def devMsg(devtext):
  m.devMsg(devtext)

def errMsg(code, errtext):
  m.errMsg(code, errtext)

def warnMsg(code):
  m.alertMsg(code)
