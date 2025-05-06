This project uses Python to create an advanced student attendance system that replaces manual methods with automation, improving accuracy, saving time, and reducing errors through smart technology.

# 🎓 Face Recognition Based Attendance System

A Python-based project that automates student attendance using face recognition. This system captures, trains, and recognizes student faces in real time and logs attendance efficiently.

## 🚀 Features

- 📸 Face detection and image capture
- 🧠 Model training using OpenCV
- 👁️ Real-time face recognition
- 🗂️ Attendance logging with date & time
- 🔐 Password-protected admin panel
- 🖥️ User-friendly GUI using Tkinter

## 🛠️ Tech Stack

- Python
- OpenCV
- NumPy
- Tkinter
- CSV for data storage
- PIL (Pillow) for image handling


## 📸 How It Works

1. **Register**: Capture student face images.
2. **Train**: Generate a recognition model from images.
3. **Recognize**: System identifies students via webcam.
4. **Mark**: Attendance is logged automatically.

![libraries](https://github.com/user-attachments/assets/07500c11-d4e0-48d4-bc84-f16cd0cab25d)

## 👥 User Roles & Permissions

The system supports three distinct user roles with specific functionalities:

### 🔹 Coordinator

The coordinator has administrative access and manages backend operations:

- 👤 Register new **students** and capture face data  
- 🧠 Train the face recognition **model**  
- 🧑‍🏫 Register and manage **faculty** details  
- 📅 Create and update **class timetables**  
- 🛠️ Full control over system configuration and records

---

### 🔸 Faculty

Faculty members manage classroom attendance and monitor students:

- ✅ **Mark attendance** for students using face recognition  
- 📊 View attendance **records** of their classes  
- 📆 Access and manage their **teaching timetable**  
- 🔓 Enable or disable **student self-attendance** for sessions

---

### 🔻 Student

Students interact with the system to view and record their attendance:

- 🧍‍♂️ **Mark attendance** using face recognition (if enabled by faculty)  
- 📈 View personal **attendance history**  
- 🗓️ Access their **class timetable**

