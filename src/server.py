'''
Filename: /src/twitch/faceover/src/server.py
Path: /src/twitch/faceover/src
Created Date: Monday, May 8th 2023, 12:23:13 pm
Author: hippy

Copyright (c) 2023 WTFPL
'''

import threading
from flask import Flask, render_template, send_file, url_for, make_response
from flask_socketio import SocketIO, emit
import os
from urllib.parse import unquote, quote
from src.config import Config

app = Flask(__name__)

# Load the config file
config = Config()
config.load()

app.config['SERVER_NAME'] = "localhost:" + str(config.WEBSERVER_PORT)
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/terminator.html')
def index2():
    return render_template('terminator.html')

@app.route('/images/<path:file_path>')
def serve_image(file_path):
    file_path = unquote(file_path)  # Decode the file path
    filename = "/" + file_path 
    #filename = os.path.join(file_path)

    # read the file as raw bytes
    with open(filename, 'rb') as f:
        file_bytes = f.read()

    # create a response with the file bytes and the appropriate headers
    response = make_response(file_bytes)
    response.headers['Content-Type'] = 'application/octet-stream'
    response.headers['Content-Disposition'] = 'attachment; filename={}'.format(filename)
    return response

def generate_image_url(file_path):
    with app.app_context():
        image_url = url_for('serve_image', file_path=quote(file_path))
    return image_url

def broadcast_faces(faces_data):
    socketio.emit('faces_data', faces_data)

def broadcast_controls(controls):
    socketio.emit('controls', controls)

def start_server():
    socketio.run(app, host='0.0.0.0', port=config.WEBSERVER_PORT, debug=False)

def run_server():
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()

