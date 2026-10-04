from models import Student


class StudentManager:
    def __init__(self, students=None):
        self.students = students or {}

    def add_student(self, student: Student):
        student.validate()
        if student.student_id in self.students:
            raise ValueError("duplicate student id")
        self.students[student.student_id] = student
        return student

    def update_student(self, student_id, **changes):
        if student_id not in self.students:
            raise KeyError("student not found")
        student = self.students[student_id]
        for k, v in changes.items():
            if hasattr(student, k):
                setattr(student, k, v)
        student.validate()
        return student

    def delete_student(self, student_id):
        if student_id not in self.students:
            raise KeyError("student not found")
        return self.students.pop(student_id)

    def get(self, student_id):
        return self.students.get(student_id)
