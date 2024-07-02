import re
import json

class ConfigFile:
    
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ConfigFile, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, file_name):
        self.file_name = file_name
        self.config = self.load_config()

    def load_config(self):
        with open(self.file_name, 'r') as f:
            # Read the entire file content
            content = f.read()
            
            # Remove C-style comments (/* ... */)
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            
            # Remove C++-style comments (//)
            content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
            
            # Load the cleaned-up JSON data
            return json.loads(content)

    def get_value(self, key):
        return self.config[key]

