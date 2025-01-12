[![Ardupilot Cloud EcoSystem](https://cloud.ardupilot.org/_static/ardupilot_logo.png "Ardupilot Cloud EcoSystem")](https://cloud.ardupilot.org "Ardupilot Cloud EcoSystem") **Drone Engage** is part of Ardupilot Cloud Eco System

------------

![Drone Engage Communicator Module](https://raw.githubusercontent.com/DroneEngage/droneengage_communication/master/resources/de_logo_title.png) 

# Drone Engage Sound Module
 This is a DroneEngage plugin module for generating text-to-speach output. It runs on ubuntu and RPI.

* Supports both Raspberry Pi OS and Ubuntu for versatile deployment options.
* Leverages the appropriate text-to-speech engine for each platform:
* Ubuntu: Uses pyttsx3 for reliable speech generation.
* Raspberry Pi OS: Uses espeak-ng.
* Bluetooth Integration (Optional):
Enables audio output through Bluetooth speakers or headphones for hands-free operation.
Provides clear instructions for pairing and connecting Bluetooth devices.
* Customization Options:
Control volume and pitch of the spoken voice to suit user preferences.
Supports various languages to cater to a global audience (refer to documentation for supported languages).

### Usage

You can use this module by sending text from WebClient.

[![Sound Interface](https://raw.githubusercontent.com/DroneEngage/droneengage_sound_module/f12e6f30ec7e0ab805bde4034d5d60a340d9c114/resources/screen1.png "Sound Interface")](https://raw.githubusercontent.com/DroneEngage/droneengage_sound_module/f12e6f30ec7e0ab805bde4034d5d60a340d9c114/resources/screen1.png "Sound Interface")



### Dependencies

On Ubuntu:
   
   pip install pyttsx3


On Raspberry Pi (running Raspberry Pi OS):

    sudo apt-get update
    sudo apt-get install espeak-ng
    espeak-ng -a 150 -p 75 "Hello, how are you today?"
    


    bluetoothctl 
    power on
    discoverable on
    scan on
    pair 6D:4C:21:3A:DB:53
    connect 6D:4C:21:3A:DB:53

