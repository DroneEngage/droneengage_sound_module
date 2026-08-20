import time
import sys
import shutil
import random
import signal
import argparse
import time as time_module
from datetime import datetime


from __version__ import __version__
from de_common.colors import *
from de_common.de_module import *
from de_common.udpClient import *
from de_common.messages import *
from de_common.de_facade_base import *
from de_common.configFile import *
from de_parser import *
from sound_manager import CSoundManager, build_sound_list

MODULE_CLASS_SOUND              = "snd"
MODULE_KEY                      = "6b9858bc5ab9"

DEFAULT_UDP_DATABUS_PACKET_SIZE = 8192


MESSAGE_FILTER = [ TYPE_AndruavMessage_ID,
                    TYPE_AndruavMessage_RemoteExecute,
                    TYPE_AndruavMessage_SOUND_TEXT_TO_SPEECH,
                    TYPE_AndruavMessage_SOUND_PLAY_FILE,
                    TYPE_AndruavMessage_CONFIG_ACTION
]


cModule = CModule()
baseFacade = CFacade_Base (cModule)

def generate_random_module_id():
    return ''.join(random.choice('0123456789') for _ in range(12))

def apply_sound_config(config):
    """
    Applies volume/pitch/language/mute settings from the config dict to the live
    CSoundManager. Called once at startup, and again automatically whenever the
    GCS pushes a CONFIG_ACTION_APPLY_CONFIG - so remote volume/mute control works
    without needing to restart the module.
    """
    CSoundManager().configure(
        default_volume=config.get('default_volume'),
        default_pitch=config.get('default_pitch'),
        default_language=config.get('default_language'),
        muted=config.get('muted'),
    )
    # Re-publish the sound file library so the GCS dropdown reflects any edits
    # made through the config UI (e.g. added/removed/renamed entries).
    send_sound_list(config)


def send_sound_list(config, target_party_id="", reply=False):
    """
    Builds the sound file library from the current config and sends it to the
    GCS via TYPE_AndruavMessage_SOUND_LIST. By default broadcasts to all GCS
    (used after startup and after a config apply); pass a specific party id and
    reply=True when answering a RemoteExecute request.
    """
    # Guard: apply_sound_config() is called once before cModule.init() sets up
    # the UDP client, so cUDPClient is still None on the first (startup) call.
    # The startup push is handled separately after init() completes; this guard
    # lets apply_sound_config() safely call send_sound_list() on later (remote
    # config-apply) invocations when the UDP client is already up.
    if cModule.cUDPClient is None:
        return
    sound_files = build_sound_list(config)
    baseFacade.API_sendSoundList(target_party_id, sound_files, reply)

def displayVersion():
    print(SUCCESS_CONSOLE_BOLD_TEXT + "Drone-Engage Sound Module version " + INFO_CONSOLE_TEXT + __version__ + NORMAL_CONSOLE_TEXT)

def displayVersionOnly():
    print(__version__)

def checkDependencies():
    """
    Checks for required and optional system binaries at startup.
    Prints clear install instructions for whatever is missing, so the module
    works out-of-the-box on both Ubuntu and Raspberry Pi OS after following
    the printed instructions.
    """
    missing_required = []
    missing_optional = []

    if shutil.which("espeak-ng") is None:
        missing_required.append("espeak-ng")
    if shutil.which("aplay") is None:
        missing_optional.append("aplay (alsa-utils) - needed for .wav playback")
    if shutil.which("mpg123") is None:
        missing_optional.append("mpg123 - needed for .mp3 playback")

    if missing_required:
        print(ERROR_CONSOLE_BOLD_TEXT + "MISSING REQUIRED DEPENDENCIES:" + NORMAL_CONSOLE_TEXT)
        for dep in missing_required:
            print("  " + ERROR_CONSOLE_TEXT + "- " + dep + NORMAL_CONSOLE_TEXT)
        print()
        print(INFO_CONSOLE_TEXT + "Install on Ubuntu/Debian/Raspberry Pi OS:" + NORMAL_CONSOLE_TEXT)
        print("  sudo apt-get update && sudo apt-get install espeak-ng")
        print()
        print(INFO_CONSOLE_TEXT + "For additional languages (e.g. Japanese): " + NORMAL_CONSOLE_TEXT)
        print("  sudo apt-get install espeak-ng-data")
        print()

    if missing_optional:
        print(LOG_CONSOLE_BOLD_TEXT + "Optional dependencies not found:" + NORMAL_CONSOLE_TEXT)
        for dep in missing_optional:
            print("  " + LOG_CONSOLE_TEXT + "- " + dep + NORMAL_CONSOLE_TEXT)
        print()
        print(INFO_CONSOLE_TEXT + "Install on Ubuntu/Debian/Raspberry Pi OS:" + NORMAL_CONSOLE_TEXT)
        print("  sudo apt-get install alsa-utils mpg123")
        print()

    if not missing_required and not missing_optional:
        print(SUCCESS_CONSOLE_TEXT + "All dependencies found." + NORMAL_CONSOLE_TEXT)

    return len(missing_required) == 0

exit_me = False

def quit_handler(sig, frame):
    print(INFO_CONSOLE_TEXT + "\nTERMINATING AT USER REQUEST" + NORMAL_CONSOLE_TEXT)
    try:
        uninit()
    except Exception:
        pass
    sys.exit(0)

def uninit():
    cModule.uninit()

def init():
    global exit_me
    exit_me = False

    instance_time_stamp = int(time_module.time())

    # Match C++ main.cpp init() sequence: leading newline, banner, version,
    # asctime-style timestamp + epoch seconds.
    print()
    print(SUCCESS_CONSOLE_BOLD_TEXT + "=================== STARTING PLUGIN ===================" + NORMAL_CONSOLE_TEXT)
    displayVersion()
    print(LOG_CONSOLE_BOLD_TEXT + time_module.strftime("%a %b %d %H:%M:%S %Y") + " "
          + str(instance_time_stamp) + INFO_CONSOLE_BOLD_TEXT + " seconds since the Epoch" + NORMAL_CONSOLE_TEXT)

    config_file_name = 'de_snd.config.module.json'
    if args.config:
        config_file_name = args.config

    print(LOG_CONSOLE_BOLD_TEXT + "Read internal config file: " + INFO_CONSOLE_TEXT + config_file_name + NORMAL_CONSOLE_TEXT)

    config_file = ConfigFile(config_file_name)

    # Check system dependencies (espeak-ng, aplay, mpg123) and print install
    # instructions for anything missing. The module still starts without the
    # optional tools, but espeak-ng is required for text-to-speech.
    checkDependencies()

    cParser = CParser(cModule, baseFacade, config_file, apply_sound_config)
    cModule.m_OnReceive = cParser.parseMessage

    # Report playback/speech failures back to the GCS instead of only printing them.
    CSoundManager().m_on_error = lambda desc: baseFacade.sendErrorMessage(
        "", 0, ERROR_USER_DEFINED, NOTIFICATION_TYPE_ERROR, desc)

    # Apply volume/pitch/language/mute defaults from the config file.
    apply_sound_config(config_file.config)

    # Define a Module
    cModule.defineModule(
        MODULE_CLASS_SOUND,  ## This class id known system-wide and is hardcoded.
        config_file.get_value('module_id'),
        MODULE_KEY,
        __version__,
        MESSAGE_FILTER      ## List of messages that this module wants to capture from de_communicator.
    )

    try:
        packet_size = int(config_file.get_value('s2s_udp_packet_size'), base=10)
    except (KeyError, ValueError, TypeError):
        print(INFO_CONSOLE_BOLD_TEXT + "WARNING:" + INFO_CONSOLE_TEXT
              + " MISSING FIELD " + ERROR_CONSOLE_BOLD_TEXT
              + "s2s_udp_packet_size " + INFO_CONSOLE_TEXT
              + "is missing in config file. default value "
              + ERROR_CONSOLE_BOLD_TEXT
              + str(DEFAULT_UDP_DATABUS_PACKET_SIZE)
              + INFO_CONSOLE_TEXT + " is used." + NORMAL_CONSOLE_TEXT)
        packet_size = DEFAULT_UDP_DATABUS_PACKET_SIZE

    # Initialize module and start communicator with de-communication.
    cModule.init(config_file.get_value('s2s_udp_target_ip'),
                 int(config_file.get_value('s2s_udp_target_port'), base=10),
                 config_file.get_value('s2s_udp_listening_ip'),
                 int(config_file.get_value('s2s_udp_listening_port'), base=10),
                 packet_size)

    # Startup self-test: quick way to confirm espeak-ng + audio routing work on a
    # fresh board without waiting for a real GCS command. Respects "muted".
    CSoundManager().say("Sound module ready")

    # Publish the sound file library so any connected GCS can populate its audio
    # gadget dropdown. A GCS that connects later can request it via RemoteExecute.
    send_sound_list(config_file.config)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sound Module Arguments')
    parser.add_argument('-c', '--config', default=None, help='Configuration file name')
    parser.add_argument('-v', '--version', action='store_true', default=False, help='display app version')
    parser.add_argument('-o', '--versiononly', action='store_true', default=False, help='display app version only numbers')
    args = parser.parse_args()

    if args.version:
        displayVersion()
        exit(0)

    if args.versiononly:
        displayVersionOnly()
        exit(0)

    signal.signal(signal.SIGINT, quit_handler)

    init()

    while not exit_me:
        time_module.sleep(1)

    uninit()
