'''
Filename: /src/twitch/faceover/src/config.py
Path: /src/twitch/faceover/src
Created Date: Monday, April 10th 2023, 3:29:01 pm
Author: hippy

Copyright (c) 2023 WTFPL
'''

# src/config.py
import configparser
import os

class SingletonType(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonType, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
        
class Config(metaclass=SingletonType):

    save_faces_path = 'faces/'
    save_image_expansion_ratio = 1.1


    def __init__(self, file='config.ini'):

        if hasattr(self, 'initialized'):
            return


        self.config = configparser.ConfigParser()
        self.file = file

        self.OBS_IP = "localhost"
        self.OBS_PORT = 4444
        self.OBS_PASSWORD = "AutoCaz"
        self.WEBSERVER_NAME = "127.0.0.1"
        self.WEBSERVER_PORT = 8080
        self.DETECTION_THRESHOLD = 0.5
        self.OVERLAY_DEBUG = False
        self.OVERLAY_OUTPUT = False
        self.DETECTION_ACTIVE = False
        self.DETECTION_REPLACE = True
        self.DETECTION_DEBUG = False
        self.OBS_LAST_SOURCE = ""
        self.OBS_LAST_RESOLUTION = 1
        self.SHOW_FACE_IDS_WINDOW = False
    
        self.load()

        self.initialized = True

    
    def load(self):
        if not os.path.exists(self.file):
            print(f"Config: file {self.file} does not exist, creating...")
            self.save()

        try:
            print(f"Config: Loading config file {self.file}")
            self.config.read(self.file)

            if 'OBS' not in self.config or 'WEB' not in self.config:
                raise Exception(f"Config: Could not find required sections in {self.file}!")
            
        except Exception as e:
            print(f"Error loading config file '"  +self.file+ "': {e}")
            return


        self.OBS_IP = self.config.get('OBS', 'OBS_IP', fallback='localhost')
        self.OBS_PORT = self.config.getint('OBS', 'OBS_PORT', fallback=4444)
        self.OBS_PASSWORD = self.config.get('OBS', 'OBS_PASSWORD', fallback='AutoCaz')

        self.OBS_LAST_RESOLUTION = self.config.getint('OBS', 'OBS_RES_INDEX', fallback=1)

        self.WEBSERVER_NAME = self.config.get('WEB', 'WEBSERVER_NAME', fallback='127.0.0.1')
        self.WEBSERVER_PORT = self.config.getint('WEB', 'WEBSERVER_PORT', fallback=8080)
        

        if 'DETECTION' in self.config:
            self.DETECTION_THRESHOLD = self.config.getfloat('DETECTION', 'DETECTION_THRESHOLD', fallback=0.5)
            self.DETECTION_REPLACE = self.config.getboolean('DETECTION', 'DETECTION_REPLACE', fallback=False)
            self.DETECTION_DEBUG = self.config.getboolean('DETECTION', 'DETECTION_DEBUG', fallback=False)
            self.DETECTION_ACTIVE = self.config.getboolean('DETECTION', 'DETECTION_ACTIVE', fallback=False)
            self.SHOW_FACE_IDS_WINDOW = self.config.getboolean('DETECTION', 'SHOW_FACE_IDS_WINDOW', fallback=False)
        if 'OVERLAY' in self.config:
            self.OVERLAY_DEBUG = self.config.getboolean('OVERLAY', 'OVERLAY_DEBUG', fallback=False)
            self.OVERLAY_OUTPUT = self.config.getboolean('OVERLAY', 'OVERLAY_OUTPUT', fallback=True)
        if 'OBS' in self.config:
            self.OBS_LAST_SOURCE = self.config.get('OBS', 'OBS_LAST_SOURCE', fallback="")


    def save(self):
        print(f"Saving config to {self.file}")
              
        if 'OBS' not in self.config:
            self.config.add_section('OBS')

        self.config.set('OBS', 'OBS_IP', self.OBS_IP)
        self.config.set('OBS', 'OBS_PORT', str(self.OBS_PORT))
        self.config.set('OBS', 'OBS_PASSWORD', self.OBS_PASSWORD)
        self.config.set('OBS', 'OBS_LAST_SOURCE', self.OBS_LAST_SOURCE)
        self.config.set('OBS', 'OBS_RES_INDEX', str(self.OBS_LAST_RESOLUTION))

        if 'WEB' not in self.config:
            self.config.add_section('WEB')

        self.config.set('WEB', 'WEBSERVER_PORT', str(self.WEBSERVER_PORT))
        self.config.set('WEB', 'WEBSERVER_NAME', self.WEBSERVER_NAME)

        if 'DETECTION' not in self.config:
            self.config.add_section('DETECTION')

        self.config.set('DETECTION', 'DETECTION_ACTIVE', str(self.DETECTION_ACTIVE))
        self.config.set('DETECTION', 'DETECTION_THRESHOLD', str(self.DETECTION_THRESHOLD))
        self.config.set('DETECTION', 'DETECTION_REPLACE', str(self.DETECTION_REPLACE))
        self.config.set('DETECTION', 'DETECTION_DEBUG', str(self.DETECTION_DEBUG))
        self.config.set('DETECTION', 'SHOW_FACE_IDS_WINDOW', str(self.SHOW_FACE_IDS_WINDOW))

        if 'OVERLAY' not in self.config:
            self.config.add_section('OVERLAY')
        
        self.config.set('OVERLAY', 'OVERLAY_OUTPUT', str(self.OVERLAY_OUTPUT))
        self.config.set('OVERLAY', 'OVERLAY_DEBUG', str(self.OVERLAY_DEBUG))

        try:
            with open(self.file, 'w') as configfile:
                self.config.write(configfile)

        except Exception as e:
            print(f"Error saving config: {e}")


