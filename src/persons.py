'''
Filename: /src/twitch/faceover/src/persons.py
Path: /src/twitch/faceover/src
Created Date: Wednesday, April 12th 2023, 2:44:20 pm
Author: hippy

Copyright (c) 2023 WTFPL
'''

import os
import pickle
import uuid


class PersonCatalog:
    def __init__(self, catalog_path='faces/catalog.pkl'):
        self.catalog_path = catalog_path
        self.catalog = {}
        self.face_id_to_person = {}
        self._next_person_id = self.new_uuid()
        self._load_catalog()

    def new_uuid(self):
        return uuid.uuid4().hex

    def add_person(self, face_ids, name, image_path, notes='', image_to_replace_with=None, last_seen=None, scale=1.0, offset=(0, 0), alpha=1):
        person_id = self._next_person_id
        self._next_person_id = self.new_uuid()

        self.catalog[person_id] = {
            'face_ids': face_ids,
            'name': name,
            'image_path': image_path,
            'notes': notes,
            'last_seen': last_seen,
            'image_to_replace_with': image_to_replace_with,
            'scale': scale,
            'offset': offset,
            'alpha': alpha
        }
        for face_id in face_ids:
            self.face_id_to_person[face_id] = person_id
        self._save_catalog()

    def update_person(self, person_id, face_ids=None, name=None, image_path=None, notes=None, image_to_replace_with=None, last_seen=None, scale=None, offset=None, alpha=None):
        if person_id in self.catalog:
            if face_ids is not None:
                for old_face_id in self.catalog[person_id]['face_ids']:
                    if old_face_id in self.face_id_to_person: 
                        del self.face_id_to_person[old_face_id]

                self.catalog[person_id]['face_ids'] = face_ids
                for face_id in face_ids:
                    self.face_id_to_person[face_id] = person_id

            if image_to_replace_with is not None:
                self.catalog[person_id]['image_to_replace_with'] = image_to_replace_with
            if last_seen is not None:
                self.catalog[person_id]['last_seen'] = last_seen
            if name is not None:
                self.catalog[person_id]['name'] = name
            if image_path is not None:
                self.catalog[person_id]['image_path'] = image_path
            if notes is not None:
                self.catalog[person_id]['notes'] = notes
            if scale is not None:
                self.catalog[person_id]['scale'] = scale
            if offset is not None:
                self.catalog[person_id]['offset'] = offset
            if alpha is not None:
                self.catalog[person_id]['alpha'] = alpha
            self._save_catalog()
            return True

    def remove_person(self, person_id):
        if person_id in self.catalog:
            for face_id in self.catalog[person_id]['face_ids']: 
                if face_id in self.face_id_to_person:               
                    del self.face_id_to_person[face_id]

            image_path = self.catalog[person_id]['image_path']
            if os.path.exists(image_path):
                os.remove(image_path)

            del self.catalog[person_id]
            self._save_catalog()

    def get_face_ids_for_person(self, person_id):
        return self.catalog[person_id]['face_ids']

    def get_person_by_face_id(self, face_id):
        person_id = self.face_id_to_person.get(face_id)
        return self.catalog.get(person_id)

    def _save_catalog(self):
        with open(self.catalog_path, 'wb') as f:
            pickle.dump((self.catalog, self.face_id_to_person, self._next_person_id), f)

    def _load_catalog(self):
        if os.path.exists(self.catalog_path):
            with open(self.catalog_path, 'rb') as f:
                self.catalog, self.face_id_to_person, self._next_person_id = pickle.load(f)
            
    def find_person_by_name(self, name):
        for person_id, person_data in self.catalog.items():
            if person_data['name'].strip().lower() == name.strip().lower():
                return person_id
        return None            
