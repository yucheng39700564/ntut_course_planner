from models import Course


class CourseManager:
    def __init__(self, courses=None):
        self.courses = courses or {}

    def add_course(self, course: Course):
        course.validate()
        if course.code in self.courses:
            raise ValueError("duplicate course code")
        self.courses[course.code] = course
        return course

    def update_course(self, code, **changes):
        if code not in self.courses:
            raise KeyError("course not found")
        course = self.courses[code]
        for k, v in changes.items():
            if hasattr(course, k):
                setattr(course, k, v)
        course.validate()
        return course

    def delete_course(self, code):
        if code not in self.courses:
            raise KeyError("course not found")
        if self.courses[code].enrolled_students:
            raise ValueError("cannot delete a course with enrolled students")
        return self.courses.pop(code)

    def get(self, code):
        return self.courses.get(code)

    def search(self, code=None, teacher=None, day=None, required=None, has_seat=None):
        result = list(self.courses.values())
        if code:
            result = [c for c in result if code.lower() in c.code.lower()]
        if teacher:
            result = [c for c in result if teacher.lower() in c.teacher.lower()]
        if day is not None:
            result = [c for c in result if any(s.day == day for s in c.timeslots)]
        if required is not None:
            result = [c for c in result if c.required == required]
        if has_seat is True:
            result = [c for c in result if c.remaining_seats > 0]
        return result
