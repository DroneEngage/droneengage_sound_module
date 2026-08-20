[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/DroneEngage/droneengage_sound_module)

# DroneEngage Sound Module

A Python DroneEngage module that provides text-to-speech and audio file playback
on the drone unit. It listens on the inter-module UDP databus for sound commands
from the GCS or other modules.

Serves as a **reference sample** for writing DroneEngage plugins in Python.

## Features

- Text-to-speech via `espeak-ng` (en, ar, ru, es, ja)
- Audio file playback via `aplay` (.wav), `mpg123` (.mp3), or `ffplay` fallback
- **Configured sound library** — named sound entries in `de_snd.config.module.json`
  are published to the GCS as a dropdown via `TYPE_AndruavMessage_SOUND_LIST`
  (6530). Operators pick a friendly name; the module plays the corresponding file.
- Non-blocking playback queue (UDP receive thread never blocks)
- Remote config via GCS: volume, pitch, language, mute, sound library (live, no restart)
- Config template for GCS config UI (`template.json`)
- Sample audio files included in `sound_box/` (CC0 / OpenGameArt)
- Startup self-test speech
- Clean shutdown on Ctrl+C / SIGINT

## Installation

### 1. System dependencies (Ubuntu / Debian / Raspberry Pi OS)

The easiest way is to use the provided install script, which detects your
package manager (apt/dnf/yum/pacman), installs everything missing, and
verifies the result:

```bash
./install.sh
```

Or install manually:

```bash
sudo apt-get update
sudo apt-get install espeak-ng alsa-utils mpg123 ffmpeg
```

- `espeak-ng` — required, text-to-speech engine
- `alsa-utils` (provides `aplay`) — optional, .wav file playback
- `mpg123` — optional, .mp3 file playback
- `ffmpeg` (provides `ffplay`) — optional, fallback for .ogg and other formats

For additional language voices (e.g. Japanese):

```bash
sudo apt-get install espeak-ng-data
```

### 2. Python dependencies

```bash
pip install colorama
```

Or install the module itself (pulls in `colorama`):

```bash
python3 setup.py install
```

### 3. Verify espeak-ng works

```bash
espeak-ng -a 150 -p 75 "Hello, how are you today?"
```

## Running

```bash
python3 de_sound_module.py
```

With a custom config file:

```bash
python3 de_sound_module.py -c /path/to/de_snd.config.module.json
```

The module will check for missing dependencies at startup and print install
instructions if anything is missing.

## Configuration

Edit `de_snd.config.module.json`:

| Field | Default | Description |
|---|---|---|
| `module_id` | `SND` | Module identifier |
| `s2s_udp_target_ip` | `127.0.0.1` | Communicator IP |
| `s2s_udp_target_port` | `60000` | Communicator port |
| `s2s_udp_listening_ip` | `127.0.0.1` | This module's listen IP |
| `s2s_udp_listening_port` | `61025` | This module's listen port |
| `s2s_udp_packet_size` | `8192` | UDP datagram payload size |
| `default_volume` | `100` | Default speech volume (0-100) |
| `default_pitch` | `50` | Default espeak-ng pitch (0-99) |
| `default_language` | `en` | Default language (en, ar, ru, es, ja) |
| `muted` | `false` | Mute all speech/playback |
| `sound_files` | `[]` | Named sound library: array of `{ name, file }` entries |

All speech settings can be changed remotely from the GCS config UI without
restarting the module.

## Sound file library

The `sound_files` top-level key in `de_snd.config.module.json` defines a named
library of audio files that the GCS audio gadget displays as a dropdown:

```json
"sound_files": [
    { "name": "Alarm",  "file": "sound_box/alarm.wav" },
    { "name": "Siren",  "file": "sound_box/siren.mp3" }
]
```

- **`name`** — friendly display name shown in the GCS dropdown.
- **`file`** — path on the unit (absolute or relative to the module's CWD).
  Supports `.wav` (aplay), `.mp3` (mpg123), `.ogg`/other (ffplay fallback).

The module publishes this list to all connected GCS clients at startup and
after every config apply, using `TYPE_AndruavMessage_SOUND_LIST` (6530). A GCS
that connects later can request it on-demand by sending a `RemoteExecute` with
`C = 6530`; the module replies with the current library.

The `sound_box/` directory ships with sample CC0 audio files from
[OpenGameArt](https://opengameart.org). Replace them with your own files and
update `sound_files` accordingly.

### Config template (`template.json`)

The config UI groups are: **Communication** (UDP settings), **Speech
Settings** (volume/pitch/language/mute), and **Sound Files** (the library
array). Editing one group sends only that group's output, which is
shallow-merged into the module config by `ConfigFile.updateJSON()` (top-level
keys only). Because of this, `sound_files` is a top-level key.

## Bluetooth audio output (optional)

To route audio to a Bluetooth speaker on Raspberry Pi:

```bash
bluetoothctl
power on
discoverable on
scan on
pair 6D:4C:21:3A:DB:53
connect 6D:4C:21:3A:DB:53
```

Auto-connect script on boot:

```bash
#!/bin/bash
# Wait for the Bluetooth agent to register
while ! bluetoothctl show | grep -q 'Agent registered: yes'; do
    sleep 1
done

# Check if the device is already connected
if ! bluetoothctl info 6D:4C:21:3A:DB:53 | grep -q 'Connected: yes'; then
    bluetoothctl connect 6D:4C:21:3A:DB:53
    echo "yes" | bluetoothctl authorize service 0000110d-0000-1000-8000-00805f9b34fb
fi

echo "Bluetooth connection successful."
```
