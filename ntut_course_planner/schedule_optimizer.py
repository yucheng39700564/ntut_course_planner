import itertools
from conflict_checker import find_overlaps


def schedule_is_feasible(course_list, min_credits, max_credits, required_codes=None,
                         forbidden_slots=None):
    required_codes = set(required_codes or [])
    forbidden_slots = set((d, str(p)) for d, p in (forbidden_slots or []))
    codes = {c.code for c in course_list}
    if not required_codes.issubset(codes):
        return False
    credits = sum(c.credits for c in course_list)
    if not (min_credits <= credits <= max_credits):
        return False
    if any(c.remaining_seats <= 0 for c in course_list):
        return False
    for c in course_list:
        if any((s.day, str(s.period)) in forbidden_slots for s in c.timeslots):
            return False
    for i in range(len(course_list)):
        for j in range(i + 1, len(course_list)):
            if find_overlaps(course_list[i].timeslots, course_list[j].timeslots):
                return False
    return True


def score_schedule(course_list, weights=None, preferred_codes=None):
    weights = weights or {
        "days": 3.0,
        "gaps": 1.5,
        "early": 2.0,
        "preferred": 2.5,
    }
    preferred_codes = set(preferred_codes or [])

    day_periods = {}
    for c in course_list:
        for s in c.timeslots:
            day_periods.setdefault(s.day, []).append(str(s.period))

    school_days = len(day_periods)
    early = sum(1 for periods in day_periods.values() if "1" in periods)
    gaps = 0
    order = [str(i) for i in range(1,10)] + ["a","b","c"]
    for periods in day_periods.values():
        idx = sorted(order.index(p) for p in set(periods))
        if len(idx) >= 2:
            gaps += (idx[-1] - idx[0] + 1) - len(idx)

    preferred = sum(1 for c in course_list if c.code in preferred_codes)
    return (
        -weights["days"] * school_days
        -weights["gaps"] * gaps
        -weights["early"] * early
        +weights["preferred"] * preferred
    )


def exhaustive_search(candidates, min_credits, max_credits, required_codes=None,
                      forbidden_slots=None):
    feasible = []
    nodes = 0
    for r in range(len(candidates) + 1):
        for combo in itertools.combinations(candidates, r):
            nodes += 1
            if schedule_is_feasible(combo, min_credits, max_credits, required_codes, forbidden_slots):
                feasible.append(list(combo))
    return feasible, nodes


def backtracking_search(candidates, min_credits, max_credits, required_codes=None,
                        forbidden_slots=None):
    feasible = []
    nodes = 0
    required_codes = set(required_codes or [])
    forbidden_slots = set((d, str(p)) for d,p in (forbidden_slots or []))

    def conflicts_with_selected(course, selected):
        if course.remaining_seats <= 0:
            return True
        if any((s.day, str(s.period)) in forbidden_slots for s in course.timeslots):
            return True
        return any(find_overlaps(course.timeslots, x.timeslots) for x in selected)

    from conflict_checker import find_overlaps

    def dfs(index, selected, credits):
        nonlocal nodes
        nodes += 1
        if credits > max_credits:
            return
        if index == len(candidates):
            if min_credits <= credits <= max_credits:
                codes = {c.code for c in selected}
                if required_codes.issubset(codes):
                    feasible.append(selected.copy())
            return

        course = candidates[index]
        dfs(index + 1, selected, credits)

        if not conflicts_with_selected(course, selected):
            selected.append(course)
            dfs(index + 1, selected, credits + course.credits)
            selected.pop()

    dfs(0, [], 0)
    return feasible, nodes


def ranked_schedules(candidates, min_credits, max_credits, required_codes=None,
                     forbidden_slots=None, weights=None, preferred_codes=None, top_n=5):
    feasible, nodes = backtracking_search(
        candidates, min_credits, max_credits, required_codes, forbidden_slots
    )
    ranked = sorted(
        feasible,
        key=lambda s: score_schedule(s, weights, preferred_codes),
        reverse=True
    )
    return [(s, score_schedule(s, weights, preferred_codes)) for s in ranked[:top_n]], nodes
