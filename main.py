import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
from pathlib import Path
from database import get_attendance_records, get_student_attendance


BASE_DIR = Path(__file__).resolve().parent


def register_student():
    """Open the student registration window."""

    register_window = tk.Toplevel(root)

    register_window.title("Register Student")

    register_window.geometry("350x250")

    register_window.resizable(False, False)


    # Name
    tk.Label(
        register_window,
        text="Student Name"
    ).pack(pady=(20, 5))

    name_entry = tk.Entry(
        register_window,
        width=30
    )

    name_entry.pack()


    # Roll Number
    tk.Label(
        register_window,
        text="Roll Number"
    ).pack(pady=(15, 5))

    roll_entry = tk.Entry(
        register_window,
        width=30
    )

    roll_entry.pack()


    def start_registration():

        name = name_entry.get().strip()

        roll_no = roll_entry.get().strip()


        # Check that both fields are filled
        if not name or not roll_no:

            messagebox.showerror(
                "Error",
                "Please enter both name and roll number."
            )

            return


        # Start register.py with name and roll number
        subprocess.Popen(
            [
                sys.executable,
                str(BASE_DIR / "register.py"),
                name,
                roll_no
            ]
        )

        # Close registration window
        register_window.destroy()


    tk.Button(
        register_window,
        text="Start Camera",
        width=20,
        height=2,
        command=start_registration
    ).pack(pady=25)


def start_attendance():
    """Run the attendance script."""

    subprocess.Popen(
        [sys.executable, str(BASE_DIR / "attendance.py")]
    )


def view_attendance():
    """Open a window showing attendance records."""

    records = get_attendance_records()

    attendance_window = tk.Toplevel(root)

    attendance_window.title("Attendance Records")

    attendance_window.geometry("800x500")


    # Search area
    search_frame = tk.Frame(attendance_window)

    search_frame.pack(
        fill="x",
        padx=10,
        pady=10
    )


    tk.Label(
        search_frame,
        text="Roll Number:"
    ).pack(side="left")


    roll_entry = tk.Entry(
        search_frame,
        width=25
    )

    roll_entry.pack(
        side="left",
        padx=10
    )


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


    def display_records(records):
        """Clear and display records."""

        for item in table.get_children():
            table.delete(item)

        for record in records:
            table.insert(
                "",
                tk.END,
                values=record
            )


    def search_student():

        roll_no = roll_entry.get().strip()

        if roll_no:
            records = get_student_attendance(roll_no)
        else:
            # Empty search box = show all records
            records = get_attendance_records()

        display_records(records)


    # Search button
    tk.Button(
        search_frame,
        text="Search",
        command=search_student
    ).pack(side="left")


    table.pack(
        expand=True,
        fill="both",
        padx=10,
        pady=(0, 10)
    )


    # Display all records initially
    display_records(records)


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