
'''
Filename: /src/twitch/faceover/src/win_detection.py
Path: /src/twitch/faceover/src
Created Date: Monday, May 8th 2023, 3:36:22 pm
Author: hippy

Copyright (c) 2023 WTFPL
'''

import imgui
import time
import src.face_detection


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
            print(f"Input Selected: {self.obs_input_name}\n")
            tmpflag = False
            if (self.face_detection_enabled):
                tmpflag = True
                self.face_detection_enabled = False
                time.sleep(2)                    
            self.obs_capture.set_source(self.obs_input_name)
            if (tmpflag):
                self.face_detection_enabled = True

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

    imgui.new_line()    
    imgui.text(self.obs_status_string)
    imgui.new_line()    
    imgui.separator()
    imgui.new_line()
    
    _, self.face_detection_enabled = imgui.checkbox(f"Run Face Detection", self.face_detection_enabled)
    
    imgui.same_line()        
    _, self.face_detector.autoAddNewFaces = imgui.checkbox(f"Training", self.face_detector.autoAddNewFaces)
    imgui.same_line()
    _, self.face_detector.replace_faces = imgui.checkbox(f"Preview Replace", self.face_detector.replace_faces)  
    
    _, self.face_detector.distance_threshold = imgui.slider_float(f"Detection Threshold", self.face_detector.distance_threshold, 0.0, 1.0)

    imgui.new_line()
    _, self.face_detector.web_show_detections = imgui.checkbox(f"Output Enable", self.face_detector.web_show_detections)
    imgui.same_line()
    _, self.face_detector.web_show_debug = imgui.checkbox(f"Output Debug", self.face_detector.web_show_debug)

    # # Add downscaling options
    # scale_options = ["Full", "3/4", "1/2", "1/4"]
    # _, selected_option = imgui.combo("Downscale", self.selected_scale_option, scale_options)
    
    # if selected_option != self.selected_scale_option:
    #     self.selected_scale_option = selected_option
    #     update_downscale_factor(self)
    
    imgui.new_line()
    if self.face_detection_enabled:

        # returned clicked position x,y relative to the pre-downscaled image
        clicked_position = self.face_detection_output_texture.display_imgui_image()

        if clicked_position is not None:
            for face_id, face_location in zip(self.face_ids, self.face_locations):
                if is_position_within_face_location(clicked_position, face_location):
                    print(f"Clicked on face ID: {face_id}")
                    self.face_detector.process_clicked_face(clicked_position)

                    break
        imgui.same_line()
        imgui.text(f"Scaled Size: {self.face_detector.scaled_x}x{self.face_detector.scaled_y}") 

    else:
        self.obs_input_texture.display_imgui_image()
 

    imgui.end()


# def update_downscale_factor(self):
#     scale_factors = [1.0, 0.75, 0.5, 0.25]
#     self.face_detector.downscale_factor = scale_factors[self.selected_scale_option]
