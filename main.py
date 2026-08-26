import tkinter as tk
from tkinter import ttk
import subprocess
import sys
from pathlib import Path
from database import get_attendance_records


BASE_DIR = Path(__file__).resolve().parent


def register_student():
    """Run the student registration script."""

    subprocess.Popen(
        [sys.executable, str(BASE_DIR / "register.py")]
    )


def start_attendance():
    """Run the attendance script."""

    subprocess.Popen(
        [sys.executable, str(BASE_DIR / "attendance.py")]
    )


def view_attendance():
    """Open a window showing attendance records."""

    records = get_attendance_records()

    # Create a new window
    attendance_window = tk.Toplevel(root)

    attendance_window.title("Attendance Records")

    attendance_window.geometry("800x500")


    # Create table
    columns = (
        "name",
        "roll_no",
        "date",
        "time",
        "status"
    )

    table = ttk.Treeview(
        attendance_window,
        columns=columns,
        show="headings"
    )


    # Table headings
    table.heading("name", text="Name")
    table.heading("roll_no", text="Roll Number")
    table.heading("date", text="Date")
    table.heading("time", text="Time")
    table.heading("status", text="Status")


    # Column sizes
    table.column("name", width=180)

    table.column("roll_no", width=120)

    table.column("date", width=120)

    table.column("time", width=120)

    table.column("status", width=100)


    # Insert database records
    for record in records:

        table.insert(
            "",
            tk.END,
            values=record
        )


    table.pack(
        expand=True,
        fill="both",
        padx=10,
        pady=10
    )


# Create main window
root = tk.Tk()

root.title("Face Attendance System")

root.geometry("400x400")

root.resizable(False, False)


# Title
title = tk.Label(
    root,
    text="FACE ATTENDANCE SYSTEM",
    font=("Arial", 18, "bold")
)

title.pack(pady=40)


# Register button
register_button = tk.Button(
    root,
    text="Register Student",
    font=("Arial", 12),
    width=20,
    height=2,
    command=register_student
)

register_button.pack(pady=10)


# Attendance button
attendance_button = tk.Button(
    root,
    text="Start Attendance",
    font=("Arial", 12),
    width=20,
    height=2,
    command=start_attendance
)

attendance_button.pack(pady=10)


#attendance view button
view_button = tk.Button(
    root,
    text="View Attendance Records",
    font=("Arial", 12),
    width=20,
    height=2,
    command=view_attendance
)

view_button.pack(pady=10)

# Start GUI
root.mainloop()