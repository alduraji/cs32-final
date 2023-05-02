import tkinter
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import random
import time
import threading
import datetime
from pync import Notifier


def clear_form():
    supplement_name_entry.delete(0, tkinter.END)
    dosage_entry.delete(0, tkinter.END)
    intake_time_combobox.set("")


def enter_data():
    supplement_name = supplement_name_entry.get()
    supplement_dosage = dosage_entry.get()

    if supplement_name and supplement_dosage:
        intake_time = intake_time_combobox.get()
        mandatory_daily = accept_var.get()

        conn = sqlite3.connect('data.db')
        table_create_query = '''
                              CREATE TABLE IF NOT EXISTS Supplement_Data
                              (supplement_name TEXT, dosage TEXT, intake_time TEXT,
                              mandatory_daily TEXT)
                              '''
        conn.execute(table_create_query)

        data_insert_query = '''
                             INSERT INTO Supplement_Data (supplement_name, dosage, intake_time,
                             mandatory_daily) VALUES (?, ?, ?, ?)
                             '''
        data_insert_tuple = (supplement_name, supplement_dosage, intake_time, mandatory_daily)
        cursor = conn.cursor()
        cursor.execute(data_insert_query, data_insert_tuple)
        conn.commit()
        conn.close()
        show_schedule()
        clear_form()
        tkinter.messagebox.showinfo(title="Success", message="Supplement added successfully")

    else:
        tkinter.messagebox.showwarning(title="Error", message="Supplement name and dosage are required.")


def show_schedule():
    schedule_data.clear()
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    for time_of_day in ["Morning", "Afternoon", "Evening"]:
        cursor.execute(f"SELECT * FROM Supplement_Data WHERE intake_time = '{time_of_day}'")
        supplements = list(cursor.fetchall())

        mandatory_supplements = [supplement for supplement in supplements if supplement[3] == "Yes"]
        other_supplements = [supplement for supplement in supplements if supplement[3] == "No"]

        schedule_data[time_of_day] = mandatory_supplements + random.sample(other_supplements, min(len(other_supplements), 3 - len(mandatory_supplements)))

    conn.close()
    refresh_schedule_view()


def refresh_schedule_view():
    for section in ["Morning", "Afternoon", "Evening"]:
        section_frame = schedule_frames[section]
        for widget in section_frame.winfo_children():
            widget.destroy()

        label = tkinter.Label(section_frame, text=section, font=("Arial", 14))
        label.pack(anchor="w", pady=(10, 5))

        for supplement in schedule_data[section]:
            supplement_label = tkinter.Label(section_frame, text=f"{supplement[0]} ({supplement[1]})", font=("Arial", 12))
            supplement_label.pack(anchor="w", side="left")

            def mark_as_taken(supplement_label=supplement_label):
                supplement_label.config(font=("Arial", 12, "overstrike"))

            supplement_button = tkinter.Button(section_frame, text="✓", command=mark_as_taken)
            supplement_button.pack(side="left", pady=(0, 5))
            sep = ttk.Separator(section_frame, orient="vertical")
            sep.pack(side="left", fill="y", padx=(10, 0))

        sep = ttk.Separator(home_frame, orient="horizontal")
        sep.pack(side="left", fill="x", padx=(10, 10))


def switch_frame(frame_to_show):
    for frame in [home_frame, data_entry_frame, database_viewer_frame, settings_frame]:
        frame.pack_forget()

    frame_to_show.pack()


def update_schedule():
    while True:
        now = time.time()
        next_day = now + 24 * 60 * 60
        time_to_next_day = next_day - now
        time.sleep(time_to_next_day)
        show_schedule()


def show_database():
    database_viewer_tree.delete(*database_viewer_tree.get_children())  # Clear existing items
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Supplement_Data")
    supplements = cursor.fetchall()

    for idx, supplement in enumerate(supplements):
        tag = "odd" if idx % 2 == 1 else None
        database_viewer_tree.insert("", "end", values=supplement, tags=(tag,))

    conn.close()


def on_select(event):
    global current_selected_item
    selected_items = database_viewer_tree.selection()
    if selected_items:
        current_selected_item = database_viewer_tree.item(selected_items[0], "values")


def show_edit_frame():
    if not current_selected_item:
        messagebox.showwarning("No selection", "Please select an entry to edit.")
        return

    edit_window = tkinter.Toplevel()
    edit_window.title("Edit Supplement Data")

    supplement_name_var = tkinter.StringVar(value=current_selected_item[0])
    dosage_var = tkinter.StringVar(value=current_selected_item[1])
    intake_time_var = tkinter.StringVar(value=current_selected_item[2])
    mandatory_daily_var = tkinter.StringVar(value=current_selected_item[3])

    name_label = tkinter.Label(edit_window, text="Supplement Name")
    name_label.grid(row=0, column=0)
    name_entry = tkinter.Entry(edit_window, textvariable=supplement_name_var)
    name_entry.grid(row=1, column=0)

    dosage_label = tkinter.Label(edit_window, text="Dosage")
    dosage_label.grid(row=0, column=1)
    dosage_entry = tkinter.Entry(edit_window, textvariable=dosage_var)
    dosage_entry.grid(row=1, column=1)

    intake_time_label = tkinter.Label(edit_window, text="Intake Time")
    intake_time_label.grid(row=0, column=2)
    intake_time_combobox = ttk.Combobox(edit_window, values=["Morning", "Afternoon", "Evening"], textvariable=intake_time_var)
    intake_time_combobox.grid(row=1, column=2)

    mandatory_daily_label = tkinter.Label(edit_window, text="Mandatory Daily")
    mandatory_daily_label.grid(row=0, column=3)
    mandatory_daily_checkbox = tkinter.Checkbutton(edit_window, text="Yes", variable=mandatory_daily_var, onvalue="Yes", offvalue="No")
    mandatory_daily_checkbox.grid(row=1, column=3)

    def edit_selected_entry():
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()

        new_name = supplement_name_var.get()
        new_dosage = dosage_var.get()
        new_intake_time = intake_time_var.get()
        new_mandatory_daily = mandatory_daily_var.get()

        query = '''
        UPDATE Supplement_Data
        SET supplement_name = ?, dosage = ?, intake_time = ?, mandatory_daily = ?
        WHERE supplement_name = ? AND dosage = ? AND intake_time = ? AND mandatory_daily = ?
        '''
        values = (new_name, new_dosage, new_intake_time, new_mandatory_daily, current_selected_item[0], current_selected_item[1], current_selected_item[2], current_selected_item[3])
        cursor.execute(query, values)
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Entry successfully updated.")
        show_database()
        edit_window.destroy()

    update_button = ttk.Button(edit_window, text="Update", command=edit_selected_entry)
    update_button.grid(row=2, column=1)


def edit_entry():
    if not current_selected_item:
        messagebox.showwarning("No selection", "Please select an entry to edit.")
        return

    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    new_name = current_selected_item[0]
    new_dosage = current_selected_item[1]

    query = '''
    UPDATE Supplement_Data
    SET supplement_name = ?, dosage = ?
    WHERE supplement_name = ? AND dosage = ? AND intake_time = ? AND mandatory_daily = ?
    '''
    values = (new_name, new_dosage, current_selected_item[0], current_selected_item[1], current_selected_item[2], current_selected_item[3])
    cursor.execute(query, values)
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "Entry successfully updated.")
    show_database()


def remove_entry():
    if not current_selected_item:
        messagebox.showwarning("No selection", "Please select an entry to remove.")
        return

    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    query = '''
    DELETE FROM Supplement_Data
    WHERE supplement_name = ? AND dosage = ? AND intake_time = ? AND mandatory_daily = ?
    '''
    values = (current_selected_item[0], current_selected_item[1], current_selected_item[2], current_selected_item[3])
    cursor.execute(query, values)
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "Entry successfully removed.")
    show_database()


def apply_settings():
    global morning_notif_time, afternoon_notif_time, evening_notif_time

    morning_notif_time = morning_time_var.get()
    afternoon_notif_time = afternoon_time_var.get()
    evening_notif_time = evening_time_var.get()

    notif_times_frame.config(text=f"Notification Times: {morning_notif_time}, {afternoon_notif_time}, {evening_notif_time}")

    tkinter.messagebox.showinfo(title="Success", message="Notification times updated successfully")

def send_notifications():
    while True:
        for intake_time, notif_time in [("Morning", morning_notif_time), ("Afternoon", afternoon_notif_time), ("Evening", evening_notif_time)]:
            sec_diff = get_sec_diff_from_now(notif_time)
            if sec_diff > 0:
                time.sleep(sec_diff)
                conn = sqlite3.connect('data.db')
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM Supplement_Data WHERE intake_time = '{intake_time}'")
                supplements = list(cursor.fetchall())
                conn.close()

                mandatory_supplements = [supplement for supplement in supplements if supplement[3] == "Yes"]
                other_supplements = [supplement for supplement in supplements if supplement[3] == "No"]
                selected_supplements = mandatory_supplements + random.sample(other_supplements, min(len(other_supplements), 3 - len(mandatory_supplements)))

                supplement_strs = [f'{supplement[0]} ({supplement[1]})' for supplement in selected_supplements]
                Notifier.notify(f"Time for your {intake_time} supplements:\n" + ', '.join(supplement_strs), title="Supplement Management")


def parse_colon_separated_time(time_str):
    time_components = time_str.split(':')
    return datetime.time(int(time_components[0]), int(time_components[1]))


def get_sec_diff_from_now(time_str):
    now = datetime.datetime.now()
    cur_time = now.time()
    target = parse_colon_separated_time(time_str)

    delta = datetime.timedelta(hours=target.hour - cur_time.hour, minutes=target.minute - cur_time.minute, seconds=-cur_time.second)
    if delta.days < 0:
        delta += datetime.timedelta(days=1)

    return delta.total_seconds()


window = tkinter.Tk()
window.title("Supplement Management")

frame = tkinter.Frame(window)
frame.pack()

# Home Frame
home_frame = tkinter.Frame(frame)

notif_times_frame = tkinter.LabelFrame(home_frame, text="Notification Times")
notif_times_frame.pack(side="bottom", padx=10, pady=10)
morning_notif_time, afternoon_notif_time, evening_notif_time = "08:00", "12:00", "18:00"
notif_times_frame.config(text=f"Notification Times: {morning_notif_time}, {afternoon_notif_time}, {evening_notif_time}")

schedule_frames = {
    "Morning": tkinter.Frame(home_frame),
    "Afternoon": tkinter.Frame(home_frame),
    "Evening": tkinter.Frame(home_frame),
}

schedule_data = {
    "Morning": [],
    "Afternoon": [],
    "Evening": [],
}

for section_frame in schedule_frames.values():
    section_frame.pack(side="left", fill="both", expand=True)

# Data Entry Frame
data_entry_frame = tkinter.Frame(frame)

supplement_info_frame = tkinter.LabelFrame(data_entry_frame, text="Supplement Information")
supplement_info_frame.pack(padx=20, pady=10)

supplement_name_label = tkinter.Label(supplement_info_frame, text="Supplement Name")
supplement_name_label.grid(row=0, column=0)
supplement_name_entry = tkinter.Entry(supplement_info_frame)
supplement_name_entry.grid(row=1, column=0)

dosage_label = tkinter.Label(supplement_info_frame, text="Dosage")
dosage_label.grid(row=0, column=1)
dosage_entry = tkinter.Entry(supplement_info_frame)
dosage_entry.grid(row=1, column=1)

intake_time_label = tkinter.Label(supplement_info_frame, text="Intake Time")
intake_time_label.grid(row=0, column=2)
intake_time_combobox = ttk.Combobox(supplement_info_frame, values=["Morning", "Afternoon", "Evening"])
intake_time_combobox.grid(row=1, column=2)

for widget in supplement_info_frame.winfo_children():
    widget.grid_configure(padx=10, pady=5)

terms_frame = tkinter.LabelFrame(data_entry_frame, text="Mandatory Daily Supplement")
terms_frame.pack(padx=20, pady=10)

accept_var = tkinter.StringVar(value="No")
mandatory_daily_check = tkinter.Checkbutton(terms_frame, text="Is this a mandatory daily supplement?",
                                            variable=accept_var, onvalue="Yes", offvalue="No")
mandatory_daily_check.grid(row=0, column=0)

entry_button = tkinter.Button(data_entry_frame, text="Submit", command=enter_data)
entry_button.pack(padx=20, pady=10)

# Database Viewer Frame
database_viewer_frame = tkinter.Frame(frame)

columns = ("supplement_name", "dosage", "intake_time", "mandatory_daily")
database_viewer_tree = ttk.Treeview(database_viewer_frame, columns=columns, show="headings", selectmode="browse")
for column in columns:
    database_viewer_tree.heading(column, text=column.capitalize())

database_viewer_tree.tag_configure("odd", background="#f2f2f2")

database_viewer_tree.pack(padx=10, pady=10, fill="both", expand=True)
database_viewer_scrollbar = ttk.Scrollbar(database_viewer_frame, orient="vertical", command=database_viewer_tree.yview)
database_viewer_scrollbar.pack(side="right", fill="y")
database_viewer_tree["yscrollcommand"] = database_viewer_scrollbar.set

edit_button = ttk.Button(database_viewer_frame, text="Edit", command=show_edit_frame)
edit_button.pack(side="left", padx=(10, 10), pady=(10, 10))

delete_button = ttk.Button(database_viewer_frame, text="Remove", command=remove_entry)
delete_button.pack(side="left", padx=(0, 10), pady=(10, 10))

current_selected_item = None
database_viewer_tree.bind("<<TreeviewSelect>>", on_select)

# Settings Frame
settings_frame = tkinter.Frame(frame)
morning_time_label = tkinter.Label(settings_frame, text='Morning Notification Time (HH:MM)')
morning_time_label.grid(row=0, column=0)
morning_time_var = tkinter.StringVar(value="08:00")  # Default morning time
morning_time_entry = tkinter.Entry(settings_frame, textvariable=morning_time_var)
morning_time_entry.grid(row=1, column=0)

afternoon_time_label = tkinter.Label(settings_frame, text='Afternoon Notification Time (HH:MM)')
afternoon_time_label.grid(row=0, column=1)
afternoon_time_var = tkinter.StringVar(value="12:00")  # Default afternoon time
afternoon_time_entry = tkinter.Entry(settings_frame, textvariable=afternoon_time_var)
afternoon_time_entry.grid(row=1, column=1)

evening_time_label = tkinter.Label(settings_frame, text='Evening Notification Time (HH:MM)')
evening_time_label.grid(row=0, column=2)
evening_time_var = tkinter.StringVar(value="18:00")  # Default evening time
evening_time_entry = tkinter.Entry(settings_frame, textvariable=evening_time_var)
evening_time_entry.grid(row=1, column=2)

for widget in settings_frame.winfo_children():
    widget.grid_configure(padx=10, pady=5)

apply_btn = tkinter.Button(settings_frame, text="Apply", command=apply_settings)
apply_btn.grid(row=2, column=1)

# Navigation Buttons
navigation_frame = tkinter.Frame(frame)
navigation_frame.pack(side="bottom")

home_button = tkinter.Button(navigation_frame, text="Home", command=lambda: switch_frame(home_frame))
home_button.pack(side="left", padx=(0, 20))

data_entry_button = tkinter.Button(navigation_frame, text="Enter data", command=lambda: switch_frame(data_entry_frame))
data_entry_button.pack(side="left")

database_viewer_button = tkinter.Button(navigation_frame, text="Database Viewer",
                                        command=lambda: [switch_frame(database_viewer_frame), show_database()])
database_viewer_button.pack(side="left", padx=(20, 0))

settings_button = tkinter.Button(navigation_frame, text="Settings", command=lambda: switch_frame(settings_frame))
settings_button.pack(side="left", padx=(20, 0))

# Show Home Frame and Schedule List
switch_frame(home_frame)
show_schedule()

schedule_updater_thread = threading.Thread(target=update_schedule, daemon=True)
schedule_updater_thread.start()

notification_thread = threading.Thread(target=send_notifications, daemon=True)
notification_thread.start()

window.mainloop()