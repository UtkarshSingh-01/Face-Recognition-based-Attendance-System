import cv2
import numpy as np
from PIL import Image
import os
import tkinter as tk
from tkinter import messagebox

def train_model():
    # Create root context if not inside a main Tkinter loop
    temp_root = tk.Tk()
    temp_root.withdraw()

    # Show temporary training popup
    loading_window = tk.Toplevel()
    loading_window.title("Training")
    loading_window.geometry("300x100")
    loading_window.configure(bg="#1e1e2f")
    tk.Label(loading_window, text="Model training started.\nPlease wait...", fg="white", bg="#1e1e2f", font=("Segoe UI", 11)).pack(expand=True)
    loading_window.update()  # Ensure it renders immediately

    temp_root.update()

    data_dir = "student_data"
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    ids = []
    faces = []

    for folder in os.listdir(data_dir):
        folder_path = os.path.join(data_dir, folder)
        if not os.path.isdir(folder_path):
            continue
        try:
            student_id = int(folder.split('_')[0])  # Extract ID from folder name
        except ValueError:
            continue

        for image_file in os.listdir(folder_path):
            image_path = os.path.join(folder_path, image_file)
            img = Image.open(image_path).convert("L")  # grayscale
            img_np = np.array(img, "uint8")

            faces_detected = face_cascade.detectMultiScale(img_np)
            for (x, y, w, h) in faces_detected:
                faces.append(img_np[y:y+h, x:x+w])
                ids.append(student_id)

    if not faces:
        loading_window.destroy()
        messagebox.showerror("Error", "No faces found. Please register students first.")
        return

    recognizer.train(faces, np.array(ids))
    recognizer.save("trained_model.yml")

    loading_window.destroy()
    messagebox.showinfo("Success", "Model training complete.\nSaved as trained_model.yml")

    temp_root.destroy()
