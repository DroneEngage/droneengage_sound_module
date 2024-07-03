import subprocess

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
        pass

    def say (self, text, language, pitch, volume):
        if (isinstance(volume,int)):
            self.m_volume = volume * 2
        if (isinstance(pitch,int)):
            self.m_pitch = pitch
            
        # Set the voice properties (optional)
        if (language == 'ar'):
            self.m_language = 'ar'
        elif (language == 'en'):
            self.m_language = 'en-us'
        elif (language == 'ru'):
            self.m_language = 'ru'
        elif (language == 'es'):
            self.m_language = 'es'
        
        try:
            subprocess.run(["espeak-ng", "-a", str(self.m_volume * 2), "-v", self.m_language, "-p", str(self.m_pitch) , text], check=True)

        except subprocess.CalledProcessError as e:
            print(f"Error running espeak-ng: {e}")
