import datetime  
  
  
class Medicine:  
    def __init__(self, medicine_name, dosage, time,  
                 date_added=None, date_taken=None,  
                 status=None, position=None):  
        self.medicine_name = medicine_name  
        self.dosage = dosage  
        self.time = time  
        self.date_added = date_added if date_added is not None else datetime.datetime.now().isoformat()  
        self.date_taken = date_taken if date_taken is not None else None  
        self.status = status if status is not None else 1  # 1 = not taken, 2 = taken  
        self.position = position if position is not None else None  
  
    def __repr__(self) -> str:  
        return f"({self.medicine_name}, {self.dosage}, {self.time}, {self.date_added}, {self.date_taken}, {self.status}, {self.position})"