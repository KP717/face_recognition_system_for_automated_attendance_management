# utils/database_utils.py
import sqlite3
from datetime import datetime

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect('database/attendance.db')
    cursor = conn.cursor()
    
    # Create students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            course TEXT NOT NULL,
            photo_filename TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create attendance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            date DATE NOT NULL,
            time TIME NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (student_id),
            UNIQUE(student_id, date)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_student(student_id, name, email, course, photo_filename):
    """Add a new student to the database"""
    try:
        conn = sqlite3.connect('database/attendance.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO students (student_id, name, email, course, photo_filename)
            VALUES (?, ?, ?, ?, ?)
        ''', (student_id, name, email, course, photo_filename))
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def get_all_students():
    """Get all students from the database"""
    conn = sqlite3.connect('database/attendance.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT student_id, name, email, course FROM students ORDER BY name')
    students = cursor.fetchall()
    
    conn.close()
    return students

def mark_student_attendance(student_id, date, time):
    """Mark attendance for a student"""
    try:
        print("----------- cursor 100 -----------------")
        conn = sqlite3.connect('database/attendance.db')
        cursor = conn.cursor()
        print("----------- cursor 101 -----------------")

        cursor.execute('''
            INSERT INTO attendance (student_id, date, time)
            VALUES (?, ?, ?)
        ''', (student_id, date, time))
        print("----------- cursor 102 -----------------")

        conn.commit()
        conn.close()
        print("----------- cursor 103 -----------------")

        return True
    except sqlite3.IntegrityError:
        # Attendance already marked for today
        return False

def get_attendance_by_date(date):
    """Get attendance records for a specific date"""
    conn = sqlite3.connect('database/attendance.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.student_id, s.name, s.course, a.time
        FROM attendance a
        JOIN students s ON a.student_id = s.student_id
        WHERE a.date = ?
        ORDER BY a.time
    ''', (date,))
    
    records = cursor.fetchall()
    conn.close()
    return records

def get_student_attendance(student_id):
    """Get all attendance records for a specific student"""
    conn = sqlite3.connect('database/attendance.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.student_id, s.name, s.course, a.date, a.time
        FROM attendance a
        JOIN students s ON a.student_id = s.student_id
        WHERE s.student_id = ?
        ORDER BY a.date DESC, a.time DESC
    ''', (student_id,))
    
    records = cursor.fetchall()
    conn.close()
    return records