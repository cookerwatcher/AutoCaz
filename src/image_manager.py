'''
Filename: /src/twitch/faceover/src/image_manager.py
Path: /src/twitch/faceover/src
Created Date: Sunday, April 16th 2023, 1:09:57 pm
Author: hippy

Copyright (c) 2023 WTFPL
'''

import cv2
import OpenGL.GL as gl

class ImageManager:
    def __init__(self):
        self.image_cache = {}

    def _load_image(self, filename):
        image = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
        if image is None:
            return 0, 0, 0

        if image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            internal_format = gl.GL_RGB
            format = gl.GL_RGB
        else:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
            internal_format = gl.GL_RGBA
            format = gl.GL_RGBA

        height, width, channels = image.shape

        texture_id = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, internal_format, width, height, 0, format, gl.GL_UNSIGNED_BYTE, image)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

        return texture_id, width, height

    def get_person_image(self, filename):
        if filename not in self.image_cache:
            texture_id, width, height = self._load_image(filename)
            if texture_id == 0:
                return 0, 0, 0

            self.image_cache[filename] = {'texture_id': texture_id, 'width': width, 'height': height}

        return self.image_cache[filename]['texture_id'], self.image_cache[filename]['width'], self.image_cache[filename]['height']

    def remove_image(self, filename):
        if filename in self.image_cache:
            gl.glDeleteTextures(1, [self.image_cache[filename]['texture_id']])
            del self.image_cache[filename]
