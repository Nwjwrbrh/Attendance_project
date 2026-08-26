import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "attendance.db"


def get_connection():
    """Connect to the SQLite database."""

    connection = sqlite3.connect(DB_PATH)

    # Enable foreign key support
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def create_tables():
    """Create the required database tables."""

    connection = get_connection()
    cursor = connection.cursor()

    # Student information
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT NOT NULL UNIQUE,
            photo BLOB NOT NULL,
            face_embedding BLOB NOT NULL
        )
    """)

    # Attendance records
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Present',

            FOREIGN KEY (student_id)
                REFERENCES students(id)
                ON DELETE CASCADE

        )
    """)

    connection.commit()
    connection.close()


def add_student(name, roll_no, photo, face_embedding):
    """Add a student to the database."""

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO students (
                name,
                roll_no,
                photo,
                face_embedding
            )
            VALUES (?, ?, ?, ?)
        """, (
            name,
            roll_no,
            photo,
            face_embedding
        ))

        connection.commit()

        print(f"\nStudent '{name}' registered successfully.")

        return True

    except sqlite3.IntegrityError:
        print(f"\nError: Roll number '{roll_no}' already exists.")

        return False

    finally:
        connection.close()


def get_all_students():
    """Get all registered students."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            roll_no,
            face_embedding
        FROM students
    """)

    students = cursor.fetchall()

    connection.close()

    return students


def mark_attendance(student_id):
    """Mark attendance with a 5-minute cooldown."""

    connection = get_connection()
    cursor = connection.cursor()

    # Get the student's most recent attendance record
    cursor.execute("""
        SELECT date, time
        FROM attendance
        WHERE student_id = ?
        ORDER BY date DESC, time DESC
        LIMIT 1
    """, (student_id,))

    last_record = cursor.fetchone()

    now = datetime.now()

    # Check whether 5 minutes have passed
    if last_record:
        last_date, last_time = last_record

        last_datetime = datetime.strptime(
            f"{last_date} {last_time}",
            "%Y-%m-%d %H:%M:%S"
        )

        if now - last_datetime < timedelta(minutes=5):
            connection.close()
            return False

    # Insert new attendance record
    cursor.execute("""
        INSERT INTO attendance (
            student_id,
            date,
            time,
            status
        )
        VALUES (?, ?, ?, 'Present')
    """, (
        student_id,
        now.strftime("%Y-%m-%d"),
        now.strftime("%H:%M:%S")
    ))

    connection.commit()
    connection.close()

    return True


def get_attendance_records():
    """Get all attendance records."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            students.name,
            students.roll_no,
            attendance.date,
            attendance.time,
            attendance.status
        FROM attendance
        JOIN students
            ON attendance.student_id = students.id
        ORDER BY attendance.date DESC, attendance.time DESC
    """)

    records = cursor.fetchall()

    connection.close()

    return records


def get_student_attendance(roll_no):
    """Get attendance records for a specific roll number."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            students.name,
            students.roll_no,
            attendance.date,
            attendance.time,
            attendance.status
        FROM attendance
        JOIN students
            ON attendance.student_id = students.id
        WHERE students.roll_no = ?
        ORDER BY attendance.date DESC, attendance.time DESC
    """, (roll_no,))

    records = cursor.fetchall()

    connection.close()

    return records


if __name__ == "__main__":
    create_tables()

    print("Database created successfully.")
    print(f"Database location: {DB_PATH}")