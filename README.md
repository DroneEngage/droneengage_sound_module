

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





مَرحبًا



#!/bin/bash

# Wait for the Bluetooth agent to register
while ! bluetoothctl show | grep -q 'Agent registered: yes'; do
    sleep 1
done

# Check if the device is already connected
if ! bluetoothctl info 6D:4C:21:3A:DB:53 | grep -q 'Connected: yes'; then
    # Connect to the device
    bluetoothctl connect 6D:4C:21:3A:DB:53
    # Authorize the service
    echo "yes" | bluetoothctl authorize service 0000110d-0000-1000-8000-00805f9b34fb
fi

echo "Bluetooth connection successful."


python3 setup.py install
