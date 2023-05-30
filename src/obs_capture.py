'''
Filename: /src/twitch/faceover/src/obs_capture.py
Path: /src/twitch/faceover/src
Created Date: Friday, April 14th 2023, 12:33:36 am
Author: hippy

Copyright (c) 2023
'''

import time
import numpy as np
from src.obs import OBSHandler
from threading import Thread, Event
from queue import Queue, Empty

QUEUE_SIZE = 1

def capture_loop(source_name, requested_width, requested_height, connected, capture_running, image_queue, status_queue, desired_capture_rate=1/5):
    obs_handler = OBSHandler()
    obs_handler.connect()
    print(f"OBSCap: Starting capture from source {source_name}")
    queue_full = False
    while connected.is_set() and capture_running.is_set():
        try:
            tmp = time.time()                
            frame = obs_handler.get_frame_from_source(
                source_name,
                width=requested_width if requested_width > 0 else None,
                height=requested_height if requested_height > 0 else None)

            obs_input_frametime = time.time() - tmp

            if frame is not None:
                # If the queue is full, remove the oldest frame
                if image_queue.qsize() == QUEUE_SIZE:
                    try:
                        image_queue.get_nowait()
                        if queue_full is not True:
                            print(f"OBSCap: Queue is Overflowing")
                            queue_full = True
                    except Empty:
                        pass
                else:
                    queue_full = False
                
                # Add the new frame to the queue
                image_queue.put(frame)

                width, height = frame.shape[1], frame.shape[0]

                time_since_last_frame = time.time() - tmp
                if time_since_last_frame < desired_capture_rate:
                    time.sleep(desired_capture_rate - time_since_last_frame)

                status_string = f"OBS: {'Connected' if connected.is_set() else 'Disconnected'} | "
                status_string += f"Source: '{source_name}' {width}x{height} @ {1/desired_capture_rate:.2f} | "
                status_string += f"Frame time: {(obs_input_frametime * 1000):.2f}ms"
                
                status_queue.put(status_string)

        except Exception as e:
            time.sleep(0.1)
                        

    print(f"OBSCap: Capture loop stopped")
    capture_running.clear()

class OBSCapture:
    def __init__(self):
        self.source_name = None
        self.width = 640
        self.height = 360
        self.capture_thread = None
        self.capture_running = Event()
        self.connected = Event()

        self.image_queue = Queue(maxsize=QUEUE_SIZE)
        self.status_queue = Queue()

    def startup(self):
        self.connect()
        self._start_capture()

    def connect(self):
        obs_handler = OBSHandler()
        if obs_handler.connect():
            self.connected.set()
        else:
            time.sleep(5)

    def disconnect(self):
        self._stop_capture()
        self.connected.clear()

    def _start_capture(self):
        if self.capture_thread is not None and self.capture_thread.is_alive():
            return
        print(f"Starting capture from source {self.source_name}")
        self.capture_running.set()
        self.capture_thread = Thread(target=capture_loop, args=(self.source_name, self.width, self.height, self.connected, self.capture_running, self.image_queue, self.status_queue))
        self.capture_thread.start()

    def _stop_capture(self):
        self.capture_running.clear()
        if self.capture_thread is not None and self.capture_thread.is_alive():
            self.capture_thread.join()
            self.capture_thread = None

    def set_source(self, source_name):
        self._stop_capture()
        self.source_name = source_name
        self._start_capture()

    def set_resolution(self, width, height):
        self.width = width
        self.height = height
        if self.capture_running.is_set():
            self._stop_capture()
            self._start_capture()

    def get_image(self):
        if not self.connected.is_set() or not self.capture_running.is_set():
            return None # np.zeros((self.height, self.width, 3), dtype=np.uint8)
        else:
            try:                           
                return self.image_queue.get_nowait()  
            except Empty:
                return None

    def get_status_string(self):
        try:
            return self.status_queue.get_nowait()
        except Empty:
            return ''
