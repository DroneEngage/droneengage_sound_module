import json

from de_common.messages import *
from de_common.colors import *


class CFacade_Base:
    def __init__(self, m_module):
        self.m_module = m_module

    def requestID(self, target_party_id):
        message = {
            "C": TYPE_AndruavMessage_ID
        }

        self.m_module.sendJMSG(target_party_id, message, TYPE_AndruavMessage_RemoteExecute, True)

    def sendErrorMessage(self, target_party_id, error_number, info_type, notification_type, description):
        """
        EN: error number "not currently processed".
        IT: info type indicate what component is reporting the error.
        NT: severity and compliant with ardupilot.
        DS: description message.
        """
        message = {
            "EN": error_number,
            "IT": info_type,
            "NT": notification_type,
            "DS": description
        }

        self.m_module.sendJMSG(target_party_id, message, TYPE_AndruavMessage_Error, False)

        print(f"\n{SUCCESS_CONSOLE_BOLD_TEXT} -- sendErrorMessage {NORMAL_CONSOLE_TEXT}{description}")

    def API_sendConfigTemplate(self, target_party_id, module_key, json_file_content_json, reply):
        message = {
            "a": CONFIG_STATUS_FETCH_CONFIG_TEMPLATE,
            "b": json_file_content_json,
            "k": module_key,
            "R": reply
        }

        self.m_module.sendJMSG(target_party_id, message, TYPE_AndruavMessage_CONFIG_STATUS, False)

    def API_sendSoundList(self, target_party_id, sound_files, reply):
        """
        Sends the configured sound file library to the GCS so the audio gadget
        can display a dropdown instead of a free-text path input.
        Mirrors the camera module's sendCameraList: payload "T" is the list of
        {"n": name, "f": file_path} entries, "R" marks a reply to a request.
        Use target_party_id="" to broadcast to all GCS (e.g. after a config apply).
        """
        message = {
            "T": sound_files,
            "R": reply
        }

        self.m_module.sendJMSG(target_party_id, message, TYPE_AndruavMessage_SOUND_LIST, False)

class MyFacade(CFacade_Base):
    def __init__(self, m_module):
        super().__init__(m_module)

    # Add your custom methods here
    def my_custom_method(self, arg1, arg2):
        # Implement your custom method here
        pass

