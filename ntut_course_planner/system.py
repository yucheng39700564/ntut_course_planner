from models import Course, Student, Classroom, Activity
from data_manager import DataStore
from course_manager import CourseManager
from student_manager import StudentManager
from activity_manager import ActivityManager
from campus_map import CampusMap


class CampusSystem:
    def __init__(self, data_dir="data"):
        self.store = DataStore(data_dir)
        raw = self.store.load_all()
        self.courses = {x["code"]: Course.from_dict(x) for x in raw["courses"]}
        self.students = {x["student_id"]: Student(**x) for x in raw["students"]}
        self.classrooms = {x["code"]: Classroom(**x) for x in raw["classrooms"]}
        self.activities = {x["code"]: Activity(**x) for x in raw["activities"]}
        self.campus_graph = raw["campus_graph"]

        self.course_manager = CourseManager(self.courses)
        self.student_manager = StudentManager(self.students)
        self.activity_manager = ActivityManager(self.activities)
        self.campus_map = CampusMap(self.campus_graph)

    def save(self):
        self.store.save_all(
            self.courses, self.students, self.classrooms,
            self.activities, self.campus_graph
        )
