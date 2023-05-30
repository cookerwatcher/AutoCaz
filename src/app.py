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

from src.persons import PersonCatalog
from src.obs_capture import OBSCapture
from src.win_catalog import draw_catalog_window
from src.win_detection import draw_detection_window
from src.face_detection import FaceDetector
import src.face_processing as face_processing
from src.server import run_server
from src.config import Config

class App:
    # application stats
    app_frame_count = 0
    app_start_time = perf_counter()
    app_fps = 0

    cfg = Config()

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

    # create face detector instance which will start the server
    face_detector = FaceDetector()    
    DetectorBusy = False

    frame = None # the current frame being processed from the input
    frame_copy = None
    face_locations = [] # the locations of the faces in the frame
    face_ids = [] # the ids of the faces in the frame

    # person catalog, for face recognition persistance
    person_catalog = PersonCatalog()

    # UI state
    obs_current_resolution_combo_index = 1
    obs_capture_resolutions = [
        "320x180",
        "640x360",
        "854x480",
        "960x540",
        "1280x720",
        "1366x768",
        "1600x900",
        "1920x1080",
    ]


    autoAddNewFaces = False  # if not true, then only known faces will be detected        
    distance_threshold = 0.5    
    replace_faces = True  
    terminate_id = None  # this is for the terminator effect.
    web_show_detections = True
    web_show_debug = False
    

    # UI state
    selected_person_id = None
    selected_person_name = ""
    image_path = ""
    notes = ""
    image_to_replace_with = ""
    image_manager = ImageManager()

    # this is application constructor

    def __init__(self):
        print("AutoCaz App Created :)")
     
        

    # boot the application.  returning anything except True here terminates the application
    def Setup(self):       
      
        run_server()


        self.face_detector.start()
        self.obs_input_texture = Texture(640, 360)
        self.face_detection_output_texture = Texture(640, 360)

        self.obs_capture.startup()
        self.obs_connected = self.obs_handler.connect()
        if self.obs_connected:
            self.obs_input_list = self.obs_handler.get_input_list()

        # look for cfg.OBS_LAST_INPUT_NAME in the list of inputs
        if self.obs_connected and self.cfg.OBS_LAST_SOURCE != "":
            input_names = [x['inputName'] for x in self.obs_input_list["inputs"]]
            for i in range(len(input_names)):
                if input_names[i] == self.cfg.OBS_LAST_SOURCE:
                    self.obs_input_id = i
                    self.obs_input_name = input_names[i]
                    break

        self.obs_current_resolution_combo_index = self.cfg.OBS_LAST_RESOLUTION
       
        self.obs_capture.set_source(self.obs_input_name)
    
    
        return True

    # shutdown the application
    def Teardown(self):

        self.cfg.OBS_LAST_SOURCE = self.obs_input_name
        self.cfg.save()

        # shutdown the face detector
        self.face_detector.input_queue.put("quit")
        # disconnect OBS capture, and command and control
        self.obs_capture._stop_capture()
        if self.obs_connected:
            self.obs_handler.disconnect()
        

    # Main application loop
    def AppMainLoop(self):
        
        detection_result = None

        # this call is non-blocking, returns nothing except when a new frame is available
        self.obs_input_image = self.obs_capture.get_image()  

        if self.obs_input_image is not None:
            self.obs_input_texture.update_texture_data(self.obs_input_image)
            self.obs_status_string = self.obs_capture.get_status_string()
           
            if self.cfg.DETECTION_ACTIVE:

                if self.DetectorBusy is not True:
                    self.frame_copy = self.obs_input_image.copy()
                    self.frame = self.obs_input_image
                    self.face_detector.input_queue.put(("detect", (self.frame, self.cfg.DETECTION_THRESHOLD)))
                    self.DetectorBusy = True
                else:
                    # check for results from the face detector
                    try:
                        detection_result = self.face_detector.output_queue.get(timeout=0.01)  # Timeout if no results are available                    
                    except:                    
                        pass # print("No results yet.")

                    if detection_result is not None:
                        # there was a new frame process
                        self.face_locations, self.face_ids = detection_result
                        
                        # print face locations and face IDs detections
                        if self.face_locations:
                            print("Face locations:", self.face_locations)
                            print("Face IDs:", self.face_ids)

                        # look through the persons catalog and see if any of the detected faces are known
                        for face_id in self.face_ids:
                            person = self.person_catalog.get_person_by_face_id(face_id)
                            if person:
                                print("Known face detected:", person)
                                self.person_catalog.update_last_seen(person)

                        face_processing.broadcast_face_data(self.frame, self.face_locations, self.face_ids, self.person_catalog, web_show_debug = self.cfg.OVERLAY_DEBUG, web_show_detections = self.cfg.OVERLAY_OUTPUT, terminate_id = self.terminate_id)
                        # clear the flag
                        if self.terminate_id is not None:
                            self.terminate_id = None
                                                    
                        # we shall do the the draw faces and persons catalog here
                        self.face_detection_output_image = face_processing.draw_faces(self.frame, self.face_locations, self.face_ids, self.person_catalog, replace_faces=self.cfg.DETECTION_REPLACE,debug=self.cfg.DETECTION_DEBUG)
                        self.face_detection_output_texture.update_texture_data(self.face_detection_output_image)
            
                        # setup for next detection.
                        self.DetectorBusy = False


    def AppUI(self):

        # input / detection window
        draw_detection_window(self)

        # person/face catalog window
        draw_catalog_window(self)

        #fps timer
        self.app_frame_count += 1
        if perf_counter() - self.app_start_time >= 1:
            self.app_fps = self.app_frame_count / (perf_counter() - self.app_start_time)
            self.app_frame_count = 0
            self.app_start_time = perf_counter()
        
        imgui.set_next_window_position(0, 0)
        imgui.set_next_window_size(100, 50)
        imgui.begin("FPS", flags=imgui.WINDOW_NO_TITLE_BAR)
        imgui.text("FPS: %.1f" % self.app_fps)
        imgui.end()

