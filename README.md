[![Ardupilot Cloud EcoSystem](https://cloud.ardupilot.org/_static/ardupilot_logo.png "Ardupilot Cloud EcoSystem")](https://cloud.ardupilot.org "Ardupilot Cloud EcoSystem") **Drone Engage** is part of Ardupilot Cloud Eco System

------------

![Drone Engage Communicator Module](https://raw.githubusercontent.com/DroneEngage/droneengage_communication/master/resources/de_logo_title.png) 

# Drone Engage Sound Module

DroneEngage-Sound Module is a Python plugin that allows DroneEngage to generate text-to-speech output on speakers or Bluetooth devices. It supports both Ubuntu and Raspberry Pi OS.

## Features

- **Platform Support**: Compatible with both Raspberry Pi OS and Ubuntu.
- **Text-to-Speech Engines**:
  - Ubuntu: Uses `pyttsx3` for reliable speech generation.
  - Raspberry Pi OS: Uses `espeak-ng`.
- **Bluetooth Integration**: Optional support for audio output through Bluetooth speakers or headphones.
- **Customization Options**: Control volume and pitch of the spoken voice.
- **Language Support**: Supports various languages (refer to documentation for supported languages).

## Installation

### On Ubuntu

```sh
pip install pyttsx3
```

### On Raspberry Pi OS

```sh
sudo apt-get update
sudo apt-get install espeak-ng
espeak-ng -a 150 -p 75 "Hello, how are you today?"
```


### Bluetooth Setup (Optional)

```sh
bluetoothctl 
power on
discoverable on
scan on
pair 6D:4C:21:3A:DB:53
connect 6D:4C:21:3A:DB:53
```

### Usage

You can use this module by sending text from WebClient.

[![Sound Interface](https://raw.githubusercontent.com/DroneEngage/droneengage_sound_module/f12e6f30ec7e0ab805bde4034d5d60a340d9c114/resources/screen1.png "Sound Interface")](https://raw.githubusercontent.com/DroneEngage/droneengage_sound_module/f12e6f30ec7e0ab805bde4034d5d60a340d9c114/resources/screen1.png "Sound Interface")


### Configuration

The module configuration is stored in a JSON file. Below is an example configuration file (de_snd.config.module.json):

{
  "module_id": "SND",
  "s2s_udp_target_ip": "127.0.0.1",
  "s2s_udp_target_port": "60000",
  "s2s_udp_listening_ip": "127.0.0.1",
  "s2s_udp_listening_port": "61025",
  "s2s_udp_packet_size": "8192"
}


### Running the Module
To run the module, use the following command:
python3 de_sound_module.py



