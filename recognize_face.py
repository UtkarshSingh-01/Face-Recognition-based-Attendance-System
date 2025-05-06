import cv2
import numpy as np
import pandas as pd
from datetime import datetime
import os

def recognize_and_mark():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("trained_model.yml")
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    cam = cv2.VideoCapture(0)
    attendance = []
    
    while True:
        ret, frame = cam.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x,y,w,h) in faces:
            face = gray[y:y+h, x:x+w]
            id_, conf = recognizer.predict(face)
            if conf < 70:
                name = [d for d in os.listdir("student_data") if str(id_) in d][0].split("_")[1]
                cv2.putText(frame, f"{name} ({id_})", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
                attendance.append((id_, name, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            else:
                cv2.putText(frame, "Unknown", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

            cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 2)

        cv2.imshow("Face Recognition", frame)
        if cv2.waitKey(1) == 13:
            break

    cam.release()
    cv2.destroyAllWindows()

    # Save attendance
    df = pd.DataFrame(set(attendance), columns=["ID", "Name", "DateTime"])
    if not os.path.exists("attendance"):
        os.makedirs("attendance")
    df.to_csv(f"attendance/attendance_{datetime.now().date()}.csv", index=False)
    print("[INFO] Attendance saved.")

