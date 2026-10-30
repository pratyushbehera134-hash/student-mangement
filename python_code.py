# models.py

class Person:
    def __init__(self, name: str) -> None:
        self.name = name

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        cleaned_name = value.strip()
        if not cleaned_name:
            raise ValueError("Student name cannot be empty.")
        self.__name = cleaned_name


class Student(Person):
    def __init__(
        self,
        name: str,
        roll_number: str,
        course: str,
        marks: int,
    ) -> None:
        super().__init__(name)
        self.roll_number = roll_number
        self.course = course
        self.marks = marks

    @property
    def roll_number(self) -> str:
        return self.__roll_number

    @roll_number.setter
    def roll_number(self, value: str) -> None:
        cleaned_roll_number = value.strip()
        if not cleaned_roll_number:
            raise ValueError("Roll number cannot be empty.")
        self.__roll_number = cleaned_roll_number

    @property
    def course(self) -> str:
        return self.__course

    @course.setter
    def course(self, value: str) -> None:
        cleaned_course = value.strip()
        if not cleaned_course:
            raise ValueError("Course cannot be empty.")
        self.__course = cleaned_course

    @property
    def marks(self) -> int:
        return self.__marks

    @marks.setter
    def marks(self, value: int) -> None:
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError("Marks must be a whole number.")
        if not 0 <= value <= 100:
            raise ValueError("Marks must be between 0 and 100.")
        self.__marks = value

    def to_record(self) -> dict[str, str | int]:
        return {
            "name": self.name,
            "roll_number": self.roll_number,
            "course": self.course,
            "marks": self.marks,
        }


# database.py

import sqlite3
from pathlib import Path

from student_management.models import Student


DEFAULT_DATABASE_PATH = Path(__file__).with_name("students.db")


class StudentDatabase:
    def __init__(self, database_path: str | Path = DEFAULT_DATABASE_PATH) -> None:
        self.__database_path = str(database_path)
        self.create_table()

    def __connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.__database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def create_table(self) -> None:
        with self.__connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    roll_number TEXT NOT NULL COLLATE NOCASE UNIQUE,
                    course TEXT NOT NULL,
                    marks INTEGER NOT NULL CHECK (marks BETWEEN 0 AND 100)
                )
                """
            )

    def add_student(self, student: Student) -> None:
        record = student.to_record()
        try:
            with self.__connect() as connection:
                connection.execute(
                    """
                    INSERT INTO students (name, roll_number, course, marks)
                    VALUES (:name, :roll_number, :course, :marks)
                    """,
                    record,
                )
        except sqlite3.IntegrityError as error:
            if "UNIQUE" in str(error).upper():
                raise ValueError("That roll number is already in use.") from error
            raise

    def get_all_students(self) -> list[Student]:
        with self.__connect() as connection:
            rows = connection.execute(
                """
                SELECT name, roll_number, course, marks
                FROM students
                ORDER BY name COLLATE NOCASE, roll_number COLLATE NOCASE
                """
            ).fetchall()

        return [
            Student(
                name=row["name"],
                roll_number=row["roll_number"],
                course=row["course"],
                marks=row["marks"],
            )
            for row in rows
        ]

    def find_by_roll_number(self, roll_number: str) -> Student | None:
        with self.__connect() as connection:
            row = connection.execute(
                """
                SELECT name, roll_number, course, marks
                FROM students
                WHERE roll_number = ? COLLATE NOCASE
                """,
                (roll_number.strip(),),
            ).fetchone()

        if row is None:
            return None

        return Student(
            name=row["name"],
            roll_number=row["roll_number"],
            course=row["course"],
            marks=row["marks"],
        )

    def delete_student(self, roll_number: str) -> bool:
        with self.__connect() as connection:
            cursor = connection.execute(
                "DELETE FROM students WHERE roll_number = ? COLLATE NOCASE",
                (roll_number.strip(),),
            )
        return cursor.rowcount > 0
