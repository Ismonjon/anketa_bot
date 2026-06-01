import csv
import os

def export_students_to_excel():
    import database as db
    rows = db.get_all_students()
    
    file_name = "Oquvchilar_Bazasi.csv"
    
    with open(file_name, mode="w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        
        # Жадвалнинг устун номлари (Шапка)
        writer.writerow([
            "Т/р", "Телеграм ID", "Исми", "Фамилияси", "Отасининг исми", 
            "Тўғилган санаси", "Метрика рақами", "Паспорт маълумоти", "ЖШШИР (ПИНФЛ)", 
            "Телефон рақами", "Жинси", "Яшаш манзили", "Отасининг И.Ш.", "Онасининг И.Ш.", "Ота-онасининг иш жойи", "Рўйхатдан ўтган вақти"
        ])
        
        for index, row in enumerate(rows, start=1):
            # Базадаги қаторларни чиройли тартибда ёзамиз
            writer.writerow([
                index, row[0], row[1], row[2], row[3], 
                row[4], row[5], row[6], f"'{row[7]}", # ЖШШИР рақамлари Excelда бузилиб кетмаслиги учун олдига ' қўшилади
                row[8], row[9], row[10], row[11], row[12], row[13], row[14]
            ])
            
    return file_name
