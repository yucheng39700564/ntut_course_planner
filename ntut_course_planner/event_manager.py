from copy import deepcopy
from schedule_optimizer import ranked_schedules


def handle_dynamic_event(event, courses, classrooms, activities):
    event_type = event["type"]
    result = {"type": event_type, "changed": False, "reason": ""}

    if event_type == "course_full":
        code = event["course_code"]
        if code not in courses:
            result["reason"] = "course not found"
        else:
            c = courses[code]
            c.enrolled_students = [f"FULL{i}" for i in range(c.capacity)]
            result["changed"] = True

    elif event_type == "teacher_time_change":
        code = event["course_code"]
        if code not in courses:
            result["reason"] = "course not found"
        else:
            from models import TimeSlot
            courses[code].timeslots = [TimeSlot(**x) for x in event["timeslots"]]
            courses[code].validate()
            result["changed"] = True

    elif event_type == "classroom_unavailable":
        room = event["classroom"]
        affected = [c.code for c in courses.values() if c.classroom == room]
        result["affected_courses"] = affected
        result["changed"] = bool(affected)

    elif event_type == "mandatory_activity":
        code = event["activity_code"]
        if code not in activities:
            result["reason"] = "activity not found"
        else:
            result["changed"] = True

    else:
        raise ValueError("unsupported dynamic event")

    return result


def replan_schedule(candidates, min_credits, max_credits, required_codes,
                    forbidden_slots=None, preferred_codes=None):
    ranked, nodes = ranked_schedules(
        candidates,
        min_credits,
        max_credits,
        required_codes,
        forbidden_slots,
        preferred_codes=preferred_codes,
        top_n=1
    )
    if not ranked:
        return {"success": False, "reason": "no feasible alternative", "nodes": nodes}
    schedule, score = ranked[0]
    return {
        "success": True,
        "courses": [c.code for c in schedule],
        "score": score,
        "nodes": nodes
    }
