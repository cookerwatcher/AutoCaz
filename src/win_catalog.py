'''
Filename: /src/twitch/faceover/src/win_catalog.py
Path: /src/twitch/faceover/src
Created Date: Monday, April 24th 2023, 2:10:14 pm
Author: hippy

Copyright (c) 2023 WTFPL
'''

import imgui
import tkinter as tk
from tkinter import filedialog



def draw_face_ids_window(face_encodings, face_ids):
    imgui.begin("Face IDs")
    imgui.listbox_header("##FaceIDs", 200, 250)
    selected_index = -1
    was_clicked = False
    for index, (face_encoding, face_id) in enumerate(zip(face_encodings, face_ids)):
        item_text = f"Face ID: {face_id}"
        was_clicked, _ = imgui.selectable(item_text, index == selected_index)
        if was_clicked:
            selected_index = index
            break
    imgui.listbox_footer()

    imgui.end()



def draw_catalog_window(self):
        imgui.begin("Catalog")
        # Create a list of names associated with person IDs and make a listbox with the names
        names_list = [f"{person_data['name']}" for person_id, person_data in self.person_catalog.catalog.items()]
        imgui.listbox_header("##List", 200, 400)
        selected_index = None
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

   
                imgui.new_line()


                # list all fade_ids for this person
                for face_id in person_data["face_ids"]:
                    imgui.text(f"Face ID: {face_id}")

                imgui.new_line()

                # Image path
                # imgui.text("Image Path: " + self.image_path)
                # Image display
                texture_id, width, height = self.image_manager.get_person_image(self.image_path)
                if texture_id:
                    imgui.image(texture_id, 100, 100 * (height / width))


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
                        filetypes=[("Image files", "*.jpg ; *.png ; *.jpeg"), ("All files", "*.*")],
                        defaultextension="*.png",                        
                    )
                    if file_path:
                        self.image_to_replace_with = file_path

                imgui.text("Overlay Image: " + (self.image_to_replace_with or "None"))

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


                # Save button
                if imgui.button("Save"):
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
                        self.face_detector.remove_face(tmpid)                    
                    self.person_catalog.remove_person(self.selected_person_id)                    
                    self.selected_person_id = None

                if imgui.button("Terminator"):
                    self.face_detector.terminate_id = self.person_catalog.get_face_ids_for_person(self.selected_person_id)[0]

            imgui.end_child()

        imgui.end()

        # draw_face_ids_window(self.face_detector.face_encodings, self.face_detector.face_ids)
