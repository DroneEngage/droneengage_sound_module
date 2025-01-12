import random
import argparse
from datetime import datetime


from __version__ import __version__
from de_common.colors import *
from de_common.de_module import *
from de_common.udpClient import *
from de_common.messages import *
from de_common.de_facade_base import *
from de_common.configFile import *
from de_parser import *

MODULE_CLASS_SOUND              = "snd"

DEFAULT_UDP_DATABUS_PACKET_SIZE = 8192 


MESSAGE_FILTER = [ TYPE_AndruavMessage_ID,
                   TYPE_AndruavMessage_SOUND_TEXT_TO_SPEECH,
                   TYPE_AndruavMessage_SOUND_PLAY_FILE
]


cModule = CModule()
cParser = CParser()
cModule.m_OnReceive = cParser.parseMessage
baseFacade = CFacade_Base (cModule)

def generate_random_module_id():
    """
    Generates a random module ID consisting of 12 digits.

    Returns:
        str: A random 12-digit module ID.
    """
    return ''.join(random.choice('0123456789') for _ in range(12))

def displayVersion():
    """
    Displays the current version of the Drone-Engage Sound Module.
    """
    print(SUCCESS_CONSOLE_BOLD_TEXT + "Drone-Engage Sound Module version " + INFO_CONSOLE_TEXT + __version__ + NORMAL_CONSOLE_TEXT)

def displayVersionOnly():
    """
    Displays only the version number of the Drone-Engage Sound Module.
    """
    print(__version__)

if __name__ == "__main__":
    
    module_id = generate_random_module_id()
    print(SUCCESS_CONSOLE_BOLD_TEXT + "=================== STARTING PLUGIN ===================" + NORMAL_CONSOLE_TEXT)
    
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

    displayVersion()
    print(LOG_CONSOLE_BOLD_TEXT + str(datetime.now()) + NORMAL_CONSOLE_TEXT)

    config_file_name = 'de_snd.config.module.json'
    if args.config:
        config_file_name = args.config
    
    
    print(LOG_CONSOLE_BOLD_TEXT + "Read internal config file: " + INFO_CONSOLE_TEXT + config_file_name + NORMAL_CONSOLE_TEXT)

    # Load configuration
    config_file = ConfigFile(config_file_name)

    
    
    # Define a Module
    cModule.defineModule(
        MODULE_CLASS_SOUND,  ## This class id known system-wide and is hardcoded.
        config_file.get_value('module_id'),
        "6b9858bc5ab9",
        __version__,
        MESSAGE_FILTER      ## List of messages that this module wants to capture from de_communicator.
    )

    # Initialize module and start communicator with de-communication.
    cModule.init(config_file.get_value('s2s_udp_target_ip'), 
                 int(config_file.get_value('s2s_udp_target_port'), base=10),
                 config_file.get_value('s2s_udp_listening_ip'),
                 int(config_file.get_value('s2s_udp_listening_port'), base=10),
                 DEFAULT_UDP_DATABUS_PACKET_SIZE)

    
    