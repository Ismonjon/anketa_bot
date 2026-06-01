import sqlite3

def init_db():
    conn = sqlite3.connect("students_base.db")
    cursor = conn.cursor()
    # user_id UNIQUE қилинди - бу тизимда бир киши 2 марта рўйхатдан ўтишини тўлиқ чеклайди
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            middle_name TEXT,
            birth_date TEXT,
            birth_certificate TEXT,
            passport TEXT,
            pinfl TEXT,
            phone TEXT,
            gender TEXT,
            address TEXT,
            father_name TEXT,
            mother_name TEXT,
            parents_work TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def get_student(user_id):
    conn = sqlite3.connect("students_base.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def save_student(user_id, data):
    conn = sqlite3.connect("students_base.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO students (
                user_id, first_name, last_name, middle_name, birth_date, 
                birth_certificate, passport, pinfl, phone, gender, 
                address, father_name, mother_name, parents_work
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, data['first_name'], data['last_name'], data['middle_name'], data['birth_date'],
            data['birth_certificate'], data['passport'], data['pinfl'], data['phone'], data['gender'],
            data['address'], data['father_name'], data['mother_name'], data['parents_work']
        ))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False  # Агар фойдаланувчи аллақачон мавжуд бўлса
    conn.close()
    return success

def update_student(user_id, data):
    conn = sqlite3.connect("students_base.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE students SET 
            first_name = ?, last_name = ?, middle_name = ?, birth_date = ?, 
            birth_certificate = ?, passport = ?, pinfl = ?, phone = ?, gender = ?, 
            address = ?, father_name = ?, mother_name = ?, parents_work = ?
        WHERE user_id = ?
    """, (
        data['first_name'], data['last_name'], data['middle_name'], data['birth_date'],
        data['birth_certificate'], data['passport'], data['pinfl'], data['phone'], data['gender'],
        data['address'], data['father_name'], data['mother_name'], data['parents_work'], user_id
    ))
    conn.commit()
    conn.close()

def get_all_students():
    conn = sqlite3.connect("students_base.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students ORDER BY created_at ASC")
    rows = cursor.fetchall()
    conn.close()
    return rows
