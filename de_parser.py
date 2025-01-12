import json
from de_common.messages import *
from sound_manager import *

class CParser(object):
    """
    Singleton class responsible for parsing incoming messages and triggering appropriate actions.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensures only one instance of CParser is created (Singleton pattern).
        """
        if cls._instance is None:
            cls._instance = super(CParser, cls).__new__(cls)
        return cls._instance
    
    def parseMessage(self, message, len, jMsg: json):
        """
        Parses the incoming message and triggers the appropriate action based on the message type.

        Args:
            message (str): The raw message string.
            len (int): The length of the message.
            jMsg (json): The parsed JSON message.

        Returns:
            None
        """
        message_type = jMsg[ANDRUAV_PROTOCOL_MESSAGE_TYPE]
        message_command = jMsg[ANDRUAV_PROTOCOL_MESSAGE_CMD]

        if message_type == TYPE_AndruavMessage_SOUND_TEXT_TO_SPEECH:
            sound_manager = CSoundManager()
            sound_manager.say(message_command['t'], message_command['l'], message_command['p'], message_command['v'])
            return
        
        if message_type == TYPE_AndruavMessage_SOUND_PLAY_FILE:
            # Placeholder for handling sound file playback
            return
        
        return