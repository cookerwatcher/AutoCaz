
'''
Filename: /src/twitch/faceover/src/win_detection.py
Path: /src/twitch/faceover/src
Created Date: Monday, May 8th 2023, 3:36:22 pm
Author: hippy

Copyright (c) 2023 WTFPL
'''

import imgui
import time
from src.face_processing import process_clicked_face
from src.config import Config   

cfg = Config()



def is_position_within_face_location(position, face_location):
    x, y = position
    top, right, bottom, left = face_location
    if left <= x <= right and top <= y <= bottom:
        return True
    return False


def draw_detection_window(self):
    # Detection results window
    imgui.begin(f"Input", True)

    if self.obs_input_list:
        input_names = [x['inputName'] for x in self.obs_input_list["inputs"]]

        # Create the combobox with the input names
        changed, selected_index = imgui.combo("Source", self.obs_input_id, input_names)

        # Perform the desired action when item selection changes
        if changed and selected_index != self.obs_input_id:            
            self.obs_input_id = selected_index
            self.obs_input_name = input_names[self.obs_input_id]
            cfg.OBS_LAST_SOURCE = input_names[self.obs_input_id]
            print(f"Input Selected: {self.obs_input_name}\n")
            tmpflag = False
            if (cfg.DETECTION_ACTIVE):
                tmpflag = True
                cfg.DETECTION_ACTIVE = False
               # time.sleep(2)                    
            self.obs_capture.set_source(self.obs_input_name)
            if (tmpflag):
                cfg.DETECTION_ACTIVE = True

    else:
        imgui.begin_child(f"##OBS_input", 200, 250)
        imgui.text(f"No inputs found.")
        imgui.end_child()

    imgui.same_line()

    if imgui.button(f"Refresh"):
        self.obs_input_list = self.obs_handler.get_input_list()

    # requested resolution from OBS
    res_changed, self.obs_current_resolution_combo_index = imgui.combo(
        "Resolution", self.obs_current_resolution_combo_index, self.obs_capture_resolutions
    )
    if res_changed:
        width, height = [int(
            x) for x in self.obs_capture_resolutions[self.obs_current_resolution_combo_index].split('x')]
        self.obs_capture.set_resolution(width, height)
        cfg.OBS_LAST_RESOLUTION = self.obs_current_resolution_combo_index

    imgui.new_line()    
    imgui.text(self.obs_status_string)
    imgui.new_line()    
    imgui.separator()
    imgui.new_line()
    
    _, cfg.DETECTION_ACTIVE = imgui.checkbox(f"Run Face Detection", cfg.DETECTION_ACTIVE)
    
    imgui.same_line()    
  #  _, self.face_detector.autoAddNewFaces = imgui.checkbox(f"Training", self.face_detector.autoAddNewFaces)

    _, cfg.OVERLAY_DEBUG = imgui.checkbox(f"Debugging", cfg.OVERLAY_DEBUG)

    if cfg.OVERLAY_DEBUG:
        imgui.same_line()
        _, cfg.SHOW_FACE_IDS_WINDOW = imgui.checkbox(f"Face IDs", cfg.SHOW_FACE_IDS_WINDOW)

        imgui.same_line()
        _, cfg.DETECTION_REPLACE = imgui.checkbox(f"Preview Replace", cfg.DETECTION_REPLACE)  
        
    _, cfg.DETECTION_THRESHOLD = imgui.slider_float(f"Detection Threshold", cfg.DETECTION_THRESHOLD, 0.0, 1.0)
    imgui.text("<-------------- Strict      | normal |      Loose -------------->")
    imgui.new_line()
    _, cfg.OVERLAY_OUTPUT = imgui.checkbox(f"Output Enable", cfg.OVERLAY_OUTPUT)
        

    
    imgui.new_line()
    if cfg.DETECTION_ACTIVE:

        # returned clicked position x,y relative to the pre-downscaled image
        clicked_position = self.face_detection_output_texture.display_imgui_image()

        if clicked_position is not None and self.frame is not None:
            for face_id, face_location in zip(self.face_ids, self.face_locations):
                if is_position_within_face_location(clicked_position, face_location):
                    print(f"Clicked on face ID: {face_id}")
                    process_clicked_face(frame=self.frame_copy, clicked_point=clicked_position, face_locations=self.face_locations, person_catalog=self.person_catalog, queue=self.face_detector.input_queue)
                    break

    else:
        self.obs_input_texture.display_imgui_image()
 
    imgui.end()

