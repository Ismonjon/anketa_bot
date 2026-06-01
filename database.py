import sqlite3

def init_db():
    conn = sqlite3.connect("flexible_students.db")
    cursor = conn.cursor()
    
    # 1. Администратор қўшган динамик саволлар жадвали
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            field_name TEXT NOT NULL,
            question_text TEXT NOT NULL
        )
    """)
    
    # 2. Фойдаланувчилар (Ўқувчилар) жадвали
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            user_id INTEGER PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 3. Ота-оналар берган жавоблар жадвали
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS answers (
            user_id INTEGER,
            question_id INTEGER,
            answer_value TEXT,
            PRIMARY KEY (user_id, question_id),
            FOREIGN KEY (user_id) REFERENCES students(user_id) ON DELETE CASCADE,
            FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM questions")
    if cursor.fetchone()[0] == 0:
        default_questions = [
            ("Исми", "Ўқувчининг ИСМИНИ киритинг (ҳужжатдагидек):"),
            ("Фамилияси", "Ўқувчининг ФАМИЛИЯСИНИ киритинг (ҳужжатдагидек):"),
            ("Отасининг исми", "Ўқувчининг ОТАСИНИНГ ИСМИНИ киритинг (ҳужжатдагидек):"),
            ("Тўғилган санаси", "Тўғилган куни, ойи ва йилини киритинг (гувоҳномадагидек, мас: 15.08.2012):"),
            ("Метрика рақами", "Туғилганлик ҳақида гувоҳнома (метрика) серияси ва рақамини аниқ ёзинг:"),
            ("Паспорт маълумоти", "Агар паспорти (ИД-картаси) бўлса, серия ва рақамини ёзинг (Бўлмаса 'Йўқ' деб ёзинг):"),
            ("ЖШШИР (ПИНФЛ)", "Ўқувчи ёки ота-онанинг ЖШШИР (паспорт пастидаги 14 хонали ПИНФЛ) кодини аниқ киритинг:"),
            ("Телефон рақами", "Алоқа учун ишлайдиган телефон рақамини киритинг (Мас: +998901234567):"),
            ("Жинси", "Ўқувчининг жинсини танланг (Ўғил бола / Қиз бола):"),
            ("Яшаш манзили", "Паспортдаги рўйхатда турган (прописка) тўлиқ манзилини киритинг:"),
            ("Отасининг И.Ш.", "Отасининг тўлиқ исми, фамилияси ва шарифини киритинг (паспортдагидек):"),
            ("Онасининг И.Ш.", "Онасининг тўлиқ исми, фамилияси ва шарифини киритинг (паспортдагидек):"),
            ("Ота-онасининг иш жойи", "Ота-онасининг расмий иш жойи ва лавозимини киритинг:")
        ]
        cursor.executemany("INSERT INTO questions (field_name, question_text) VALUES (?, ?)", default_questions)
        conn.commit()
        
    conn.close()

def get_all_questions():
    conn = sqlite3.connect("flexible_students.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, field_name, question_text FROM questions ORDER BY id ASC")
    cols = cursor.fetchall()
    conn.close()
    return cols

def add_new_question(field_name, question_text):
    conn = sqlite3.connect("flexible_students.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO questions (field_name, question_text) VALUES (?, ?)", (field_name, question_text))
    conn.commit()
    conn.close()

def save_answer(user_id, question_id, value):
    conn = sqlite3.connect("flexible_students.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO students (user_id) VALUES (?)", (user_id,))
    cursor.execute("""
        INSERT OR REPLACE INTO answers (user_id, question_id, answer_value) 
        VALUES (?, ?, ?)
    """, (user_id, question_id, value))
    conn.commit()
    conn.close()

def check_student_filled(user_id):
    conn = sqlite3.connect("flexible_students.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM answers WHERE user_id = ?", (user_id,))
    answered_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM questions")
    total_questions = cursor.fetchone()[0]
    conn.close()
    return answered_count >= total_questions if total_questions > 0 else False

def get_student_answers(user_id):
    conn = sqlite3.connect("flexible_students.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT q.field_name, a.answer_value 
        FROM questions q
        LEFT JOIN answers a ON q.id = a.question_id AND a.user_id = ?
        ORDER BY q.id ASC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def clear_student_answers(user_id):
    conn = sqlite3.connect("flexible_students.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM answers WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
