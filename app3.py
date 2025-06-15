from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import cv2
import face_recognition
import numpy as np
import sqlite3
import os
from datetime import datetime, date
import pickle
from werkzeug.utils import secure_filename
import base64
import io
from PIL import Image

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure required directories exist
os.makedirs('static/uploads', exist_ok=True)
os.makedirs('face_encodings', exist_ok=True)
os.makedirs('database', exist_ok=True)

# Import utility functions
from utils.database_utils import init_db, add_student, get_all_students, mark_student_attendance, get_attendance_by_date, get_student_attendance
from utils.face_recognition_utils import save_face_encoding, load_face_encodings, recognize_face

# Initialize database
init_db()

@app.route('/')
def index():

    if request.method == 'POST':
        print(request.form)

    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        print("form details:  ",request.form)

    return render_template('register.html')

@app.route('/mark_attendance')
def mark_attendance():
    return render_template('mark_attendance.html')

@app.route('/register_student', methods=['POST'])
def register_student():
     
     if request.method == 'POST':

        print("--------------- inside of POST Method ------------------")
        try:
        
            student_id = request.form['student_id']
            student_name = request.form['student_name']
            student_email = request.form['student_email']
            student_course = request.form['student_cource']

            print("request.files:  ",request.form)

            
            if 'student_images' not in request.files:
                return jsonify({'error': 'No image file provided'}), 400

            file = request.files['student_images']

            # Check if file is selected
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
        
            
            print("request.files:  ",file)

            if file:

                filename = secure_filename(f"{student_id}_{file.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
            
                # Process face encoding
                if save_face_encoding(filepath, student_id):
                    # Add student to database
                    if add_student(student_id, student_name, student_email, student_course, filename):
                        return jsonify({'success': 'Student registered successfully'}), 200
                        # return redirect(url_for('index'))
                    else:
                        return jsonify({'error': 'Error saving student data'}), 401
                else:
                    os.remove(filepath)  # Remove uploaded file if face not detected
                    return jsonify({'error': 'No face detected in the image!'}), 400
        
        except Exception as e:
            return jsonify({'error': 'Exception while registring student!' +e}), 400


@app.route('/capture_attendance', methods=['POST'])
def capture_attendance():
    try:
        # Get image data from request
        image_data = request.json['image']
        
        # Decode base64 image
        image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert PIL image to numpy array
        image_np = np.array(image)
        
        # Convert RGB to BGR (OpenCV format)
        image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        
        # Recognize face
        student_id = recognize_face(image_bgr)
        
        if student_id:
            # Mark attendance
            current_date = date.today().isoformat()
            current_time = datetime.now().strftime('%H:%M:%S')

            if mark_student_attendance(student_id, current_date, current_time):

                # Get student name
                conn = sqlite3.connect('database/attendance.db')
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM students WHERE student_id = ?", (student_id,))
                result = cursor.fetchone()
                conn.close()
                
                student_name = result[0] if result else "Unknown"
                return jsonify({
                    'success': True,
                    'message': f'Attendance marked for {student_name} ({student_id})',
                    'student_id': student_id,
                    'student_name': student_name,
                    'time': current_time
                })
            
            else:
                return jsonify({
                    'success': False,
                    'message': 'Attendance already marked for today'
                })
        else:
            return jsonify({
                'success': False,
                'message': 'Face not recognized'
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@app.route('/view_attendance')
def view_attendance():
    date_filter = request.args.get('date', date.today().isoformat())
    student_filter = request.args.get('student_id', '')
    
    if student_filter:
        attendance_records = get_student_attendance(student_filter)
    else:
        attendance_records = get_attendance_by_date(date_filter)
    
    students = get_all_students()
    
    return render_template('view_attendance.html', 
                         attendance_records=attendance_records,
                         students=students,
                         selected_date=date_filter,
                         selected_student=student_filter)

@app.route('/api/students')
def api_students():
    students = get_all_students()
    return jsonify(students)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5010,debug=True)