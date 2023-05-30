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
import pickle
import os
import time
from queue import Empty
from multiprocessing import Process, Queue

class FaceDetector:
    def __init__(self, model='hog', encodings_path='faces/encodings.pkl', save_faces_path='faces/'):
        self.model = model        
        self.encodings_path = encodings_path
        self.save_faces_path = save_faces_path
        self.detector = dlib.get_frontal_face_detector()        
        self.face_encodings = []
        self.face_ids = []
        self.frame = None  # the current frame before we draw all over it
        self.input_queue = Queue()
        self.output_queue = Queue()
        self.process = None
  
        self.load_encodings()

    def start(self):
        # start the face detection process
        self.process = Process(target=face_detection_process, args=(self.input_queue, self.output_queue, self))
        self.process.start()

    def _check_path(self):
        if not os.path.exists(self.save_faces_path):
            os.makedirs(self.save_faces_path)

    def load_encodings(self):
        self._check_path()
        # load encodings
        if os.path.exists(self.encodings_path):
            with open(self.encodings_path, 'rb') as f:
                self.face_encodings, self.face_ids = pickle.load(f)

    def save_encodings(self):
        self._check_path()
        with open(self.encodings_path, 'wb') as f:
            pickle.dump([self.face_encodings, self.face_ids], f)

    def detect_faces(self, frame, distance_threshold = 0.6):                
        if frame is None or len(frame) < 1:
            print("detect_faces: Invalid frame!")
            return [], []
        
        # convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_frame, model=self.model)
                
        # get detected face encodings for all faces in the frame
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        output_face_ids = []      
        face_id = None

        # Loop through each face in this frame of video
        for this_face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
            face_id = None
                
            # See if the face is a match for the known face(s) from the database
            distances = face_recognition.face_distance(self.face_encodings, this_face_encoding)

            # if distances is empty, then there are no known faces
            if len(distances) > 0 and len(self.face_ids) > 0:          
                min_distance_index = distances.argmin() # the shortest distance is the closest match
                min_distance = distances[min_distance_index]

                # Check if the minimum distance is below the threshold
                if min_distance < distance_threshold:
                    face_id = self.face_ids[min_distance_index]
            else:
                face_id = None  # an unknown face was detected

            output_face_ids.append(face_id)

        # we return a list of face locations and face ids (where none is an unrecognized face)
        return face_locations, output_face_ids

    # remove a face from the list of faces, along with it's face_encoding and the face image file    
    def remove_face(self, face_id):

        # is the face_id in the list of face_ids?
        if face_id not in self.face_ids:            
            return False

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

        return True



def face_detection_process(input_queue, output_queue, face_detector):
    while True:
        try:
            result = input_queue.get(timeout=1)
            if result is not None:
                command, data = result
                
                if command == "detect":
                    frame, threshold = data                    
                    face_locations, face_ids = face_detector.detect_faces(frame, threshold)
                    output_queue.put((face_locations, face_ids))
                    if len(face_ids) > 0:
                        print(f"FR: Detected {len(face_ids)} faces")

                elif command == "removeface":
                    if face_detector.remove_face(data) == True:
                        print(f"FR: Removed face {data}")

                elif command == "addface":
                    face_id, face_encoding = data
                    face_detector.face_ids.append(face_id)
                    face_detector.face_encodings.append(face_encoding)
                    face_detector.save_encodings()   
                    print(f"FR: Added face {face_id}")     

                elif command == "quit":
                    print("FR: Quitting...")
                    break

                else:
                    print(f"FR: Unknown command: {command}")

        except Empty:
            time.sleep(0.01)
            continue

        except Exception as e:
            print(f"FR: Exception: {e}")
            break



