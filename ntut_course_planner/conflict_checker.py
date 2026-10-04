from models import VALID_PERIODS


def slot_sort_key(slot):
    return (slot.day, VALID_PERIODS.index(str(slot.period)))


def find_overlaps(slots_a, slots_b):
    a = {(s.day, str(s.period)) for s in slots_a}
    b = {(s.day, str(s.period)) for s in slots_b}
    return sorted(a & b, key=lambda x: (x[0], VALID_PERIODS.index(x[1])))


def check_enrollment(student, target_course, courses, activities):
    issues = []

    for code in student.selected_courses:
        current = courses.get(code)
        if current:
            overlaps = find_overlaps(current.timeslots, target_course.timeslots)
            for day, period in overlaps:
                issues.append({
                    "type": "course_conflict",
                    "day": day,
                    "period": period,
                    "with": current.code
                })

    for activity_code in student.activities:
        activity = activities.get(activity_code)
        if activity and not activity.cancelled:
            overlaps = find_overlaps(activity.timeslots(), target_course.timeslots)
            for day, period in overlaps:
                issues.append({
                    "type": "activity_conflict",
                    "day": day,
                    "period": period,
                    "with": activity.code
                })

    current_credits = sum(courses[c].credits for c in student.selected_courses if c in courses)
    if current_credits + target_course.credits > student.credit_limit:
        issues.append({
            "type": "credit_limit",
            "current_credits": current_credits,
            "after_credits": current_credits + target_course.credits,
            "limit": student.credit_limit
        })

    if target_course.remaining_seats <= 0:
        issues.append({"type": "course_full"})

    return issues


def enroll_student(student, target_course, courses, activities):
    issues = check_enrollment(student, target_course, courses, activities)
    if issues:
        return False, issues
    if target_course.code not in student.selected_courses:
        student.selected_courses.append(target_course.code)
    if student.student_id not in target_course.enrolled_students:
        target_course.enrolled_students.append(student.student_id)
    return True, []


def withdraw_student(student, course):
    if course.code in student.selected_courses:
        student.selected_courses.remove(course.code)
    if student.student_id in course.enrolled_students:
        course.enrolled_students.remove(student.student_id)
