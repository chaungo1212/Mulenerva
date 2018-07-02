# Author: Peter Yung

import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


class Monitor:
  """
  Prototype PiOLED resource monitor for Mulenerva project
  This keeps track of percentages of:
    - Download/upload completion
    - Storage capacity
    - Network strength
    - Power supply
  """

  def __init__(self):
    # Define path for resources
    # TODO: Fix this for variable installation locations
    resourcePath = '/home/pi/mulenerva/python/data_mule/pimon/opt/pimon/monitor/resources/'

    # Initialize the progress to 0
    self.pTransfer = 0.0
    self.pStorage = 0.0
    self.pNetwork = 0.0
    self.pPower = 0.0

    # Raspberry Pi pin configuration:
    RST = 24

    # 128x32 display with hardware I2C:
    self.disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

    # Initialize library.
    self.disp.begin()

    # Clear display.
    self.disp.clear()
    self.disp.display()

    # Load a font
    self.font = ImageFont.load_default()

    # Load the icons
    uploadIcon = Image.open(resourcePath+'icons/uparrow.pbm')
    downloadIcon = Image.open(resourcePath+'icons/downarrow.pbm')
    storageIcon = Image.open(resourcePath+'icons/storage.pbm')
    networkIcon = Image.open(resourcePath+'icons/network.pbm')
    powerIcon = Image.open(resourcePath+'icons/power.pbm')

    # Create blank image for drawing.
    # Make sure to create image with mode '1' for 1-bit color.
    self.width = self.disp.width
    self.height = self.disp.height
    self.progressImage = Image.new('1', (self.width, self.height))
    self.devMsgImage = Image.new('1', (self.width, self.height))
    self.errMsgImage = Image.new('1', (self.width, self.height))
    self.alertBatteryImage = Image.open(resourcePath+'images/alertBattery.pbm')
    # Initialize backgrounds for these images
    self.initDevMsgImage()
    self.initErrMsgImage()
    self.initAlertMsgImage()

    # Get drawing object to draw on self.progressImage.
    draw = ImageDraw.Draw(self.progressImage)

    # Display four bars on the right side of the screen w/ icon labels
    self.barh = self.height/4
    self.bargap = 2
    self.bx0 = self.width/3
    self.bx1 = self.width-1
    self.by0 = 0
    self.by1 = self.barh - self.bargap
    baricons = [downloadIcon, storageIcon, networkIcon, powerIcon]
    for i in range(0,4):
      x0 = self.bx0
      y0 = i*self.barh + self.by0
      x1 = self.bx1
      y1 = i*self.barh + self.by1
      draw.rectangle((x0, y0, x1, y1),outline=255,fill=0)
      draw.bitmap((0, y0), baricons[i], fill=255)
    return


  def update(self,pTransfer=None,pStorage=None,pNetwork=None,pPower=None):
    """
    Update the display. Use 0 <= p <= 1
    """
    image = self.progressImage.copy()
    draw = ImageDraw.Draw(image)
    # Upload/Downlaod
    if pTransfer == None:
      pTransfer = self.pTransfer
    else:
      self.pTransfer = pTransfer
    # Storage
    if pStorage == None:
      pStorage = self.pStorage
    else:
      self.pStorage = pStorage
    # Network
    if pNetwork == None:
      pNetwork = self.pNetwork
    else:
      self.pNetwork = pNetwork
    # Power
    if pPower == None:
      pPower = self.pPower
    else:
      self.pPower = pPower

    ps = [pTransfer, pStorage, pNetwork, pPower]
    for i in range(0,4):
      x0 = self.bx0
      y0 = i*self.barh + self.by0
      x1 = self.bx0 + ps[i]*(self.bx1 - self.bx0)
      y1 = i*self.barh + self.by1
      draw.rectangle((x0,y0,x1,y1),outline=255,fill=255)
      # Need to offset text by -2 in order to display properly
      draw.text((12,y0-2), '{:3d}%'.format(int(100*ps[i])), font=self.font, fill=255)
    self.disp.image(image.rotate(180))
    self.disp.display()
    return


  def initDevMsgImage(self):
    """
    Create developer message template to draw on
    """
    return


  def devMsg(self, text):
    """
    Display a developer message on the screen
    """
    # Preprocess text
    lines = text.splitlines()

    image = self.devMsgImage.copy()
    draw = ImageDraw.Draw(image)
    # Text
    x0 = 0
    y0 = -2
    for i in range(0,len(lines)):
      draw.text((x0, y0+i*7), lines[i], font=self.font, fill=255)
    self.disp.image(image.rotate(180))
    self.disp.display()
    return


  def initErrMsgImage(self):
    """
    Create error message template to draw on
    """
    draw = ImageDraw.Draw(self.errMsgImage)
    # Outline
    draw.rectangle((0,0,self.width-1,self.height-1),outline=255,fill=0)
    # Stripes
    nLines = 8
    lineSlope = self.height/2
    for i in range(0,nLines):
      x0 = i*self.width/(2*nLines)
      y0 = 0
      x1 = x0 - lineSlope
      y1 = self.height
      draw.line((x0,y0,x1,y1),fill=255)
    # Text box
    x0 = self.width/4
    y0 = 0
    x1 = self.width-1
    y1 = self.height-1
    draw.rectangle((x0,y0,x1,y1),outline=255,fill=0)
    # Error symbols
    x0 = self.width/16
    y0 = 3*self.height/4
    x1 = 3*self.width/16
    y1 = y0
    x2 = (x0 + x1)/2
    y2 = self.height/4
    draw.polygon((x0,y0,x1,y1,x2,y2),outline=255,fill=255)
    draw.text((x0+6,y2+5),'!',font=self.font,fill=0)
    return


  def errMsg(self, code, text):
    """
    Display an error message on the screen
    """
    # Preprocess text
    lines = text.splitlines()

    image = self.errMsgImage.copy()
    draw = ImageDraw.Draw(image)
    # Text
    x0 = self.width/4 + 2
    y0 = -1
    draw.text((x0, y0), 'ERROR {:5d}'.format(code), font=self.font, fill=255)
    for i in range(0,len(lines)):
      draw.text((x0, y0 + (i+1)*7), lines[i], font=self.font, fill=255)
    self.disp.image(image.rotate(180))
    self.disp.display()
    return


  def initAlertMsgImage(self):
    """
    Display an alert message on the screen
    """
    return


  def alertMsg(self, code):
    """
    Display an alert symbol on the screen
    """
    if code == 1:
      self.disp.image(self.alertBatteryImage.rotate(180))
    self.disp.display()
    return


  def clear(self):
    self.disp.clear()
    self.disp.display()
    return

