import cv2
from PIL import Image
import face_recognition
import os
from src.server import broadcast_faces, broadcast_controls
from src.server import generate_image_url
from src.config import Config


cfg = Config()


color_palette = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
    (255, 0, 255), (0, 255, 255), (128, 0, 0), (0, 128, 0),
    (0, 0, 128), (128, 128, 0), (128, 0, 128), (0, 128, 128),
    (192, 0, 0), (0, 192, 0), (0, 0, 192), (192, 192, 0),
]


#takes in a frame and returns the frame with the faces drawn on it
def draw_faces(frame, face_locations, face_ids, person_catalog, replace_faces=False, debug=False):
        if not face_locations or not face_ids:
            return frame
      
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
                
                person = person_catalog.get_person_by_face_id(face_id)
                if person:
                    name = person['name']
    
            if replace_faces and person is not None:
                if person['image_to_replace_with'] is not None and os.path.exists(person['image_to_replace_with']):
                    # Replace face with the specified image
                    replacement_image_path = person['image_to_replace_with']
                    replacement_image = cv2.imread(replacement_image_path, cv2.IMREAD_COLOR)

                    if replacement_image is not None:
                        

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
            if debug == True:
                cv2.putText(frame, f"{name} ({face_id})", (left + 6, top - 6), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 1)
            else:
                cv2.putText(frame, f"{name}", (left + 6, top - 6), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 1)                                

        return frame



def get_clicked_face(clicked_position, face_locations):    
    clicked_face_location = None
    for face_location in face_locations:
        top, right, bottom, left = map(int, face_location)
        if (left <= clicked_position[0] <= right) and (top <= clicked_position[1] <= bottom):
            clicked_face_location = int(top), int(right), int(bottom), int(left)
            break
    return clicked_face_location


def process_clicked_face(frame, clicked_point, face_locations, person_catalog, queue):
    """
    Process the clicked face location and store the face information if a face is found.
    :param clicked_point: (x, y) tuple representing the clicked point on the frame
    """
    clicked_face_location = get_clicked_face(clicked_point, face_locations)
    
    if clicked_face_location is not None:
        # Face found, process and store it
        face_encoding = face_recognition.face_encodings(frame, [clicked_face_location])[0]

        if face_encoding is not None:
            # Assign a new face_id
            face_id = person_catalog.new_uuid()
  
            # Save the face image
            top, right, bottom, left = map(int, clicked_face_location)
            height, width, _ = frame.shape
            expand_top = max(int(top - (bottom - top) * (cfg.save_image_expansion_ratio - 1) / 2), 0)
            expand_bottom = min(int(bottom + (bottom - top) * (cfg.save_image_expansion_ratio - 1) / 2), height)
            expand_left = max(int(left - (right - left) * (cfg.save_image_expansion_ratio - 1) / 2), 0)
            expand_right = min(int(right + (right - left) * (cfg.save_image_expansion_ratio - 1) / 2), width)

            face_image = frame[expand_top:expand_bottom, expand_left:expand_right]
            face_image_pil = Image.fromarray(cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB))
            face_image_path = f"{cfg.save_faces_path}face_{face_id}.jpg"            
            face_image_pil.save(face_image_path)

            # send the encoded face to the server
            queue.put(("addface",(face_id, face_encoding)))            
            # add it to the catalog
            person_catalog.add_person([face_id], name='Unknown', image_path=face_image_path)




# Broadcast the face data to the web page
def broadcast_face_data(frame, face_locations, face_ids, person_catalog, web_show_debug = False, web_show_detections = True, terminate_id = None):
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
            person = person_catalog.get_person_by_face_id(face_id)

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
        "frame_width": frame.shape[1],
        "frame_height": frame.shape[0],
        "show_detections":web_show_detections if web_show_detections else False,  
        "show_debug": web_show_debug if web_show_debug else False,          
    }

    if terminate_id is not None:
        control_data["terminator_id"] = terminate_id

    broadcast_controls(control_data)
