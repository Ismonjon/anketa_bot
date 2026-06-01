import csv
import os

def export_students_to_excel():
    import database as db
    rows = db.get_all_students()
    
    file_name = "Oquvchilar_Bazasi.csv"
    
    # Excel устунларга тўғри ажратиши учун delimiter=";" қўшилди
    with open(file_name, mode="w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file, delimiter=";")
        
        # Жадвалнинг устун номлари (Шапка)
        writer.writerow([
            "Т/р", "Телеграм ID", "Исми", "Фамилияси", "Отасининг исми", 
            "Тўғилган санаси", "Метрика рақами", "Паспорт маълумоти", "ЖШШИР (ПИНФЛ)", 
            "Телефон рақами", "Жинси", "Яшаш манзили", "Отасининг И.Ш.", "Онасининг И.Ш.", "Ота-онасининг иш жойи"
        ])
        
        for index, row in enumerate(rows, start=1):
            # Агар базадаги маълумот ичида нуқтали вергул бўлса, Excel бузилмаслиги учун уларни тозалаймиз
            cleaned_row = [str(item).replace(";", " ") if item is not None else "" for item in row]
            
            writer.writerow([
                index, 
                cleaned_row[0],  # user_id
                cleaned_row[1],  # first_name
                cleaned_row[2],  # last_name
                cleaned_row[3],  # middle_name
                cleaned_row[4],  # birth_date
                cleaned_row[5],  # birth_certificate
                cleaned_row[6],  # passport
                f"'{cleaned_row[7]}", # ЖШШИР рақами бузилиб кетмаслиги учун олдига ' қўшилди
                cleaned_row[8],  # phone
                cleaned_row[9],  # gender
                cleaned_row[10], # address
                cleaned_row[11], # father_name
                cleaned_row[12], # mother_name
                cleaned_row[13]  # parents_work
            ])
            
    return file_name
