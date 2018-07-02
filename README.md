# Mulenerva

A prototype system for delivering curated educational materials to
internet-disconnected students.

Created for CSCE 482 (Computer Science Capstone) during Spring 2018 at Texas A&M
University.

## What's here?

This is the source code repository for the project, containing all code files
and static content necessary for building and deploying all aspects of the
Mulenerva project.

At its highest level, this project is divided into two sides: frontend and
backend. For the sake of organization, all frontend related files appear in the
`web` subdirectory, and all backend related files appear in the `python`
subdirectory.

The frontend folder is divided into three major components: *Local Server
Standard UI*, *Local Server Lite UI*, and *Datastore Server UI*. The backend
folder is divided into two major components: *Catalog Server* and *Data Mule*.
These components all serve roles related to their name, and can be found in
their own subfolder in either the `web` or `python` folder.

## How do I run stuff?

### Web Components

All web interfaces rely on the Angular framework and Node.js. First install Node.js via the instructions on their website. It is strongly recommended that you follow the instructions on the Node.js website, as your package manager’s default nodejs package may be out-of-date. At time of writing, official instructions are available here: https://nodejs.org/en/download/package-manager/

Once Node.js (and the related npm program) are installed, use the following command to install the Angular CLI:

	npm install -g @angular/cli
    
Then, change directory to the web interface you are seeking to install:

    ‘web/local_ui/client’ for the local server interface
    ‘web/datastore_ui’ for the datastore interface

Finally, once there, run npm install to install the necessary Node modules.

### Python Components

#### General Instructions

Although each Python component may have its own setup instructions, they all
function in a similar environment and require Python3, Pip, and Pipenv in order
to function. Before setting up any of the backend components, run the following:

    pipenv install
    pipenv shell

Then proceed to the correct instructions below.

#### Catalog Server

In order to run the Catalog server, simply run the following command.

`python run_server.py [community/datastore]`

If you want to take advantage of the Amazon S3 functionality, you will need
to make sure that AWS credentials exist on the system. The easiest way to
do this is to run the following commands.

```
pip install awscli
aws configure
```

There's a few unit tests available, which you can run with:

`python -m unittest discover`

**DO NOT - UNDER ANY CIRCUMSTANCES - COMMIT AWS CONFIGURATION FILES.**

#### Data Mule

The data mule is designed for use with a Raspberry Pi Zero W with an attached
PiOLED display, running Raspbian Stretch Lite. The following commands should
be run in order to ensure proper functionality:

1. Install the basic Linux and Python dependencies:
```
sudo apt-get update
sudo apt-get install git build-essential python-dev python-pip
sudo apt-get install python-imaging python-smbus i2c-tools
sudo pip install RPi.GPIO awscli boto3 requests requests_toolbelt
```

2. Install the Python drivers for the
[Adafruit Python SSD1306](https://github.com/adafruit/Adafruit_Python_SSD1306)
as follows:

```
git clone https://github.com/adafruit/Adafruit_Python_SSD1306.git
cd Adafruit_Python_SSD1306
sudo python setup.py install
```

3. Configure i2c:
`sudo raspi-config`

    Navigate to Interfacing Options -> I2C

    Select 'Yes' when prompted if you would like to enable the I2C interface

    Select 'Yes' when prompted to load the I2C kernel module

    `sudo reboot`

4. Finally, configure Amazon S3:
`sudo aws configure`

In order to run the mulenerva service, run with the following command:
`sudo python /home/pi/mulenerva/python/data_mule/transfer/transferServicePoll.py`
