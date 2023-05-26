'''
Filename: /src/twitch/faceover/src/obs.py
Path: /src/twitch/faceover/src
Created Date: Monday, April 10th 2023, 3:26:42 pm
Author: hippy

Copyright (c) 2023 WTFPL
'''


import cv2
import base64
import numpy as np
from obswebsocket import obsws, requests
from src.config import Config

Config = Config()
Config.load()
OBS_IP = Config.OBS_IP
OBS_PORT = Config.OBS_PORT
OBS_PASSWORD = Config.OBS_PASSWORD

class OBSHandler:

    version = ""

    def __init__(self, ip=OBS_IP, port=OBS_PORT, password=OBS_PASSWORD):
        self.client = obsws(ip, port, password)
        self.connedted = False
 
    def connect(self):
        try:
            self.client.connect()
            version = self.get_version()
            print("Connected to OBS. " + version)
            self.connected = True
            return True
        except Exception as e:
            print(f"Can't connect to OBS: Error: {e}")
            self.connected = False
            return False

    def disconnect(self):
        self.client.disconnect()
        print("Disconnected from OBS.")

    def get_version(self):
        version_string = self.client.call(requests.GetVersion())
        self.version = "OBS: " + version_string.datain['obsVersion'] + " Socket: " + version_string.datain['obsWebSocketVersion'] + " Platform: " + version_string.datain['platform'] + " " + version_string.datain['platformDescription']
        return self.version

    def get_input_list(self):
        if not self.connected:
            self.connect()

        if not self.connected:
            return None

        input_list = self.client.call(requests.GetInputList()).datain
        return input_list

    def get_current_program_scene_name(self):
        if not self.connected:
            self.connect()
        
        if not self.connected:
            return None

        scenes = self.client.call(requests.GetSceneList())
        current_program_scene_name = scenes.datain['currentProgramSceneName']
        return current_program_scene_name

    def get_scene_items(self, scene_name):
        if not self.connected:
            self.connect()

        if not self.connected:
            return None

        scene_items = self.client.call(requests.GetSceneItemList(sceneName=scene_name))
        sources = scene_items.getSceneItems()
        return sources


    def get_frame_from_source(self, source_name, width=None, height=None, compression_quality=None):
        if not self.connected:
            self.connect()
        
        if not self.connected:
            return None
        
        # Set the optional parameters for the GetSourceScreenshot request
        screenshot_params = {'sourceName': source_name, 'imageFormat': 'jpg'}
        if width is not None:
            screenshot_params['imageWidth'] = width
        if height is not None:
            screenshot_params['imageHeight'] = height
        if compression_quality is not None:
            screenshot_params['imageCompressionQuality'] = compression_quality

        # Take a screenshot of the specified source
        screenshot_data = self.client.call(requests.GetSourceScreenshot(**screenshot_params))
        base64_data = screenshot_data.datain["imageData"].split(',')[1]

        # Convert the screenshot data to an OpenCV frame
        image_data = np.frombuffer(base64.b64decode(base64_data), dtype=np.uint8)
        frame = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
        return frame
