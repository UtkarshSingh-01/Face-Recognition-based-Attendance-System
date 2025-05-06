import cv2
import json
import numpy as np
import os
from datetime import datetime
import pandas as pd
import tkinter as tk
from tkinter import simpledialog, messagebox


def load_timetable():
    """Load timetable data from timetable.json file"""
    try:
        with open("timetable.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        messagebox.showerror("Error", "Timetable file not found!")
        return {"classes": []}


def check_subject_in_timetable(subject_name, timetable_data):
    """Check if the subject exists in the timetable"""
    for class_data in timetable_data["classes"]:
        if class_data["class_name"].lower() == subject_name.lower():
            return class_data  # Return the class data if found
    return None


def check_student_in_class(student_id, class_data):
    """Check if the student is enrolled in the class"""
    student_id_str = str(student_id).strip()  # Ensure we treat the student ID as a string and remove extra spaces
    print(f"Checking student {student_id_str} in class {class_data['class_name']}...")  # Debugging line
    if student_id_str in class_data["students"]:
        return True
    return False


def recognize_and_mark():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("trained_model.yml")
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    data_dir = "student_data"
    id_name_map = {}

    # Map ID to Name from folder structure
    for folder in os.listdir(data_dir):
        if os.path.isdir(os.path.join(data_dir, folder)):
            student_id, student_name = folder.split('_', 1)
            id_name_map[int(student_id)] = student_name

    # Create attendance folder if not exists
    attendance_folder = "attendance"
    if not os.path.exists(attendance_folder):
        os.makedirs(attendance_folder)

    # Set the attendance file path
    attendance_file = os.path.join(attendance_folder, f"Attendance_{datetime.now().date()}.csv")
    attendance_set = set()

    if os.path.exists(attendance_file):
        df = pd.read_csv(attendance_file)
        attendance_set = set(df["ID"].astype(str) + "_" + df["Name"] + "_" + df.get("Subject", pd.Series([""])) )

    # --- ASK for Subject / Class Name using Tkinter dialog ---
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window

    subject_name = simpledialog.askstring("Subject Name", "Enter Subject Name (for attendance record):")

    if not subject_name:
        subject_name = "Unknown"

    # Load timetable data and validate the subject
    timetable_data = load_timetable()
    class_data = check_subject_in_timetable(subject_name, timetable_data)
    if class_data is None:
        messagebox.showerror("Invalid Subject", f"The subject '{subject_name}' is not found in the timetable.")
        return  # Exit if the subject is not valid

    # --- ASK for Student ID ---
    student_id_str = simpledialog.askstring("Student ID", "Enter your Student ID:")

    if not student_id_str:
        messagebox.showerror("Error", "Student ID is required!")
        return  # Exit if no student ID is entered

    student_id = student_id_str.strip()  # Strip any leading/trailing spaces

    # Check if the student ID is associated with the subject
    if not check_student_in_class(student_id, class_data):
        messagebox.showerror("Student Not Found", f"Student ID {student_id} is not associated with the subject {subject_name}.")
        return  # Exit if the student ID is not associated with the subject

    cap = cv2.VideoCapture(0)

    print("[INFO] Starting face recognition. Press Enter to exit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face_img = gray[y:y+h, x:x+w]
            id_, conf = recognizer.predict(face_img)

            if conf < 60:  # Confidence threshold
                name = id_name_map.get(id_, "Unknown")
                key = f"{id_}_{name}_{subject_name}"

                if key not in attendance_set:
                    now = datetime.now()
                    dt_string = now.strftime("%H:%M:%S")

                    write_header = not os.path.exists(attendance_file) or os.path.getsize(attendance_file) == 0

                    with open(attendance_file, "a") as f:
                        if write_header:
                            f.write("ID,Name,Time,Subject\n")
                        f.write(f"{id_},{name},{dt_string},{subject_name}\n")

                    attendance_set.add(key)
                    print(f"[MARKED] {name} ({id_}) for {subject_name} at {dt_string}")

                cv2.putText(frame, f"{name} ({id_})", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "Unknown", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        cv2.imshow("Face Recognition - Press Enter to Exit", frame)

        if cv2.waitKey(1) == 13:  # Enter key
            break

    cap.release()
    cv2.destroyAllWindows()
