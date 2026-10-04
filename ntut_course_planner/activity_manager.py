from models import Activity
from conflict_checker import find_overlaps


class ActivityManager:
    def __init__(self, activities=None):
        self.activities = activities or {}

    def add_activity(self, activity: Activity):
        activity.validate()
        if activity.code in self.activities:
            raise ValueError("duplicate activity code")
        self.activities[activity.code] = activity
        return activity

    def cancel_activity(self, code):
        if code not in self.activities:
            raise KeyError("activity not found")
        self.activities[code].cancelled = True

    def suitable_classrooms(self, activity, classrooms, courses):
        result = []
        rejected = {}
        for room in classrooms.values():
            reasons = []
            if room.capacity < activity.capacity:
                reasons.append("insufficient_capacity")
            missing = [x for x in activity.required_equipment if x not in room.equipment]
            if missing:
                reasons.append("missing_equipment:" + ",".join(missing))

            for course in courses.values():
                if course.classroom == room.code and find_overlaps(course.timeslots, activity.timeslots()):
                    reasons.append("time_conflict")
                    break

            for other in self.activities.values():
                if other.code != activity.code and not other.cancelled and other.classroom == room.code:
                    if find_overlaps(other.timeslots(), activity.timeslots()):
                        reasons.append("time_conflict")
                        break

            if reasons:
                rejected[room.code] = reasons
            else:
                result.append(room.code)
        return result, rejected

    def assign_classroom(self, activity_code, room_code, classrooms, courses):
        activity = self.activities[activity_code]
        suitable, rejected = self.suitable_classrooms(activity, classrooms, courses)
        if room_code not in suitable:
            raise ValueError(f"classroom not suitable: {rejected.get(room_code, ['unknown'])}")
        activity.classroom = room_code

    def register(self, activity_code, student_id):
        a = self.activities[activity_code]
        if a.cancelled:
            raise ValueError("activity is cancelled")
        if a.remaining_seats <= 0:
            raise ValueError("activity is full")
        if student_id not in a.participants:
            a.participants.append(student_id)
