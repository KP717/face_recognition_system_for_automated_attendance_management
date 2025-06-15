# utils/face_recognition_utils.py
import face_recognition
import pickle
import os
import cv2
import numpy as np

def save_face_encoding(image_path, student_id):
    """Save face encoding for a student"""
    try:

        # Load image
        image = face_recognition.load_image_file(image_path)
        
        # Get face encodings
        face_encodings = face_recognition.face_encodings(image)
        
        if len(face_encodings) > 0:
            # Save the first face encoding
            encoding = face_encodings[0]
            
            # Save encoding to file
            encoding_path = f'face_encodings/{student_id}.pkl'
            with open(encoding_path, 'wb') as f:
                pickle.dump(encoding, f)
            
            return True
        else:
            return False
    except Exception as e:
        print(f"Error saving face encoding: {e}")
        return False

def load_face_encodings():
    """Load all face encodings"""
    known_encodings = []
    known_student_ids = []
    
    encoding_dir = 'face_encodings'
    if not os.path.exists(encoding_dir):
        return known_encodings, known_student_ids
    
    for filename in os.listdir(encoding_dir):
        if filename.endswith('.pkl'):
            student_id = filename[:-4]  # Remove .pkl extension
            
            try:
                with open(os.path.join(encoding_dir, filename), 'rb') as f:
                    encoding = pickle.load(f)
                    known_encodings.append(encoding)
                    known_student_ids.append(student_id)
            except Exception as e:
                print(f"Error loading encoding for {student_id}: {e}")
    
    return known_encodings, known_student_ids

def recognize_face(image):
    """Recognize face in the given image"""
    try:
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Find face locations and encodings
        face_locations = face_recognition.face_locations(rgb_image)
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
        
        if len(face_encodings) == 0:
            return None
        
        # Load known encodings
        known_encodings, known_student_ids = load_face_encodings()
        
        if len(known_encodings) == 0:
            return None
        
        # Compare faces
        face_encoding = face_encodings[0]
        matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.6)
        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
        
        if True in matches:
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                return known_student_ids[best_match_index]
        
        return None
    
    except Exception as e:
        print(f"Error in face recognition: {e}")
        return None