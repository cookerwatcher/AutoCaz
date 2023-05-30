'''
Filename: /src/twitch/faceover/src/win_catalog.py
Path: /src/twitch/faceover/src
Created Date: Monday, April 24th 2023, 2:10:14 pm
Author: hippy

Copyright (c) 2023 WTFPL
'''

import imgui
import os
import tkinter as tk
from tkinter import filedialog



def draw_face_ids_window(self, face_encodings, face_ids):
    imgui.begin("Face IDs", self.cfg.SHOW_FACE_IDS_WINDOW)
    
    # number of items in the listbox
    num_items = len(face_ids)

    # for each item in the listbox, check if there is a person associated with it
    # if there is, display the person's name
    for index in range(num_items):
        face_id = face_ids[index]
        face_encoding = face_encodings[index]
        person_id = self.person_catalog.get_person_by_face_id(face_id)
        if person_id is not None:            
            imgui.text(f"Face ID: {face_id} is {person_id['name']}")            
            fname = f"{self.cfg.save_faces_path}face_{face_id}.jpg"
            texture_id, width, height = self.image_manager.get_person_image(fname)
            tcnt = 0
            if texture_id:
                imgui.same_line()
                imgui.image(texture_id, 100, 100 * (height / width))
                    # wrap every 3 images
        else:
            imgui.text(f"Face ID: {face_id} is Orphaned")
            
        imgui.same_line()
        if imgui.button(f"Delete##{face_id}", 80, 20):                
            self.face_detector.input_queue.put(("removeface", face_id))

    imgui.separator()

    # look for non-existent face_ids in persons
    for person in self.person_catalog.catalog.values():
        persons_face_ids_list = person['face_ids']
        # check persons_face_ids_list items to see if it's in face_ids
        for f_id in persons_face_ids_list:
            # check if the f_id is in face_ids
            if f_id not in face_ids:
                # if it is not, display the person's name
                imgui.text(f"Face ID: {f_id} is referenced by {person['name']}, but does not exist.")
                imgui.same_line()
                if imgui.button(f"Delete##{f_id}", 80, 20):                                        
                    if f_id in person['face_ids']:
                        person['face_ids'].remove(f_id)

    imgui.end()



def draw_catalog_window(self):
        imgui.begin("Catalog")   

        save_me = False

        # Create a list of names associated with person IDs and make a listbox with the names
        selected_index = None
        names_list = [f"{person_data['name']}" for person_id, person_data in self.person_catalog.catalog.items()]
        
        if imgui.listbox_header("##List", 180, 600):
            
            selected_id = None
            was_clicked = False
            for index, (person_id, name) in enumerate(zip(self.person_catalog.catalog.keys(), names_list)):
                was_clicked, _ = imgui.selectable(name, self.selected_person_id == person_id)
                if was_clicked:
                    selected_index = index
                    selected_id = person_id
                    break            
            imgui.listbox_footer()
            

        if selected_index is not None:
            self.selected_person_id = selected_id

        if self.selected_person_id is not None: # and selected_index >= 0:
            # If the item selection changed, update the person data
            if was_clicked:
                #self.selected_person_id = list(self.person_catalog.catalog.keys())[selected_index]
                person_data = self.person_catalog.catalog[self.selected_person_id]
                self.selected_person_name = person_data["name"]
                self.image_path = person_data["image_path"]
                self.notes = person_data["notes"]
                self.image_to_replace_with = person_data["image_to_replace_with"]

            # Create a child space for the properties editor
            imgui.same_line()

            imgui.begin_child("properties_editor")
            if self.selected_person_id is not None:
                person_data = self.person_catalog.catalog[self.selected_person_id]
  
                imgui.same_line()            
                if imgui.button("Terminator"):
                    self.terminate_id = self.person_catalog.get_face_ids_for_person(self.selected_person_id)[0]

                # list all fade_ids for this person
                for face_id in person_data["face_ids"]:
                    imgui.text(f"Face ID: {face_id}")

                imgui.new_line()

                # Image path
                # imgui.text("Image Path: " + self.image_path)
                # Image display

                # display an image for each face_id
                for face_id in person_data["face_ids"]:

                    fname = f"{self.cfg.save_faces_path}face_{face_id}.jpg"
                    texture_id, width, height = self.image_manager.get_person_image(fname)
                    tcnt = 0
                    if texture_id:
                        imgui.image(texture_id, 100, 100 * (height / width))
                        # wrap every 3 images
                        tcnt += 1
                        if (tcnt) % 3 != 0:
                            imgui.same_line()
                        

                imgui.new_line()
                # Name editor
                _, self.selected_person_name = imgui.input_text("Name", self.selected_person_name, 256)
                
                
                imgui.new_line()
                # Notes editor
                _, self.notes = imgui.input_text_multiline("Notes", self.notes, 256)
                
                # Image to replace with file dialog
                if imgui.button("Overlay Image"):
                    root = tk.Tk()
                    root.withdraw()
                    file_path = filedialog.askopenfilename(initialfile=self.image_to_replace_with,
                        title="Select Image to Overlay",
                        filetypes=[("Image files", "*.jpg ; *.png ; *.jpeg ; *.gif"), ("All files", "*.*")],
                        defaultextension="*.png",                        
                    )
                    if file_path:
                        self.image_to_replace_with = file_path
                        save_me = True

                # clear button
                imgui.same_line()
                if imgui.button("Clear"):
                    self.image_to_replace_with = None
                    person_data['image_to_replace_with'] = None
                    save_me = True

                # get just the filename
                just_filename = os.path.basename(self.image_to_replace_with) if self.image_to_replace_with else "None"

                imgui.text("Image: " + (just_filename or "None"))

                imgui.new_line()

                # Scale, Offset, and Alpha controls
                _, scale = imgui.slider_float("Scale", person_data.get('scale', 1.0), 0.1, 5.0)
                person_data['scale'] = scale
                offset_x, offset_y = person_data.get('offset', (0, 0))
                _, offset_x = imgui.slider_int("Offset X", offset_x, -100, 100)
                _, offset_y = imgui.slider_int("Offset Y", offset_y, -100, 100)
                person_data['offset'] = (offset_x, offset_y)
                _, alpha = imgui.slider_float("Alpha", person_data.get('alpha', 1.0), 0.0, 1.0)
                person_data['alpha'] = alpha

                imgui.new_line()

                # Save button
                if imgui.button("Save Person") or save_me:
                    save_me = False 

                    existing_person_id = self.person_catalog.find_person_by_name(self.selected_person_name)
                    if existing_person_id is not None and existing_person_id != self.selected_person_id:
                        # Merge the existing person with the currently selected person
                        existing_person_data = self.person_catalog.catalog[existing_person_id]
                        new_face_ids = list(set(existing_person_data['face_ids']).union(set(person_data['face_ids'])))
                        updated = self.person_catalog.update_person(
                            person_id=existing_person_id,
                            face_ids=new_face_ids,
                            name=self.selected_person_name,
                            image_path=self.image_path,
                            notes=self.notes,
                            image_to_replace_with=self.image_to_replace_with,                            
                        )
                        if updated:
                            # Remove the currently selected person from the catalog
                            self.person_catalog.remove_person(self.selected_person_id)
                            self.selected_person_id = existing_person_id
                            person_data = self.person_catalog.catalog[self.selected_person_id]
                    else:
                            updated = self.person_catalog.update_person(
                                self.selected_person_id,
                                name=self.selected_person_name,
                                image_path=self.image_path,
                                notes=self.notes,
                                image_to_replace_with=self.image_to_replace_with,
                            )
                    if updated:
                        person_data = self.person_catalog.catalog[self.selected_person_id]
                        self.selected_person_name = person_data["name"]
                        self.image_path = person_data["image_path"]
                        self.notes = person_data["notes"]
                        self.image_to_replace_with = person_data["image_to_replace_with"]
                        # Update the selected item to the merged item
                        selected_index = list(self.person_catalog.catalog.keys()).index(self.selected_person_id)


             # Delete button
                if imgui.button("Delete Person"):
                    tmpids = self.person_catalog.get_face_ids_for_person(self.selected_person_id)
                    for tmpid in tmpids:
                        self.face_detector.input_queue.put(("removeface", tmpid))
                        # self.face_detector.remove_face(tmpid)                    
                    self.person_catalog.remove_person(self.selected_person_id)                    
                    self.selected_person_id = None

           

            imgui.end_child()

        imgui.end()

        if self.cfg.SHOW_FACE_IDS_WINDOW:           
            draw_face_ids_window(self, self.face_detector.face_encodings, self.face_detector.face_ids)
