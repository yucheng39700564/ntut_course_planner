def filter_courses(courses, desired_codes=None, required_codes=None, forbidden_slots=None,
                   preferred_days=None, only_with_seats=True):
    desired_codes = set(desired_codes or [])
    required_codes = set(required_codes or [])
    forbidden_slots = set((d, str(p)) for d, p in (forbidden_slots or []))
    preferred_days = set(preferred_days or [])

    result = []
    for c in courses.values():
        if only_with_seats and c.remaining_seats <= 0:
            continue
        if desired_codes and c.code not in desired_codes and c.code not in required_codes:
            continue
        if any((s.day, str(s.period)) in forbidden_slots for s in c.timeslots):
            continue
        if preferred_days and not any(s.day in preferred_days for s in c.timeslots):
            continue
        result.append(c)

    missing_required = [x for x in required_codes if x not in {c.code for c in result}]
    return result, missing_required
