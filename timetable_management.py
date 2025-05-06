import json
import os

TIMETABLE_FILE = "timetable.json"  # Path to the timetable JSON file

def create_timetable():
    """Create an empty timetable if it doesn't exist."""
    if not os.path.exists(TIMETABLE_FILE):
        timetable = {"classes": []}
        with open(TIMETABLE_FILE, "w") as file:
            json.dump(timetable, file)
        print("Timetable created.")
    else:
        print("Timetable already exists.")

def add_class_to_timetable(class_name, time_slot, student_ids):
    """Add a class to the timetable."""
    with open(TIMETABLE_FILE, "r") as file:
        timetable = json.load(file)

    # Add new class to the timetable
    new_class = {
        "class_name": class_name,
        "time_slot": time_slot,
        "students": student_ids
    }

    timetable["classes"].append(new_class)

    with open(TIMETABLE_FILE, "w") as file:
        json.dump(timetable, file)

    print(f"Class '{class_name}' added to timetable.")

def get_classes_for_time(time_slot):
    """Get all classes scheduled for a specific time."""
    with open(TIMETABLE_FILE, "r") as file:
        timetable = json.load(file)

    classes_at_time = [cls for cls in timetable["classes"] if cls["time_slot"] == time_slot]
    return classes_at_time
