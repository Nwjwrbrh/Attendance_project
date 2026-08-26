import subprocess
import sys
from pathlib import Path

from database import get_attendance_records


BASE_DIR = Path(__file__).resolve().parent


def register_student():
    """Start student registration."""

    name = input("\nEnter student name: ").strip()
    roll_no = input("Enter roll number: ").strip()

    if not name or not roll_no:
        print("\nError: Name and roll number cannot be empty.")
        return

    subprocess.run(
        [
            sys.executable,
            str(BASE_DIR / "register.py"),
            name,
            roll_no
        ]
    )


def start_attendance():
    """Start attendance recognition."""

    subprocess.run(
        [
            sys.executable,
            str(BASE_DIR / "attendance.py")
        ]
    )


def view_attendance():
    """Display attendance records."""

    while True:

        roll_no = input(
            "\nEnter roll number to search "
            "(or press Enter to show all, Q to go back): "
        ).strip()

        if roll_no.lower() == "q":
            break

        records = get_attendance_records()

        # Filter by roll number if one was entered
        if roll_no:
            records = [
                record
                for record in records
                if record[1] == roll_no
            ]

        if not records:
            print("\nNo attendance records found.")
            continue

        print("\n" + "=" * 75)
        print(
            f"{'Name':<20}"
            f"{'Roll No':<15}"
            f"{'Date':<15}"
            f"{'Time':<12}"
            f"{'Status':<10}"
        )
        print("=" * 75)

        for record in records:

            name, roll_no, date, time, status = record

            print(
                f"{name:<20}"
                f"{roll_no:<15}"
                f"{date:<15}"
                f"{time:<12}"
                f"{status:<10}"
            )

        print("=" * 75)


def main():
    """Main application menu."""

    while True:

        print("\n" + "=" * 35)
        print("   FACE ATTENDANCE SYSTEM")
        print("=" * 35)

        print("1. Register Student")
        print("2. Start Attendance")
        print("3. View Attendance Records")
        print("4. Exit")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            register_student()

        elif choice == "2":
            start_attendance()

        elif choice == "3":
            view_attendance()

        elif choice == "4":
            print("\nExiting program.")
            break

        else:
            print("\nInvalid option. Please try again.")


if __name__ == "__main__":
    main()