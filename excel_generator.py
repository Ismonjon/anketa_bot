import csv
import sqlite3

def export_students_to_excel():
    conn = sqlite3.connect("flexible_students.db")
    cursor = conn.cursor()
    
    # 1. Барча саволларни устун номи сифатида оламиз
    cursor.execute("SELECT id, field_name FROM questions ORDER BY id ASC")
    questions = cursor.fetchall()
    
    # Excel Шапкаси (устунлари)
    header = ["Т/р", "Телеграм ID"] + [q[1] for q in questions]
    
    # 2. Барча ўқувчиларни оламиз
    cursor.execute("SELECT user_id FROM students ORDER BY created_at ASC")
    students = cursor.fetchall()
    
    file_name = "Oquvchilar_Umuniy_Bazasi.csv"
    
    with open(file_name, mode="w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(header)
        
        for index, (user_id,) in enumerate(students, start=1):
            row_data = [index, user_id]
            
            # Ҳар бир ўқувчи учун барча саволларга берилган жавобларни устун бўйича терамиз
            for q_id, _ in questions:
                cursor.execute("SELECT answer_value FROM answers WHERE user_id = ? AND question_id = ?", (user_id, q_id))
                ans = cursor.fetchone()
                val = ans[0] if ans else ""
                
                # ЖШШИР ёки рақамлар бузилмаслиги учун
                if len(val) >= 10 and val.isdigit():
                    val = f"'{val}"
                
                row_data.append(str(val).replace(";", " "))
                
            writer.writerow(row_data)
            
    conn.close()
    return file_name
