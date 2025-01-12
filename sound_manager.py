import subprocess
import platform


from de_common.colors import *

try:
    import pyttsx3
    pyttsx3_available = True
except ImportError:
    pyttsx3_available = False

class CSoundManager(object):

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CSoundManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        self.m_volume = 100
        self.m_pitch = 50
        self.m_language = 'en'
        self.use_pyttsx3 = False

        # Determine which speech engine to use
        if platform.system() == 'Linux' and subprocess.call(["which", "espeak-ng"], stdout=subprocess.DEVNULL) == 0:
            self.use_pyttsx3 = False  # Use espeak-ng
        elif pyttsx3_available:
            self.use_pyttsx3 = True  # Use pyttsx3
        else:
            raise RuntimeError(ERROR_CONSOLE_BOLD_TEXT + "No suitable speech engine found." + NORMAL_CONSOLE_TEXT)

    def say(self, text, language, pitch, volume):
        if isinstance(volume, int):
            self.m_volume = volume * 2
        if isinstance(pitch, int):
            self.m_pitch = pitch
            
        # Set the voice properties
        if language in ['ar', 'en', 'ru', 'es']:
            self.m_language = language
        else:
            raise ValueError("Unsupported language.")

        try:
            if self.use_pyttsx3:
                self._speak_with_pyttsx3(text)
            else:
                self._speak_with_espeak_ng(text)
        except Exception as e:
            print(ERROR_CONSOLE_BOLD_TEXT + f"Error speaking text: {e}" + NORMAL_CONSOLE_TEXT) 

    def _speak_with_espeak_ng(self, text):
        try:
            subprocess.run(["espeak-ng", "-a", str(self.m_volume), "-v", self.m_language, "-p", str(self.m_pitch), text], check=True)
        except subprocess.CalledProcessError as e:
            print(ERROR_CONSOLE_BOLD_TEXT + f"Error running espeak-ng: {e}" + NORMAL_CONSOLE_TEXT)

    def _speak_with_pyttsx3(self, text):
        engine = pyttsx3.init()
        engine.setProperty('volume', self.m_volume / 200)  # pyttsx3 volume is between 0.0 and 1.0
        engine.setProperty('rate', self.m_pitch)  # pitch is not supported in pyttsx3, use rate instead

        # Set voice for language if available
        voices = engine.getProperty('voices')
        for voice in voices:
            if self.m_language in voice.languages:
                engine.setProperty('voice', voice.id)
                break

        engine.say(text)
        engine.runAndWait()
