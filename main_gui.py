import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import subprocess
import os
import json
from timetable_management import add_class_to_timetable
import pandas as pd
from datetime import datetime
from tkcalendar import DateEntry
import csv
import winsound

def play_click_sound():
    winsound.PlaySound("click.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
def play_click2_sound():
    winsound.PlaySound("click2.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
def play_select_sound():
    winsound.PlaySound("select.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)

attendance_enabled = False  # Initial state is OFF
btn_toggle = None  # Declare globally

def toggle_attendance_mode():
    global attendance_enabled,btn_toggle
    attendance_enabled = not attendance_enabled
    if attendance_enabled:
        messagebox.showinfo("Attendance Mode", "Attendance Mode: ON")
        btn_toggle.config(text="Turn OFF Attendance Mode", bg="green")
    else:
        messagebox.showwarning("Attendance Mode", "Attendance Mode: OFF")
        btn_toggle.config(text="Turn ON Attendance Mode", bg="red")

def check_and_mark_attendance():
    if attendance_enabled:
        play_select_sound()
        mark_attendance()
    else:
        play_select_sound()
        messagebox.showerror("Access Denied", "Attendance Mode is OFF. Please enable it first.")


def check_admin_credentials(username, password):
    try:
        with open("admin_credentials.csv", mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["username"] == username and row["password"] == password:
                    return True
        return False
    except FileNotFoundError:
        messagebox.showerror("Error", "Credentials file not found!")
        return False

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
# Student data folder
STUDENT_DATA_FOLDER = "student_data"

def verify_admin_login(username, password):
    """Verify if the entered username and password match the admin credentials."""
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

def student_exists(student_id, student_name):
    """Check if the student is registered by matching ID and name."""
    student_folder = os.path.join(STUDENT_DATA_FOLDER, f"{student_id}_{student_name}")
    return os.path.exists(student_folder) and len(os.listdir(student_folder)) > 0

def open_main_gui():
    """Opens the main GUI window after successful login."""
    login_window.withdraw()

    root = tk.Tk()
    root.title("Face Attendance System")
    root.state('zoomed')  # Maximizes the window (Windows only)
    root.configure(bg="#E8F5E9")

    # Title Label
    title = tk.Label(root, text="Faculty DashBoard:", bg="#E8F5E9", fg="#1B5E20", font=("Segoe UI", 34, "bold"))
    title.pack(pady=50)

    # Buttons
    btn_mark = tk.Button(root, text="Mark Student Attendance", font=("Segoe UI", 12), bg="#43A047", fg="#ffffff",cursor="hand2", command=lambda:[play_select_sound(),check_and_mark_attendance()], width=25)
    btn_mark.pack(pady=10)

    btn_view = tk.Button(root, text="View Student Attendance", font=("Segoe UI", 12), bg="#43A047", fg="#ffffff",cursor="hand2", command=lambda:[play_click2_sound(),open_student()], width=25)
    btn_view.pack(pady=10)

    # Toggle Button
    global btn_toggle
    btn_toggle = tk.Button(root, text="Turn ON Attendance Mode", font=("Segoe UI", 12),bg="red", fg="#ffffff", cursor="hand2",command=toggle_attendance_mode, width=25)
    btn_toggle.pack(pady=10)

    btn_timetable = tk.Button(root, text="Faculty Timetable", font=("Segoe UI", 12), bg="#43A047", fg="#ffffff",cursor="hand2", command=lambda:[play_click2_sound(),view_timetable()], width=25)
    btn_timetable.pack(pady=10)

    btn_exit = tk.Button(root, text="Log Out", font=("Segoe UI", 12), bg="#D32F2F", fg="#ffffff",cursor="hand2", command=lambda:[play_click_sound(),root.destroy(), admin_login()], width=25)
    btn_exit.pack(pady=20)

    root.mainloop()

def view_timetable():
    timetable_file = "timetable.json"
    if not os.path.exists(timetable_file):
        messagebox.showinfo("Timetable", "No timetable found.")
        return

    with open(timetable_file, "r") as f:
        timetable_data = json.load(f)

    classes = timetable_data.get("classes", [])
    classes = sorted(classes, key=lambda cls: cls.get("time_slot", ""))  # Sort by time

    view_window = tk.Toplevel(login_window)
    view_window.title("View Timetable")
    view_window.state('zoomed')  # Maximizes the window (Windows only)
    view_window.configure(bg="#1e1e2f")

    search_var = tk.StringVar()
    time_filter_var = tk.StringVar(value="All Times")

    def filter_classes():
        search_text = search_var.get().lower()
        selected_time = time_filter_var.get()

        for item in tree.get_children():
            tree.delete(item)

        for cls in classes:
            if (search_text in cls.get("class_name", "").lower()) and (selected_time == "All Times" or cls.get("time_slot", "") == selected_time):
                class_name = cls.get("class_name", "N/A")
                time_slot = cls.get("time_slot", "N/A")
                students = ", ".join(cls.get("students", []))
                faculty = subject_faculty_map.get(class_name, "Substitute")
                tree.insert("", tk.END, values=(class_name, faculty, time_slot, students))


    # Top Frame for search and filter
    top_frame = tk.Frame(view_window, bg="#1e1e2f")
    top_frame.pack(pady=10)

    # Search Bar
    tk.Label(top_frame, text="Search Class:", bg="#1e1e2f", fg="white").pack(side=tk.LEFT, padx=5)
    search_entry = tk.Entry(top_frame, textvariable=search_var)
    search_entry.pack(side=tk.LEFT, padx=5)

    search_button = tk.Button(top_frame, text="Search", bg="#2d89ef", fg="white", command=filter_classes)
    search_button.pack(side=tk.LEFT, padx=5)

    # Reset Button
    reset_button = tk.Button(top_frame, text="Reset", bg="#6c757d", fg="white", command=lambda: [search_var.set(""), time_filter_var.set("All Times"), filter_classes()])
    reset_button.pack(side=tk.LEFT, padx=5)

    # Time Slot Filter
    tk.Label(top_frame, text="Filter by Time:", bg="#1e1e2f", fg="white").pack(side=tk.LEFT, padx=10)

    time_slots = ["All Times"] + sorted(list({cls.get("time_slot", "") for cls in classes}))
    time_filter_dropdown = ttk.Combobox(top_frame, textvariable=time_filter_var, values=time_slots, state="readonly")
    time_filter_dropdown.pack(side=tk.LEFT, padx=5)
    time_filter_dropdown.bind("<<ComboboxSelected>>", lambda event: filter_classes())

    # Table
    columns = ("Class Name", "Faculty", "Time Slot", "Students")
    tree = ttk.Treeview(view_window, columns=columns, show="headings")
    tree.heading("Class Name", text="Class Name")
    tree.heading("Faculty", text="Faculty")
    tree.heading("Time Slot", text="Time Slot")
    tree.heading("Students", text="Students")


    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", background="#2b2b40", fieldbackground="#2b2b40", foreground="white")
    style.configure("Treeview.Heading", background="#404060", foreground="white", font=("Segoe UI", 11, "bold"))

    # Load faculty assignments from admin_credentials.csv
    faculty_file = "admin_credentials.csv"
    subject_faculty_map = {}

    if os.path.exists(faculty_file):
        with open(faculty_file, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) == 3:
                    username, password, subject = row
                    subject_faculty_map[subject.strip()] = username.strip()


    def populate_table():
        for item in tree.get_children():
            tree.delete(item)
        for cls in classes:
            class_name = cls.get("class_name", "N/A")
            time_slot = cls.get("time_slot", "N/A")
            students = ", ".join(cls.get("students", []))
            faculty = subject_faculty_map.get(class_name, "Substitute")
            tree.insert("", tk.END, values=(class_name, faculty, time_slot, students))


    populate_table()
    tree.pack(expand=True, fill="both", padx=10, pady=10)


def open_hod_gui():
    """Opens the main GUI window after successful login."""
    login_window.withdraw()
    
    root = tk.Tk()
    root.title("Face Attendance System")
    root.state('zoomed')  # Maximizes the window (Windows only)
    root.configure(bg="#E8F5E9")

    title = tk.Label(root, text="Coordinator Page:", bg="#E8F5E9", fg="#1B5E20", font=("Segoe UI", 34, "bold"))
    title.pack(pady=30)

    btn_register = tk.Button(root, text="Register Student", font=("Segoe UI", 12), bg="#43A047", fg="#ffffff",cursor="hand2", command=lambda:[play_select_sound(),register_student()], width=25)
    btn_register.pack(pady=10)

    btn_train = tk.Button(root, text="Train Model", font=("Segoe UI", 12), bg="#43A047", fg="#ffffff",cursor="hand2", command=lambda:[play_click2_sound(),train_model()], width=25)
    btn_train.pack(pady=10)

    btn_register = tk.Button(root, text="Register Faculty", font=("Segoe UI", 12), bg="#43A047", fg="#ffffff",cursor="hand2", command=lambda:[play_click2_sound(),add_new_faculty()], width=25)
    btn_register.pack(pady=10)

    btn_view = tk.Button(root, text="View Faculty", font=("Segoe UI", 12), bg="#43A047", fg="#ffffff",cursor="hand2",command=lambda:[play_click2_sound(),view_faculty_data()], width=25)
    btn_view.pack(pady=10)

    btn_timetable = tk.Button(root, text="Manage Timetable", font=("Segoe UI", 12), bg="#43A047", fg="#ffffff",cursor="hand2", command=lambda:[play_click2_sound(),admin_panel()], width=25)
    btn_timetable.pack(pady=10)

    btn_view = tk.Button(root, text="View Attendance", font=("Segoe UI", 12), bg="#43A047", fg="#ffffff",cursor="hand2", command=lambda:[play_click2_sound(),open_student()], width=25)
    btn_view.pack(pady=10)

    btn_exit = tk.Button(root, text="Log Out", font=("Segoe UI", 12), bg="#D32F2F", fg="#ffffff",cursor="hand2", command=lambda:[play_click_sound(),root.destroy(), admin_login()], width=25)
    btn_exit.pack(pady=20)

    root.mainloop()


def load_all_subjects():
    timetable_file = "timetable.json"
    if not os.path.exists(timetable_file):
        messagebox.showerror("Error", "Timetable file not found.")
        return []

    with open(timetable_file, "r") as file:
        data = json.load(file)

    # Collect unique subjects
    subjects = list({cls["class_name"] for cls in data.get("classes", [])})
    return subjects

def add_new_faculty():
    faculty_window = tk.Toplevel()
    faculty_window.title("Register New Faculty")
    faculty_window.state('zoomed')  # Maximizes the window (Windows only)
    faculty_window.configure(bg="#1e1e2f")

    # Username Entry
    tk.Label(faculty_window, text="Username:", bg="#1e1e2f", fg="white", font=("Segoe UI", 12)).pack(pady=(10, 0))
    username_entry = tk.Entry(faculty_window, font=("Segoe UI", 12))
    username_entry.pack(pady=5)

    # Password Entry
    tk.Label(faculty_window, text="Password:", bg="#1e1e2f", fg="white", font=("Segoe UI", 12)).pack(pady=(10, 0))
    password_entry = tk.Entry(faculty_window, font=("Segoe UI", 12), show="*")
    password_entry.pack(pady=5)

    # Confirm Password Entry
    tk.Label(faculty_window, text="Confirm Password:", bg="#1e1e2f", fg="white", font=("Segoe UI", 12)).pack(pady=(10, 0))
    confirm_password_entry = tk.Entry(faculty_window, font=("Segoe UI", 12), show="*")
    confirm_password_entry.pack(pady=5)

    # Show/Hide Password Checkbox
    show_password = tk.BooleanVar()
    def toggle_password():
        show = "" if show_password.get() else "*"
        password_entry.config(show=show)
        confirm_password_entry.config(show=show)

    tk.Checkbutton(faculty_window, text="Show Password", variable=show_password, command=toggle_password,
                   bg="#1e1e2f", fg="white", font=("Segoe UI", 10)).pack(pady=(5, 10))

    # Subject Selection Dropdown
    tk.Label(faculty_window, text="Assign Subject:", bg="#1e1e2f", fg="white", font=("Segoe UI", 12)).pack(pady=(10, 0))
    subject_var = tk.StringVar()
    subjects = load_all_subjects()
    if subjects:
        subject_var.set(subjects[0])
    subject_dropdown = tk.OptionMenu(faculty_window, subject_var, *subjects)
    subject_dropdown.pack(pady=5)

    # Submit Handler
    def submit():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        confirm_password = confirm_password_entry.get().strip()
        subject = subject_var.get().strip()

        if not username or not password or not confirm_password or not subject:
            messagebox.showerror("Error", "All fields are required.", parent=faculty_window)
            return

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.", parent=faculty_window)
            return

        filename = "admin_credentials.csv"
        file_exists = os.path.isfile(filename)

        # Check for duplicate usernames
        if file_exists:
            with open(filename, mode="r", newline="") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row["username"] == username:
                        messagebox.showerror("Error", f"Username '{username}' already exists.", parent=faculty_window)
                        return

        # Save new credentials and subject
        with open(filename, mode="a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["username", "password", "subject"])
            if not file_exists:
                writer.writeheader()
            writer.writerow({"username": username, "password": password, "subject": subject})

        messagebox.showinfo("Success", f"Faculty '{username}' registered successfully!", parent=faculty_window)
        faculty_window.destroy()

    tk.Button(faculty_window, text="Register", font=("Segoe UI", 12), bg="#2d89ef", fg="white", command=lambda:[play_click2_sound(),submit()]).pack(pady=15)


CREDENTIALS_FILE = "admin_credentials.csv"

def view_faculty_data():
    def load_data(filter_subject=None):
        faculty_table.delete(*faculty_table.get_children())
        if not os.path.exists(CREDENTIALS_FILE):
            return
        with open(CREDENTIALS_FILE, mode="r", newline="") as file:
            reader = csv.DictReader(file)
            data = list(reader)
            data.sort(key=lambda x: x['username'].lower())

        for row in data:
            if filter_subject and row.get('subject', '').lower() != filter_subject.lower():
                continue
            faculty_table.insert("", "end", values=(row['username'], row['password'], row.get('subject', 'N/A')))

    def delete_faculty():
        selected = faculty_table.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a faculty to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this faculty?")
        if not confirm:
            return

        values = faculty_table.item(selected[0], "values")
        username = values[0]

        with open(CREDENTIALS_FILE, "r", newline="") as f:
            rows = list(csv.DictReader(f))

        with open(CREDENTIALS_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=['username', 'password', 'subject'])
            writer.writeheader()
            for row in rows:
                if row['username'] != username:
                    writer.writerow(row)

        load_data()
        messagebox.showinfo("Deleted", f"Faculty {username} deleted successfully.")

    def edit_faculty():
        selected = faculty_table.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a faculty to edit.")
            return

        values = faculty_table.item(selected[0], "values")
        old_username = values[0]
        old_password = values[1]
        old_subject = values[2]

        edit_win = tk.Toplevel()
        edit_win.title("Edit Faculty Details")
        edit_win.geometry("300x350")
        edit_win.configure(bg="#1e1e2f")

        tk.Label(edit_win, text="Username:", bg="#1e1e2f", fg="white").pack(pady=(10, 0))
        username_entry = tk.Entry(edit_win)
        username_entry.insert(0, old_username)
        username_entry.pack(pady=5)

        tk.Label(edit_win, text="Password:", bg="#1e1e2f", fg="white").pack(pady=(10, 0))
        password_entry = tk.Entry(edit_win, show="*")
        password_entry.insert(0, old_password)
        password_entry.pack(pady=5)

        tk.Label(edit_win, text="Subject:", bg="#1e1e2f", fg="white").pack(pady=(10, 0))
        subject_entry = tk.Entry(edit_win)
        subject_entry.insert(0, old_subject)
        subject_entry.pack(pady=5)

        def save_changes():
            new_username = username_entry.get().strip()
            new_password = password_entry.get().strip()
            new_subject = subject_entry.get().strip()

            if not new_username or not new_password or not new_subject:
                messagebox.showerror("Error", "All fields are required.", parent=edit_win)
                return

            with open(CREDENTIALS_FILE, "r", newline="") as f:
                rows = list(csv.DictReader(f))

            with open(CREDENTIALS_FILE, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=['username', 'password', 'subject'])
                writer.writeheader()
                for row in rows:
                    if row['username'] == old_username:
                        writer.writerow({'username': new_username, 'password': new_password, 'subject': new_subject})
                    else:
                        writer.writerow(row)

            load_data()
            messagebox.showinfo("Updated", "Faculty details updated successfully.", parent=edit_win)
            edit_win.destroy()

        tk.Button(edit_win, text="Save Changes", command=save_changes, bg="#2d89ef", fg="white").pack(pady=20)

    def live_search(*args):
        query = search_var.get().lower()
        faculty_table.delete(*faculty_table.get_children())
        with open(CREDENTIALS_FILE, mode="r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if query in row['username'].lower() or query in row.get('subject', '').lower():
                    faculty_table.insert("", "end", values=(row['username'], row['password'], row.get('subject', 'N/A')))

    def on_subject_filter_change(event):
        selected_subject = subject_filter.get()
        if selected_subject == "All":
            load_data()
        else:
            load_data(filter_subject=selected_subject)

    view_window = tk.Toplevel()
    view_window.title("View Faculty Data")
    view_window.state('zoomed')  # Maximizes the window (Windows only)
    view_window.configure(bg="#1e1e2f")

    top_frame = tk.Frame(view_window, bg="#1e1e2f")
    top_frame.pack(fill="x", pady=10)

    search_var = tk.StringVar()
    search_var.trace_add("write", live_search)
    tk.Entry(top_frame, textvariable=search_var, width=30, font=("Segoe UI", 10)).pack(side="left", padx=5)

    # Subject filter dropdown
    subject_filter = ttk.Combobox(top_frame, state="readonly")
    subjects = ["All"]
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, mode="r", newline="") as file:
            reader = csv.DictReader(file)
            subject_set = sorted(set(row.get('subject', '') for row in reader if row.get('subject')))
            subjects.extend(subject_set)
    subject_filter['values'] = subjects
    subject_filter.current(0)
    subject_filter.bind("<<ComboboxSelected>>", on_subject_filter_change)
    subject_filter.pack(side="left", padx=5)

    faculty_table = ttk.Treeview(view_window, columns=("Username", "Password", "Subject"), show="headings")
    faculty_table.heading("Username", text="Username")
    faculty_table.heading("Password", text="Password")
    faculty_table.heading("Subject", text="Subject")
    faculty_table.column("Username", width=180)
    faculty_table.column("Password", width=180)
    faculty_table.column("Subject", width=180)
    faculty_table.pack(expand=True, fill="both", pady=10)

    btn_frame = tk.Frame(view_window, bg="#1e1e2f")
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Delete", command=delete_faculty, bg="red", fg="white").pack(side="left", padx=5)
    tk.Button(btn_frame, text="Edit Details", command=edit_faculty, bg="#2d89ef", fg="white").pack(side="left", padx=5)

    load_data()
    view_window.mainloop()


def open_student():
    student_id = simpledialog.askstring("Student ID", "Enter Student ID:")
    if not student_id:
        return

    student_name = simpledialog.askstring("Student Name", "Enter Student Name:")
    if not student_name:
        return

    if student_exists(student_id, student_name):
        messagebox.showinfo("Login Successful", "Student found.")
        view_student_attendance(student_id, student_name)
    else:
        messagebox.showerror("Login Failed", "Student not registered!")

def admin_login():
    """Creates the login window to verify admin credentials."""
    global login_window
    login_window = tk.Tk()
    login_window.title("Login")
    login_window.state('zoomed')  # Maximizes the window (Windows only)
    login_window.configure(bg="#BBDEFB")

    label_login = tk.Label(login_window, text="Welcome:", bg="#BBDEFB", fg="#0D47A1", font=("Segoe UI", 34))
    label_login.pack(pady=20)

    def open_admin_login():
        login_window.withdraw()
        
        admin_login_window = tk.Toplevel()
        admin_login_window.title("Faculty Login")
        admin_login_window.state('zoomed')  # Maximizes the window (Windows only)
        admin_login_window.configure(bg="#FFF8E1")

        label_login = tk.Label(admin_login_window, text="Faculty Login:", bg="#FFF8E1", fg="#4E342E", font=("Segoe UI", 34))
        label_login.pack(pady=20)

        label_username = tk.Label(admin_login_window, text="Username:", bg="#FFF8E1", fg="#F9A825", font=("Segoe UI", 18))
        label_username.pack(pady=10)
        
        entry_username = tk.Entry(admin_login_window, font=("Segoe UI", 18))
        entry_username.pack(pady=5)

        label_password = tk.Label(admin_login_window, text="Password:", bg="#FFF8E1", fg="#F9A825", font=("Segoe UI", 18))
        label_password.pack(pady=10)

        entry_password = tk.Entry(admin_login_window, show="*", font=("Segoe UI", 18))
        entry_password.pack(pady=5)

        def login():
            username = entry_username.get()
            password = entry_password.get()
            
            if check_admin_credentials(username, password):
                messagebox.showinfo("Login Successful", "Welcome Faculty!")
                admin_login_window.destroy()
                open_main_gui()
            else:
                messagebox.showerror("Login Failed", "Invalid username or password!")

        btn_login = tk.Button(admin_login_window, text="Login", font=("Segoe UI", 12), bg="#D84315", fg="#ffffff", command=lambda:[play_click2_sound(),login()], width=20)
        btn_login.pack(pady=20)

    def open_hod_login():
        login_window.withdraw()
        
        admin_login_window = tk.Toplevel()
        admin_login_window.title("Coordinator Login")
        admin_login_window.state('zoomed')  # Maximizes the window (Windows only)
        admin_login_window.configure(bg="#FFF8E1")

        label_login = tk.Label(admin_login_window, text="Coordinator Login:", bg="#FFF8E1", fg="#4E342E", font=("Segoe UI", 34))
        label_login.pack(pady=20)

        label_username = tk.Label(admin_login_window, text="Username:", bg="#FFF8E1", fg="#F9A825", font=("Segoe UI", 18))
        label_username.pack(pady=10)
        
        entry_username = tk.Entry(admin_login_window, font=("Segoe UI", 18))
        entry_username.pack(pady=5)

        label_password = tk.Label(admin_login_window, text="Password:", bg="#FFF8E1", fg="#F9A825", font=("Segoe UI", 18))
        label_password.pack(pady=10)

        entry_password = tk.Entry(admin_login_window, show="*", font=("Segoe UI", 18))
        entry_password.pack(pady=5)

        def login():
            username = entry_username.get()
            password = entry_password.get()
            
            if verify_admin_login(username, password):
                messagebox.showinfo("Login Successful", "Welcome Coordinator!")
                admin_login_window.destroy()
                open_hod_gui()
            else:
                messagebox.showerror("Login Failed", "Invalid username or password!")

        btn_login = tk.Button(admin_login_window, text="Login", font=("Segoe UI", 12), bg="#D84315", fg="#ffffff", command=lambda:[play_click2_sound(),login()], width=20)
        btn_login.pack(pady=20)

    def open_student_login():
        login_window.withdraw()
        
        student_login_window = tk.Toplevel()
        student_login_window.title("Student Login")
        student_login_window.state('zoomed')  # Maximizes the window (Windows only)
        student_login_window.configure(bg="#FFF8E1")

        label_login = tk.Label(student_login_window, text="Student Login:", bg="#FFF8E1", fg="#4E342E", font=("Segoe UI", 34))
        label_login.pack(pady=20)

        label_student_id = tk.Label(student_login_window, text="Student ID:", bg="#FFF8E1", fg="#F9A825", font=("Segoe UI", 18))
        label_student_id.pack(pady=10)
        
        entry_student_id = tk.Entry(student_login_window, font=("Segoe UI", 18))
        entry_student_id.pack(pady=5)

        label_student_name = tk.Label(student_login_window, text="Student Name:", bg="#FFF8E1", fg="#F9A825", font=("Segoe UI", 18))
        label_student_name.pack(pady=10)

        entry_student_name = tk.Entry(student_login_window, font=("Segoe UI", 18))
        entry_student_name.pack(pady=5)

        def login():
            student_id = entry_student_id.get()
            student_name = entry_student_name.get()
    
            if student_exists(student_id, student_name):
                messagebox.showinfo("Login Successful", f"Welcome, {student_name}!")
                student_login_window.destroy()
                student_menu(student_id, student_name)  # <<< New Menu
            else:
                messagebox.showerror("Login Failed", "Student not registered!")

        btn_login = tk.Button(student_login_window, text="Login", font=("Segoe UI", 12), bg="#D84315", fg="#ffffff", command=lambda:[play_click2_sound(),login()], width=20)
        btn_login.pack(pady=20)

    btn_admin = tk.Button(login_window, text="Coordinator Login", font=("Segoe UI", 12), bg="#1976D2", fg="#ffffff", command=lambda:[play_click2_sound(),open_hod_login()], width=20)
    btn_admin.pack(pady=10)

    btn_admin = tk.Button(login_window, text="Faculty Login", font=("Segoe UI", 12), bg="#1976D2", fg="#ffffff", command=lambda:[play_click2_sound(),open_admin_login()], width=20)
    btn_admin.pack(pady=10)

    btn_student = tk.Button(login_window, text="Student Login", font=("Segoe UI", 12), bg="#1976D2", fg="#ffffff", command=lambda:[play_click2_sound(),open_student_login()], width=20)
    btn_student.pack(pady=10)

    btn_exit = tk.Button(login_window, text="Exit", font=("Segoe UI", 12), bg="#E53935", fg="#ffffff",cursor="hand2", command=lambda:[play_click_sound(),login_window.quit()], width=25)
    btn_exit.pack(pady=20)

    login_window.mainloop()

def register_student():
    try:
        subprocess.run(["python", "register_student.py"])
    except Exception as e:
        messagebox.showerror("Error", str(e))

def train_model():
    try:
        subprocess.run(["python", "test_train.py"])
    except Exception as e:
        messagebox.showerror("Error", str(e))

def mark_attendance():
    try:
        subprocess.run(["python", "recognize_and_mark_test.py"])
    except Exception as e:
        messagebox.showerror("Error", str(e))

def student_menu(student_id, student_name):
    """Student Menu: View Attendance or Mark Attendance"""
    menu_window = tk.Toplevel()
    menu_window.title("Student Menu")
    menu_window.state('zoomed')  # Maximizes the window (Windows only)
    menu_window.configure(bg="#E8F5E9")

    tk.Label(menu_window, text=f"Welcome, {student_name}", bg="#E8F5E9", fg="#1B5E20", font=("Segoe UI", 34, "bold")).pack(pady=20)

    btn_mark = tk.Button(menu_window, text="Mark Attendance", font=("Segoe UI", 12), bg="#43A047", fg="#ffffff",cursor="hand2",command=lambda:[play_select_sound(),check_and_mark_attendance()], width=25)
    btn_mark.pack(pady=10)

    btn_view = tk.Button(menu_window, text="View My Attendance", font=("Segoe UI", 12), bg="#43A047", fg="#ffffff",cursor="hand2",command=lambda: [play_click2_sound(),view_student_attendance(student_id, student_name)], width=25)
    btn_view.pack(pady=10)

    btn_view = tk.Button(menu_window, text="View TimeTable", font=("Segoe UI", 12), bg="#43A047", fg="#ffffff",cursor="hand2",command=lambda:[play_click2_sound(),view_timetable()], width=25)
    btn_view.pack(pady=10)

    btn_exit = tk.Button(menu_window, text="Log Out", font=("Segoe UI", 12), bg="#D32F2F", fg="#ffffff",cursor="hand2", command=lambda:[play_click_sound(),menu_window.destroy(),admin_login()], width=25)
    btn_exit.pack(pady=20)


def view_student_attendance(student_id, student_name):
    """View student's own attendance records"""
    attendance_window = tk.Toplevel()
    attendance_window.title("My Attendance")
    attendance_window.state('zoomed')  # Maximizes the window (Windows only)
    attendance_window.configure(bg="#1e1e2f")

    # Get all Attendance files
    files = [f for f in os.listdir("attendance") if f.startswith("Attendance_") and f.endswith(".csv")]

    all_records = []

    for file in files:
        try:
            # Extract the date from the filename (e.g., "attendance_2025-04-26.csv" → "2025-04-26")
            date_str = file.split('_')[1].replace('.csv', '')

            df = pd.read_csv(os.path.join("attendance", file))
            # Add the extracted date as a new column
            df['Date'] = date_str

            if 'Subject' not in df.columns:
                df["Subject"] = "Unknown"
            
            # Filter records based on student ID and name
            student_records = df[(df["ID"] == int(student_id)) & (df["Name"] == student_name)]
            all_records.append(student_records)
        except Exception as e:
            print(f"Error reading {file}: {e}")

    if all_records:
        full_data = pd.concat(all_records)
    else:
        full_data = pd.DataFrame(columns=["ID", "Name", "Time", "Subject", "Date"])

    search_var = tk.StringVar()
    subject_var = tk.StringVar(value="All Subjects")
    date_var = tk.StringVar(value="All Dates")

    def filter_attendance():
        query = search_var.get().lower()
        selected_subject = subject_var.get()
        selected_date = date_var.get()

        # Clear the existing treeview content
        for item in tree.get_children():
            tree.delete(item)

        # Filter records based on the user's search query, selected subject, and selected date
        for index, row in full_data.iterrows():
            subject = row["Subject"]
            date = row["Date"]
            if (query in subject.lower() or query in row["Time"].lower()) and \
               (selected_subject == "All Subjects" or subject == selected_subject) and \
               (selected_date == "All Dates" or date == selected_date):
                tree.insert("", tk.END, values=(row["Time"], row["Subject"], row["Date"]))

    # Top Frame for search, filter, and date picker
    top_frame = tk.Frame(attendance_window, bg="#1e1e2f")
    top_frame.pack(pady=10)

    tk.Label(top_frame, text="Search:", bg="#1e1e2f", fg="white").pack(side=tk.LEFT, padx=5)
    tk.Entry(top_frame, textvariable=search_var).pack(side=tk.LEFT, padx=5)

    search_btn = tk.Button(top_frame, text="Search", bg="#2d89ef", fg="white", command=filter_attendance)
    search_btn.pack(side=tk.LEFT, padx=5)

    tk.Label(top_frame, text="Filter by Subject:", bg="#1e1e2f", fg="white").pack(side=tk.LEFT, padx=10)
    subjects = ["All Subjects"] + sorted(full_data["Subject"].dropna().unique())
    subject_dropdown = ttk.Combobox(top_frame, textvariable=subject_var, values=subjects, state="readonly")
    subject_dropdown.pack(side=tk.LEFT, padx=5)
    subject_dropdown.bind("<<ComboboxSelected>>", lambda event: filter_attendance())

    # Date Picker for selecting the date
    tk.Label(top_frame, text="Select Date:", bg="#1e1e2f", fg="white").pack(side=tk.LEFT, padx=10)
    dates = ["All Dates"] + sorted(full_data["Date"].dropna().unique())
    date_dropdown = ttk.Combobox(top_frame, textvariable=date_var, values=dates, state="readonly")
    date_dropdown.pack(side=tk.LEFT, padx=5)
    date_dropdown.bind("<<ComboboxSelected>>", lambda event: filter_attendance())

    columns = ("Time", "Subject", "Date")
    tree = ttk.Treeview(attendance_window, columns=columns, show="headings")
    tree.heading("Time", text="Time")
    tree.heading("Subject", text="Subject")
    tree.heading("Date", text="Date")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", background="#2b2b40", fieldbackground="#2b2b40", foreground="white")
    style.configure("Treeview.Heading", background="#404060", foreground="white", font=("Segoe UI", 11, "bold"))

    # Insert all records into the treeview
    for index, row in full_data.iterrows():
        tree.insert("", tk.END, values=(row["Time"], row["Subject"], row["Date"]))

    tree.pack(expand=True, fill="both", padx=10, pady=10)

    reset_btn = tk.Button(attendance_window, text="Reset", bg="#6c757d", fg="white",
                          command=lambda: [search_var.set(""), subject_var.set("All Subjects"), date_var.set("All Dates"), filter_attendance()])
    reset_btn.pack(pady=10)


def admin_panel():
    """GUI panel for admin to manage timetable."""
    admin_window = tk.Toplevel()
    admin_window.title("Faculty Panel")
    admin_window.state('zoomed')  # Maximizes the window (Windows only)
    admin_window.configure(bg="#1e1e2f")

    def add_class():
        class_name = class_name_entry.get()
        time_slot = time_slot_entry.get()
        student_ids = student_ids_entry.get().split(',')  # Comma-separated list of student IDs

        if class_name and time_slot and student_ids:
            add_class_to_timetable(class_name, time_slot, student_ids)
            messagebox.showinfo("Success", f"Class '{class_name}' added successfully!")
        else:
            messagebox.showwarning("Input Error", "Please fill all fields.")

    def view_timetable():
        timetable_file = "timetable.json"
        if not os.path.exists(timetable_file):
            messagebox.showinfo("Timetable", "No timetable found.")
            return

        with open(timetable_file, "r") as f:
            timetable_data = json.load(f)

        classes = timetable_data.get("classes", [])
        classes = sorted(classes, key=lambda cls: cls.get("time_slot", ""))  # Sort by time

        # Load faculty assignments
        faculty_file = "admin_credentials.csv"
        subject_faculty_map = {}
        if os.path.exists(faculty_file):
            with open(faculty_file, "r") as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) == 3:
                        username, password, subject = row
                        subject_faculty_map[subject.strip()] = username.strip()

        view_window = tk.Toplevel(admin_window)
        view_window.title("View Timetable")
        view_window.state('zoomed')  # Maximizes the window (Windows only)
        view_window.configure(bg="#1e1e2f")

        search_var = tk.StringVar()
        time_filter_var = tk.StringVar(value="All Times")

        def filter_classes():
            search_text = search_var.get().lower()
            selected_time = time_filter_var.get()

            for item in tree.get_children():
                tree.delete(item)

            for cls in classes:
                class_name = cls.get("class_name", "N/A")
                time_slot = cls.get("time_slot", "N/A")
                students = ", ".join(cls.get("students", []))
                faculty = subject_faculty_map.get(class_name, "Substitute")

                if (search_text in class_name.lower()) and (selected_time == "All Times" or time_slot == selected_time):
                    tree.insert("", tk.END, values=(class_name, faculty, time_slot, students))

        # Top Frame for search and filter
        top_frame = tk.Frame(view_window, bg="#1e1e2f")
        top_frame.pack(pady=10)

        tk.Label(top_frame, text="Search Class:", bg="#1e1e2f", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Entry(top_frame, textvariable=search_var).pack(side=tk.LEFT, padx=5)

        tk.Button(top_frame, text="Search", bg="#2d89ef", fg="white", command=filter_classes).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="Reset", bg="#6c757d", fg="white",
              command=lambda: [search_var.set(""), time_filter_var.set("All Times"), filter_classes()]).pack(side=tk.LEFT, padx=5)

        tk.Label(top_frame, text="Filter by Time:", bg="#1e1e2f", fg="white").pack(side=tk.LEFT, padx=10)

        time_slots = ["All Times"] + sorted(list({cls.get("time_slot", "") for cls in classes}))
        ttk.Combobox(top_frame, textvariable=time_filter_var, values=time_slots, state="readonly").pack(side=tk.LEFT, padx=5)
        time_filter_var.trace_add("write", lambda *args: filter_classes())

        # Table
        columns = ("Class Name", "Faculty", "Time Slot", "Students")
        tree = ttk.Treeview(view_window, columns=columns, show="headings")
        for col in columns:
                tree.heading(col, text=col)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b40", fieldbackground="#2b2b40", foreground="white")
        style.configure("Treeview.Heading", background="#404060", foreground="white", font=("Segoe UI", 11, "bold"))

        def populate_table():
            for item in tree.get_children():
                tree.delete(item)
            for cls in classes:
                class_name = cls.get("class_name", "N/A")
                time_slot = cls.get("time_slot", "N/A")
                students = ", ".join(cls.get("students", []))
                faculty = subject_faculty_map.get(class_name, "Substitute")
                tree.insert("", tk.END, values=(class_name, faculty, time_slot, students))

        populate_table()
        tree.pack(expand=True, fill="both", padx=10, pady=10)

        # Edit Functionality
        def edit_selected_class():
            selected_item = tree.focus()
            if not selected_item:
                messagebox.showwarning("Select Class", "Please select a class to edit.")
                return

            values = tree.item(selected_item, "values")
            if not values:
                return

            old_class_name = values[0]

            edit_window = tk.Toplevel(view_window)
            edit_window.title("Edit Class")
            edit_window.state('zoomed')  # Maximizes the window (Windows only)
            edit_window.configure(bg="#1e1e2f")

            tk.Label(edit_window, text="New Class Name:", bg="#1e1e2f", fg="white").pack(pady=5)
            entry_class_name = tk.Entry(edit_window)
            entry_class_name.insert(0, values[0])
            entry_class_name.pack(pady=5)

            tk.Label(edit_window, text="New Time Slot:", bg="#1e1e2f", fg="white").pack(pady=5)
            entry_time_slot = tk.Entry(edit_window)
            entry_time_slot.insert(0, values[2])
            entry_time_slot.pack(pady=5)

            tk.Label(edit_window, text="New Student IDs (comma separated):", bg="#1e1e2f", fg="white").pack(pady=5)
            entry_students = tk.Entry(edit_window)
            entry_students.insert(0, values[3])
            entry_students.pack(pady=5)

            def save_changes():
                new_class_name = entry_class_name.get()
                new_time_slot = entry_time_slot.get()
                new_students = entry_students.get().split(',')

                for cls in classes:
                    if cls["class_name"] == old_class_name:
                        cls["class_name"] = new_class_name
                        cls["time_slot"] = new_time_slot
                        cls["students"] = [s.strip() for s in new_students]

                with open(timetable_file, "w") as f:
                    json.dump({"classes": classes}, f, indent=4)

                messagebox.showinfo("Success", "Class updated successfully!")
                edit_window.destroy()
                view_window.destroy()
                view_timetable()

            tk.Button(edit_window, text="Save Changes", bg="#2d89ef", fg="white", command=save_changes).pack(pady=20)

        def delete_selected_class():
            selected_item = tree.focus()
            if not selected_item:
                messagebox.showwarning("Select Class", "Please select a class to delete.")
                return

            values = tree.item(selected_item, "values")
            if not values:
                return

            class_name_to_delete = values[0]

            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{class_name_to_delete}'?")
            if not confirm:
                return

            new_classes = [cls for cls in classes if cls["class_name"] != class_name_to_delete]

            with open(timetable_file, "w") as f:
                json.dump({"classes": new_classes}, f, indent=4)

            messagebox.showinfo("Deleted", f"Class '{class_name_to_delete}' deleted successfully!")
            view_window.destroy()
            view_timetable()

        tk.Button(view_window, text="Edit Selected Class", bg="#2d89ef", fg="white", command=edit_selected_class).pack(pady=5)
        tk.Button(view_window, text="Delete Selected Class", bg="#d9534f", fg="white", command=delete_selected_class).pack(pady=5)



    # --- Admin Panel Layout ---

    tk.Label(admin_window, text="Class Name", bg="#1e1e2f", fg="#ffffff", font=("Segoe UI", 12)).pack(pady=5)
    class_name_entry = tk.Entry(admin_window, font=("Segoe UI", 12))
    class_name_entry.pack(pady=5)

    tk.Label(admin_window, text="Time Slot (HH:MM)", bg="#1e1e2f", fg="#ffffff", font=("Segoe UI", 12)).pack(pady=5)
    time_slot_entry = tk.Entry(admin_window, font=("Segoe UI", 12))
    time_slot_entry.pack(pady=5)

    tk.Label(admin_window, text="Student IDs (comma separated)", bg="#1e1e2f", fg="#ffffff", font=("Segoe UI", 12)).pack(pady=5)
    student_ids_entry = tk.Entry(admin_window, font=("Segoe UI", 12))
    student_ids_entry.pack(pady=5)

    add_class_button = tk.Button(admin_window, text="Add Class", font=("Segoe UI", 12), bg="#2d89ef", fg="#ffffff", command=lambda:[play_click2_sound(),add_class()])
    add_class_button.pack(pady=15)

    view_timetable_button = tk.Button(admin_window, text="View Timetable", font=("Segoe UI", 12), bg="#2d89ef", fg="#ffffff", command=lambda:[play_click2_sound(),view_timetable()])
    view_timetable_button.pack(pady=10)

# Start the login system
admin_login()
