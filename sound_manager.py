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
            # # Run the espeak-ng command with sudo and pipe the output to aplay
            # volume = self.m_volume * 2
            # language = self.m_language
            # pitch = self.m_pitch

            # cmd = ["sudo", "espeak-ng", "-a", str(volume), "-v", language, "-p", str(pitch), text]
            # espeak_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # aplay_proc = subprocess.Popen(["sudo", "aplay"], stdin=espeak_proc.stdout, stderr=subprocess.DEVNULL)

            # # Wait for both processes to complete
            # stdout, stderr = espeak_proc.communicate()
            # aplay_proc.communicate()
            
        except subprocess.CalledProcessError as e:
            print(f"Error running espeak-ng: {e}")
