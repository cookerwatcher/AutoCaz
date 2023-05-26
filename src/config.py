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

class Config:

    def __init__(self, file='config.ini'):
        self.config = configparser.ConfigParser()
        self.file = file

        self.OBS_IP = "localhost"
        self.OBS_PORT = 4444
        self.OBS_PASSWORD = "faceover"
        self.WEBSERVER_PORT = 8080

    
    def load(self):
        if not os.path.exists(self.file):
            self.save()

        self.config.read(self.file)
        if 'OBS' not in self.config or 'WEB' not in self.config:
            raise Exception(f"Could not find required sections in {self.file}")
        self.OBS_IP = self.config.get('OBS', 'OBS_IP')
        self.OBS_PORT = self.config.getint('OBS', 'OBS_PORT')
        self.OBS_PASSWORD = self.config.get('OBS', 'OBS_PASSWORD')
        self.WEBSERVER_PORT = self.config.getint('WEB', 'WEBSERVER_PORT')

    def save(self):
        self.config.set('OBS', 'OBS_IP', self.OBS_IP)
        self.config.set('OBS', 'OBS_PORT', str(self.OBS_PORT))
        self.config.set('OBS', 'OBS_PASSWORD', self.OBS_PASSWORD)
        self.config.set('WEB', 'WEBSERVER_PORT', str(self.WEBSERVER_PORT))
        with open(self.file, 'w') as configfile:
            self.config.write(configfile)

