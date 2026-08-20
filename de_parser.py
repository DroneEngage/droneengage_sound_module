
import json
from de_common.messages import *
from de_common.de_config_action_handler import handle_config_action
from sound_manager import *

class CParser(object):

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CParser, cls).__new__(cls)
        return cls._instance

    def __init__(self, cModule=None, facade=None, config_file=None, on_config_applied=None):
        if cModule is not None:
            self.m_module = cModule
        if facade is not None:
            self.m_facade = facade
        if config_file is not None:
            self.m_config_file = config_file
        if on_config_applied is not None:
            self.m_on_config_applied = on_config_applied

    def parseMessage(self, message, len, jMsg: json):
        #print(message)
        message_type = jMsg[ANDRUAV_PROTOCOL_MESSAGE_TYPE]
        message_command = jMsg[ANDRUAV_PROTOCOL_MESSAGE_CMD]

        if (message_type == TYPE_AndruavMessage_CONFIG_ACTION):
            handle_config_action(self.m_module, self.m_facade, self.m_config_file, jMsg, message_command,
                                  getattr(self, 'm_on_config_applied', None))
            return

        if (message_type == TYPE_AndruavMessage_RemoteExecute):
            # The GCS requests the sound file library by sending a RemoteExecute
            # with C = TYPE_AndruavMessage_SOUND_LIST. Reply to the sender with
            # the current library built from config (mirrors camera list request).
            requested = message_command.get('C') if isinstance(message_command, dict) else None
            if requested == TYPE_AndruavMessage_SOUND_LIST:
                sender = jMsg.get(ANDRUAV_PROTOCOL_SENDER, "")
                sound_files = build_sound_list(self.m_config_file.config)
                self.m_facade.API_sendSoundList(sender, sound_files, True)
            return

        if (message_type == TYPE_AndruavMessage_SOUND_TEXT_TO_SPEECH):
            # fields: t=text, l=language, p=pitch, v=volume
            text = message_command.get('t')
            if text:
                sound_manager = CSoundManager()
                sound_manager.say(text, message_command.get('l'), message_command.get('p'), message_command.get('v'))
            return

        if (message_type == TYPE_AndruavMessage_SOUND_PLAY_FILE):
            # fields: f=file path to play (wav/mp3 handled via aplay/mpg123/ffplay)
            file_path = message_command.get('f')
            if file_path:
                sound_manager = CSoundManager()
                sound_manager.play_file(file_path)
            return
        
        return 