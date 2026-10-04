from models import VALID_PERIODS


def build_weekly_schedule(student, courses, activities):
    matrix = {day: {p: [] for p in VALID_PERIODS} for day in range(1, 8)}
    for code in student.selected_courses:
        c = courses.get(code)
        if c:
            for s in c.timeslots:
                matrix[s.day][str(s.period)].append(f"COURSE:{c.code}")
    for code in student.activities:
        a = activities.get(code)
        if a and not a.cancelled:
            for p in a.periods:
                matrix[a.day][str(p)].append(f"ACTIVITY:{a.code}")
    return matrix


def query_free_periods(student, courses, activities, day, start_period="1", end_period="c", min_length=1):
    schedule = build_weekly_schedule(student, courses, activities)
    start = VALID_PERIODS.index(str(start_period))
    end = VALID_PERIODS.index(str(end_period))
    if start > end:
        raise ValueError("start_period must not be after end_period")

    free = []
    current = []
    for p in VALID_PERIODS[start:end + 1]:
        if not schedule[day][p]:
            current.append(p)
        else:
            if len(current) >= min_length:
                free.append(current)
            current = []
    if len(current) >= min_length:
        free.append(current)
    return free


def schedule_statistics(student, courses, activities):
    schedule = build_weekly_schedule(student, courses, activities)
    daily = {d: sum(1 for p in VALID_PERIODS if schedule[d][p]) for d in range(1, 8)}
    credits = sum(courses[c].credits for c in student.selected_courses if c in courses)
    occupied = sum(daily.values())
    return {
        "daily_occupied_periods": daily,
        "weekly_credits": credits,
        "free_periods": 7 * len(VALID_PERIODS) - occupied
    }
