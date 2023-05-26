'''
Filename: /src/twitch/faceover/src/texture.py
Path: /src/twitch/faceover/src
Created Date: Thursday, April 13th 2023, 10:43:31 pm
Author: hippy

Copyright (c) 2023 WTFPL
'''

import numpy as np
import imgui
import time
from OpenGL.GL import *
from threading import Lock
import cv2


class Texture:
    def __init__(self, width=None, height=None):
        self.texture_id = 0
        self.width = width
        self.height = height
        self.frame_count = 0
        self.start_time = time.time()
        self.fps = 0
        self.lock = Lock()

        if width and height:
            self.texture_id = self.create_texture(width, height)

    @staticmethod
    def create_texture(width, height):        
        texture_id = glGenTextures(1)
        texture_id = int(texture_id)  # Convert the texture_id to a Python integer
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
        glBindTexture(GL_TEXTURE_2D, 0)

        return texture_id


    def resize_texture(self, width, height):
        if self.texture_id:
            glDeleteTextures([self.texture_id])

        self.texture_id = self.create_texture(width, height)
        self.width = width
        self.height = height

    def update_texture_data(self, frame_rgb):

        if frame_rgb.size == 0:
            return

        if self.texture_id == 0:
            self.resize_texture(frame_rgb.shape[1], frame_rgb.shape[0])
        
        with self.lock:
            if frame_rgb.shape[1] != self.width or frame_rgb.shape[0] != self.height:
                self.resize_texture(frame_rgb.shape[1], frame_rgb.shape[0])

            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
            frame_rgb = frame_rgb.astype(np.uint8)
            glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, self.width, self.height, GL_BGR, GL_UNSIGNED_BYTE, frame_rgb)
            glBindTexture(GL_TEXTURE_2D, 0)

            self.frame_count += 1


    def display_imgui_image(self):
        clicked_position = None
        mouse_position = None

        if self.width != 0 and self.height != 0:

            #with self.lock:
            available_width = imgui.get_content_region_available_width()
            aspect_ratio = self.height / self.width
            imgui.image(self.texture_id, available_width, available_width * aspect_ratio)

            if imgui.is_item_hovered():
                image_pos_x, image_pos_y = imgui.get_item_rect_min()
                mouse_x, mouse_y = imgui.get_mouse_pos()
                rel_mouse_x = mouse_x - image_pos_x
                rel_mouse_y = mouse_y - image_pos_y

                scale_x = self.width / available_width
                scale_y = self.height / (available_width * aspect_ratio)
                mouse_position =(int(rel_mouse_x * scale_x), int(rel_mouse_y * scale_y))

                if imgui.is_item_clicked():
                    clicked_position = mouse_position
                    print(f"Clicked position: {clicked_position}")

            # fps counter
            elapsed_time = time.time() - self.start_time
            if elapsed_time >= 1.0:
                self.fps = self.frame_count / elapsed_time
                self.frame_count = 0
                self.start_time = time.time()

        imgui.text(f"FPS: {self.fps:.2f}")
        if mouse_position:
            imgui.text(f"Mouse position: {mouse_position}")

        return clicked_position
