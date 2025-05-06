import cv2
import os
import numpy as np
from tkinter import simpledialog, Tk
import time

# Initialize the Tkinter window (hidden)
root = Tk()
root.withdraw()

# Get the student ID and name from the user
student_id = simpledialog.askstring("Input", "Enter Student ID:", parent=root)
student_name = simpledialog.askstring("Input", "Enter Student Name:", parent=root)

if student_id is None or student_name is None:
    print("Student registration canceled.")
    exit()

# Ensure the student_data directory exists
data_dir = "student_data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Create a folder for the student
student_folder = os.path.join(data_dir, f"{student_id}_{student_name}")
if not os.path.exists(student_folder):
    os.makedirs(student_folder)

# Initialize the webcam
cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Create the recognizer object
recognizer = cv2.face.LBPHFaceRecognizer_create()

# Capture images for training
count = 0
max_samples = 100  # Number of images to capture

print("[INFO] Starting to capture images for student registration...")

while count < max_samples:
    ret, frame = cap.read()
    if not ret:
        print("[ERROR] Failed to grab frame")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        count += 1
        face_img = gray[y:y+h, x:x+w]
        img_path = os.path.join(student_folder, f"{student_id}_{count}.jpg")
        cv2.imwrite(img_path, face_img)

        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        cv2.putText(frame, f"Capturing {count}/{max_samples}", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Registering Student", frame)

    # Wait for 1 ms and break the loop if 'ESC' is pressed
    if cv2.waitKey(1) & 0xFF == 27:  # ESC key to quit early
        break

# Release the webcam and close the window
cap.release()
cv2.destroyAllWindows()

# Confirmation
print(f"[INFO] Captured {count} images for {student_name} ({student_id})")

# Wait for 2 seconds before finishing
time.sleep(2)
