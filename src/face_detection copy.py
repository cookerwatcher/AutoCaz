'''
Filename: /src/twitch/faceover/src/face_detection.py
Path: /src/twitch/faceover/src
Created Date: Friday, May 19th 2023, 4:12:28 pm
Author: hippy

Copyright (c) 2023 WTFPL
'''

# src/face_detection.py
import cv2
import dlib
import face_recognition
from PIL import Image
import pickle
import os
import time
import threading

from src.persons import PersonCatalog
from src.server import run_server, broadcast_faces, broadcast_controls
from src.server import generate_image_url

class FaceDetector:
    def __init__(self, model='hog', downscale_factor=1, save_faces_path='faces/', encodings_path='faces/encodings.pkl', replace_faces=True):
        self.model = model
        self.save_faces_path = save_faces_path
        self.encodings_path = encodings_path
        
        self.face_encodings = []
        self.face_ids = []
        self.face_locations = []


        #inputs
        self.autoAddNewFaces = False  # if not true, then only known faces will be detected        
        self.distance_threshold = 0.6    
        self.replace_faces = replace_faces  
        self.terminate_id = None  # this is for the terminator effect.
        self.web_show_detections = True
        self.web_show_debug = False
        self.downscale_factor = downscale_factor
        
        self.save_image_expansion_ratio = 1.2  

        #outputs
        self.latest_input_frame = None
        self.scaled_x = 0
        self.scaled_y = 0
        self.latest_detection = None


        self.person_catalog = PersonCatalog()
        
        # state
        self.terminator_counter = 0
        self.frame = None  # the current frame before we draw all over it
        self.processing = False  
        self.new_detection_available = False

        self.detector = dlib.get_frontal_face_detector()

        # threading
        self.queue = [] # input frames
        self.queue_lock = threading.Lock()
        
        self.stop_thread = False  # control variable for the thread
        self.worker_thread = None # handle to the thread
        
        self.startup() # start the thread



    def startup(self):

        # init paths and load encodings
        if not os.path.exists(self.save_faces_path):
            os.makedirs(self.save_faces_path)

        if os.path.exists(self.encodings_path):
            with open(self.encodings_path, 'rb') as f:
                self.face_encodings, self.face_ids = pickle.load(f)

        # start the worker thread
        self.worker_thread = threading.Thread(target=self._worker_loop)  
        self.worker_thread.daemon = True      
        self.worker_thread.start()

        # Start the web server in a separate thread
        run_server()



    def _worker_loop(self):
        while not self.stop_thread:
            frame = None
            with self.queue_lock:
                if self.queue:
                    frame = self.queue.pop(0)

            if frame is None:
                time.sleep(0.01)  # Sleep for 10 milliseconds
                continue

            # save a copy before we draw all over the frame
            self.latest_input_frame = frame.copy()

            try:
                face_locations_scaled, face_ids = self.detect_faces(frame)            
                
                annotated_frame = self.draw_faces(frame, face_locations_scaled, face_ids)
                self.broadcast_face_data(face_locations_scaled, face_ids)

                self.latest_detection = (annotated_frame, face_locations_scaled, face_ids)
                self.face_locations = face_locations_scaled
                self.processing = False
                self.new_detection_available = True
            except Exception as e:
                print(f"Error during processing: {e}")


    def stop(self):
        self.stop_thread = True
        self.worker_thread.join()       


    def run_detection(self, frame):
        if self.processing:
            return None

        if self.new_detection_available:
            self.new_detection_available = False
            return self.latest_detection

        with self.queue_lock:
            if len(self.queue) < 1:
                self.queue.append(frame)
                self.processing = True
                self.frame = frame

        return None


    def detect_faces(self, frame):
        # Resize frame of video to 1*self.downscale_factor size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=1*self.downscale_factor, fy=1*self.downscale_factor)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB) # convert to RGB
        self.scaled_x = (rgb_small_frame.shape[1])
        self.scaled_y = (rgb_small_frame.shape[0])


        # find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame, model=self.model)

        # scale back up face locations since the frame we detected in was scaled to 1*self.downscale_factor size
        face_locations_scaled = [(top / self.downscale_factor, right / self.downscale_factor,
                                  bottom / self.downscale_factor, left / self.downscale_factor)
                                 for top, right, bottom, left in face_locations]

        # get detected face encodings for all faces in the frame
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)


        output_face_ids = []        
        face_id = None

        # Loop through each face in this frame of video
        for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations_scaled):
            face_id = None
                
            # See if the face is a match for the known face(s) from the database
            distances = face_recognition.face_distance(self.face_encodings, face_encoding)

            # if distances is empty, then there are no known faces
            if len(distances) > 0 and len(self.face_ids) > 0:          
                min_distance_index = distances.argmin() # the shortest distance is the closest match
                min_distance = distances[min_distance_index]

                # Check if the minimum distance is below the threshold
                if min_distance < self.distance_threshold:
                    face_id = self.face_ids[min_distance_index]
            else:
                face_id = None

            # unknown face detected
            if face_id is None and self.autoAddNewFaces == True:
                print(f"New face detected: {face_id}")
                face_id = self.person_catalog._next_person_id

                self.face_encodings.append(face_encoding)
                self.face_ids.append(face_id)

                # save the encodings and face_ids to disk
                with open(self.encodings_path, 'wb') as f:
                    pickle.dump((self.face_encodings, self.face_ids), f)

                height, width, _ = frame.shape

                # apply an expansion ratio to the face bounding box 
                expand_top = max(int(top - (bottom - top) * (self.save_image_expansion_ratio - 1) / 2), 0)
                expand_bottom = min(int(bottom + (bottom - top) * (self.save_image_expansion_ratio - 1) / 2), height)
                expand_left = max(int(left - (right - left) * (self.save_image_expansion_ratio - 1) / 2), 0)
                expand_right = min(int(right + (right - left) * (self.save_image_expansion_ratio - 1) / 2), width)

                # take the face image
                face_image = frame[expand_top:expand_bottom, expand_left:expand_right]
                face_image_pil = Image.fromarray(cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB))

                # where to save the face image
                face_image_path = f"{self.save_faces_path}face_{face_id}.jpg"
                #self.face_ids[face_id] = face_image_path
                face_image_pil.save(face_image_path)

                self.person_catalog.add_person([face_id], name='Unknown', image_path=face_image_path)

            else:
                # there was a known face detected, update the last seen time 
                person = self.person_catalog.get_person_by_face_id(face_id)
                if person:
                    person_id = self.person_catalog.face_id_to_person[face_id]
                    self.person_catalog.update_person(person_id, last_seen=time.time())

            output_face_ids.append(face_id)

        return face_locations_scaled, output_face_ids



    def draw_faces(self, frame, face_locations, face_ids):
        if not face_locations or not face_ids:
            return frame
        
        # Define a constant color palette (excluding black)
        color_palette = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
            (255, 0, 255), (0, 255, 255), (128, 0, 0), (0, 128, 0),
            (0, 0, 128), (128, 128, 0), (128, 0, 128), (0, 128, 128),
            (192, 0, 0), (0, 192, 0), (0, 0, 192), (192, 192, 0),
        ]

        cnt = -1
        for (top, right, bottom, left), face_id in zip(face_locations, face_ids):
            cnt += 1
            left = int(left)
            top = int(top)
            right = int(right)
            bottom = int(bottom)

            name = "Unknown"            
            person = None
            
            if face_id is None:
                color = (0, 0, 0)    
            else:
                # Choose a color based on the face_id
                color = color_palette[cnt % len(color_palette)]
                
                person = self.person_catalog.get_person_by_face_id(face_id)
                if person:
                    name = person['name']
    
            if self.replace_faces and person is not None:
                if person['image_to_replace_with'] is not None and os.path.exists(person['image_to_replace_with']):
                    # Replace face with the specified image
                    replacement_image_path = person['image_to_replace_with']
                    replacement_image = cv2.imread(replacement_image_path, cv2.IMREAD_COLOR)

                    # Apply scale and offset
                    face_width = right - left
                    face_height = bottom - top
                    scaled_width = int(face_width * person['scale'])
                    scaled_height = int(face_height * person['scale'])
                    offset_x, offset_y = person['offset']

                    # Calculate the center of the detection area
                    center_x = left + face_width // 2
                    center_y = top + face_height // 2

                    # Apply the offset to the center
                    center_x += offset_x
                    center_y += offset_y

                    # Calculate the position to draw the replacement image based on the modified center
                    draw_left = max(center_x - scaled_width // 2, 0)
                    draw_top = max(center_y - scaled_height // 2, 0)
                    draw_right = min(center_x + scaled_width // 2, frame.shape[1])
                    draw_bottom = min(center_y + scaled_height // 2, frame.shape[0])

                    # Resize the replacement image and apply it to the frame
                    replacement_image = cv2.resize(replacement_image, (scaled_width, scaled_height))
                    frame[draw_top:draw_bottom, draw_left:draw_right] = replacement_image[0:(draw_bottom - draw_top), 0:(draw_right - draw_left)]
                                    
                else:
                    # Draw the rectangle around the face
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            else:
                # Draw the rectangle around the face
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

            # Put the text regardless of whether the face is replaced or not
            if (self.web_show_debug):
                cv2.putText(frame, f"{name} ({face_id})", (left + 6, top - 6), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 1)
            else:
                cv2.putText(frame, f"{name}", (left + 6, top - 6), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 1)                                

        return frame


    def get_clicked_face(self, clicked_position):
        _, face_locations, _ = self.latest_detection
        clicked_face_location = None
        for face_location in face_locations:
            top, right, bottom, left = map(int, face_location)
            if (left <= clicked_position[0] <= right) and (top <= clicked_position[1] <= bottom):
                clicked_face_location = int(top), int(right), int(bottom), int(left)
                break
        return clicked_face_location

    def process_clicked_face(self, clicked_point):
        """
        Process the clicked face location and store the face information if a face is found.
        :param clicked_point: (x, y) tuple representing the clicked point on the frame
        """
        x, y = clicked_point
        scaled_x = x #* self.downscale_factor
        scaled_y = y #* self.downscale_factor
        frame = self.latest_input_frame

        clicked_face_location = self.get_clicked_face((scaled_x, scaled_y))
        face_encoding = None

        if clicked_face_location is not None:
            # Face found, process and store it
            face_encoding = face_recognition.face_encodings(frame, [clicked_face_location])[0]

            if face_encoding is not None:
                # Assign a new face_id
                face_id = self.person_catalog.new_uuid()

                self.face_encodings.append(face_encoding)
                self.face_ids.append(face_id)

                face_image_path = f"{self.save_faces_path}face_{face_id}.jpg"
                #self.face_ids[int(face_id)] = face_image_path

                # Save the face image
                top, right, bottom, left = map(int, clicked_face_location)
                height, width, _ = frame.shape
                expand_top = max(int(top - (bottom - top) * (self.save_image_expansion_ratio - 1) / 2), 0)
                expand_bottom = min(int(bottom + (bottom - top) * (self.save_image_expansion_ratio - 1) / 2), height)
                expand_left = max(int(left - (right - left) * (self.save_image_expansion_ratio - 1) / 2), 0)
                expand_right = min(int(right + (right - left) * (self.save_image_expansion_ratio - 1) / 2), width)

                face_image = frame[expand_top:expand_bottom, expand_left:expand_right]
                face_image_pil = Image.fromarray(cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB))
                face_image_pil.save(face_image_path)

                # Save the encodings and face_ids
                with open(self.encodings_path, 'wb') as f:
                    pickle.dump((self.face_encodings, self.face_ids), f)

                self.person_catalog.add_person([face_id], name='Unknown', image_path=face_image_path)



    # Broadcast the face data to the web page
    def broadcast_face_data(self, face_locations, face_ids):
        faces_data = []

        for (top, right, bottom, left), face_id in zip(face_locations, face_ids):
            person = None
            image_url = ""

            top = int(top)
            right = int(right)
            bottom = int(bottom)
            left = int(left)

            face_data = {
                "x": left,
                "y": top,
                "width": right - left,
                "height": bottom - top,
                "image_url": "",
                "name": "",
                "last_seen": "",
                "id": face_id if face_id is not None else "",
            }

            if face_id is not None:
                person = self.person_catalog.get_person_by_face_id(face_id)

                if person is not None:
                    face_data["name"] = person['name']
                    face_data["last_seen"] = person['last_seen']

                    if person['image_to_replace_with'] is not None:                        
                        face_data["image_url"] = generate_image_url(person['image_to_replace_with'])

                    # Apply scale and offset
                    face_width = face_data["width"]
                    face_height = face_data["height"]
                    scaled_width = int(face_width * person['scale'])
                    scaled_height = int(face_height * person['scale'])
                    offset_x, offset_y = person['offset']

                    # Calculate the center of the detection area
                    center_x = left + face_width // 2
                    center_y = top + face_height // 2

                    # Apply the offset to the center
                    center_x += offset_x
                    center_y += offset_y

                    # Calculate the position to draw the replacement image based on the modified center
                    face_data["x"] = max(center_x - scaled_width // 2, 0)
                    face_data["y"] = max(center_y - scaled_height // 2, 0)
                    face_data["width"] = scaled_width
                    face_data["height"] = scaled_height

            faces_data.append(face_data)

        broadcast_faces(faces_data)

        control_data = {
            "frame_width": self.frame.shape[1],
            "frame_height": self.frame.shape[0],
            "show_detections": self.web_show_detections if self.web_show_detections else False,  
            "show_debug": self.web_show_debug if self.web_show_debug else False,          
        }

        if self.terminate_id is not None:

            if self.terminate_id in self.face_ids:
                self.terminator_counter += 1

                if self.terminator_counter >= 3:
                    self.terminate_id = None
                    self.terminator_counter = 0
                else:
                    control_data["terminator_id"] = self.terminate_id

        broadcast_controls(control_data)


    # remove a face from the list of faces, along with it's face_encoding and person entry, and the face image file    
    def remove_face(self, face_id):

        # is the face_id in the list of face_ids?
        if face_id not in self.face_ids:            
            return

        # Find the index of the face_id in the self.face_ids list
        face_index = self.face_ids.index(face_id)
        
        # Remove the face_encoding and face_id from the respective lists
        del self.face_encodings[face_index]
        del self.face_ids[face_index]
               
        # Delete the face image file
        face_image_path = f"{self.save_faces_path}face_{face_id}.jpg"
        if os.path.exists(face_image_path):
            os.remove(face_image_path)

        # Save the updated encodings and face_ids to disk
        with open(self.encodings_path, 'wb') as f:
            pickle.dump((self.face_encodings, self.face_ids), f)
