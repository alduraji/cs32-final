import sqlite3  
from typing import List  
import datetime  
from model import Medicine  
  
conn = sqlite3.connect('medicines.db')  
c = conn.cursor()

  
def create_table():  
    c.execute("""CREATE TABLE IF NOT EXISTS medicines (  
            medicine_name text,  
            dosage text,  
            time text,  
            date_added text,  
            date_taken text,  
            status integer,  
            position integer  
            )""")  
  
  
create_table()  
  
  
def insert_medicine(medicine: Medicine):  
    with conn:  
        c.execute('INSERT INTO medicines VALUES (:medicine_name, :dosage, :time, :date_added, :date_taken, :status, :position)',  
        {'medicine_name': medicine.medicine_name, 'dosage': medicine.dosage, 'time': medicine.time, 'date_added': medicine.date_added,  
         'date_taken': medicine.date_taken, 'status': medicine.status, 'position': medicine.position })  
  
  
def get_all_medicines() -> List[Medicine]:  
    c.execute('select * from medicines ORDER BY time')  
    results = c.fetchall()  
    medicines = []  
    for result in results:  
        medicines.append(Medicine(*result))  
    return medicines  
  
  
def delete_medicine(position):  
    c.execute('select count(*) from medicines')  
    count = c.fetchone()[0]  
  
    with conn:  
        c.execute("DELETE from medicines WHERE position=:position", {"position": position})  
        for pos in range(position + 1, count):  
            change_position(pos, pos - 1, False)  
  
    # Update the position of the remaining medicines  
    medicines = get_all_medicines()  
    for idx, medicine in enumerate(medicines):  
        update_medicine(idx, medicine.medicine_name, medicine.dosage, medicine.time)  
        change_position(medicine.position, idx, False)  
  
    conn.commit() 
  
  
def change_position(old_position: int, new_position: int, commit=True):  
    c.execute('UPDATE medicines SET position = :position_new WHERE position = :position_old',  
                {'position_old': old_position, 'position_new': new_position})  
    if commit:  
        conn.commit()  
  
  
def update_medicine(position: int, medicine_name: str, dosage: str, time: str):  
    with conn:  
        if medicine_name is not None and dosage is not None and time is not None:  
            c.execute('UPDATE medicines SET medicine_name = :medicine_name, dosage = :dosage, time = :time WHERE position = :position',  
                      {'position': position, 'medicine_name': medicine_name, 'dosage': dosage, 'time': time})  
        elif medicine_name is not None:  
            c.execute('UPDATE medicines SET medicine_name = :medicine_name WHERE position = :position',  
                      {'position': position, 'medicine_name': medicine_name})  
        elif dosage is not None:  
            c.execute('UPDATE medicines SET dosage = :dosage WHERE position = :position',  
                      {'position': position, 'dosage': dosage})  
        elif time is not None:  
            c.execute('UPDATE medicines SET time = :time WHERE position = :position',  
                      {'position': position, 'time': time})  
  
  
def take_medicine(position: int):  
    with conn:  
        c.execute('UPDATE medicines SET status = 2, date_taken = :date_taken WHERE position = :position',  
                  {'position': position, 'date_taken': datetime.datetime.now().isoformat()})