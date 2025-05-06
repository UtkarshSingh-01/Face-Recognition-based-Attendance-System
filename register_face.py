import cv2
import os

def register_student(student_id, student_name):
    # Load Haar cascade for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    
    # Start webcam
    cap = cv2.VideoCapture(0)
    count = 0
    
    # Folder to save images
    save_path = f"student_data/{student_id}_{student_name}"
    os.makedirs(save_path, exist_ok=True)
    
    print("[INFO] Starting face capture. Look at the camera...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in faces:
            face_img = gray[y:y+h, x:x+w]
            count += 1
            file_name_path = f"{save_path}/{count}.jpg"
            cv2.imwrite(file_name_path, face_img)
            
            # Draw the rectangle *after* saving image
            cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 2)
            cv2.putText(frame, f"Images Captured: {count}/50", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
            
            # Small delay after each capture
            cv2.imshow("Register Face", frame)
            cv2.waitKey(100)

        cv2.imshow("Register Face", frame)

        # Press Enter key or stop after 50
        if cv2.waitKey(1) == 13 or count >= 50:
            break

    
    cap.release()
    cv2.destroyAllWindows()
    print(f"[INFO] Face registration complete for {student_name} (ID: {student_id})")
