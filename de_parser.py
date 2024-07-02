
import json
from de_common.messages import *
from sound_manager import *

class CParser(object):

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CParser, cls).__new__(cls)
        return cls._instance
    
    def parseMessage(self, message, len, jMsg: json):
        #print(message)
        message_type = jMsg[ANDRUAV_PROTOCOL_MESSAGE_TYPE]
        message_command = jMsg[ANDRUAV_PROTOCOL_MESSAGE_CMD]
        if (message_type == TYPE_AndruavMessage_SOUND_TEXT_TO_SPEECH):
            sound_manager = CSoundManager()
            sound_manager.say(message_command['t'], message_command['l'], message_command['p'], message_command['v'])
            return
        
        if (message_type == TYPE_AndruavMessage_SOUND_PLAY_FILE):
            return
        
        return 