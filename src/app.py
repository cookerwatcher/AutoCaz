'''
Filename: /src/twitch/faceover/src/app.py
Path: /src/twitch/faceover/src
Created Date: Wednesday, April 12th 2023, 4:54:41 pm
Author: hippy

Copyright (c) 2023 WTFPL
'''

import imgui
import src.theme as theme
from src.image_manager import ImageManager
from time import perf_counter
from src.texture import Texture
from src.obs import OBSHandler
from src.face_detection import FaceDetector
from src.obs_capture import OBSCapture
from src.win_catalog import draw_catalog_window
from src.win_detection import draw_detection_window


class App:
    # application stats
    app_frame_count = 0
    app_start_time = perf_counter()
    app_fps = 0

    # OBS command and control
    obs_handler = OBSHandler()
    obs_connected = False
    obs_input_list = []
    obs_input_id = -1

    # OBS capture driver
    obs_capture = OBSCapture()
    obs_input_name = ""

    obs_input_image = None  # image captured from OBS
    obs_input_texture = None  # the texture that is used to display the image
    obs_status_string = ""


    # face detection
    face_detector = FaceDetector()
    face_detection_enabled = False
    face_detection_output_image = None
    # the texture that is used to display the image
    face_detection_output_texture = None
    face_locations = []
    face_ids = []

    selected_scale_option = 0  # Default to "Full"

    # person catalog, for face recognition persistance
    person_catalog = face_detector.person_catalog

    # UI state
    obs_current_resolution_combo_index = 0
    obs_capture_resolutions = [
        "640x360",
        "854x480",
        "960x540",
        "1280x720",
        "1366x768",
        "1600x900",
        "1920x1080",
    ]

    selected_person_id = None
    selected_person_name = ""
    image_path = ""
    notes = ""
    image_to_replace_with = ""
    image_manager = ImageManager()

    # this is application constructor

    def __init__(self):
        print("FaceOver App Created :)")
   
    # return face id of the face that was clicked on, or None if no face was clicked
    # def get_clicked_face_id(self, clicked_position):
    #     if clicked_position is None:
    #         return None

    #     clicked_x, clicked_y = clicked_position

    #     for face_id, (top, right, bottom, left) in zip(self.face_ids, self.face_locations):
    #         if left <= clicked_x <= right and top <= clicked_y <= bottom:
    #             return face_id
    #     return None

    # boot the application.  returning anything except True here terminates the application
    def Setup(self):
        self.obs_input_texture = Texture(320, 240)
        self.face_detection_output_texture = Texture(320, 240)

        self.obs_capture.startup()

        self.obs_connected = self.obs_handler.connect()
        if self.obs_connected:
            self.obs_input_list = self.obs_handler.get_input_list()

        theme.load_default_style()

        return True

    # shutdown the application
    def Teardown(self):
        # disconnect OBS command and control
        if self.obs_connected:
            self.obs_handler.disconnect()
        self.obs_capture._stop_capture()
        # stop face detector
        self.face_detector.stop()

    # Main application loop

    def AppMainLoop(self):
        self.AppUI()

        # this call is non-blocking, returns nothing except when a new frame is available
        self.obs_input_image = self.obs_capture.get_image()  

        if self.obs_input_image is not None:
            self.obs_input_texture.update_texture_data(self.obs_input_image)
            self.obs_status_string = self.obs_capture.get_status_string()

        # here we do the face detection on obs input image and return it as face_detection_output_image
        if self.obs_input_image is not None and self.face_detection_enabled:

            # this call is non-blocking, returns nothing except when a new recognition frame is available
            detection_result = self.face_detector.run_detection(self.obs_input_image)

            if detection_result is not None:
                # there was a new frame process
                self.face_detection_output_image, self.face_locations, self.face_ids = detection_result
                self.face_detection_output_texture.update_texture_data(self.face_detection_output_image)

                # we shall do the the draw faces and persons catalog here
                
                # print face locations and face IDs detections
                if self.face_locations:
                    print("Face locations:", self.face_locations)
                    print("Face IDs:", self.face_ids)






    def AppUI(self):

        # input / detection window
        draw_detection_window(self)

        # person/face catalog window
        draw_catalog_window(self)

        # draw the FPS counter
        # self.app_frame_count += 1
        # self.app_fps = self.app_frame_count / (perf_counter() - self.app_start_time)
        # imgui.set_next_window_position(0, 0)
        # imgui.set_next_window_size(100, 50)
        # imgui.begin("FPS", flags=imgui.WINDOW_NO_TITLE_BAR)
        # imgui.text("FPS: %.1f" % self.app_fps)
        # imgui.end()

        


