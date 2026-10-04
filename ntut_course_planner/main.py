from system import CampusSystem
from conflict_checker import enroll_student, withdraw_student
from schedule_manager import build_weekly_schedule, query_free_periods, schedule_statistics
from schedule_optimizer import ranked_schedules
from campus_map import check_travel_feasibility
from event_manager import handle_dynamic_event, replan_schedule


def print_courses(system):
    print("\nCourses")
    print("-" * 80)
    for c in sorted(system.courses.values(), key=lambda x: x.code):
        slots = ", ".join(f"D{s.day}-{s.period}" for s in c.timeslots)
        print(f"{c.code:7} | {c.name:25} | {c.credits} cr | {slots:20} | seats {c.remaining_seats}")


def show_schedule(system, student_id):
    student = system.students.get(student_id)
    if not student:
        print("Student not found.")
        return
    table = build_weekly_schedule(student, system.courses, system.activities)
    print("\nWeekly Schedule")
    print("Period | " + " | ".join(f"Day {d}" for d in range(1, 8)))
    print("-" * 110)
    periods = [str(i) for i in range(1,10)] + ["a","b","c"]
    for p in periods:
        row = []
        for d in range(1,8):
            row.append(",".join(table[d][p]) if table[d][p] else "-")
        print(f"{p:>6} | " + " | ".join(f"{x:12}" for x in row))


def menu():
    print("""
================ NTUT Course Planning System ================
1. List courses
2. Search courses
3. Enroll course
4. Withdraw course
5. Show personal schedule
6. Find free periods
7. Show schedule statistics
8. Find suitable classroom for activity
9. Find shortest campus path
10. Check travel feasibility
11. Recommend schedules
12. Simulate dynamic event
13. Save data
0. Exit
=============================================================
""")


def main():
    system = CampusSystem("data")
    while True:
        menu()
        choice = input("Select: ").strip()

        try:
            if choice == "1":
                print_courses(system)

            elif choice == "2":
                teacher = input("Teacher keyword (blank = any): ").strip() or None
                day_text = input("Day 1-7 (blank = any): ").strip()
                day = int(day_text) if day_text else None
                result = system.course_manager.search(teacher=teacher, day=day)
                for c in result:
                    print(c.code, c.name, c.teacher, c.remaining_seats)

            elif choice == "3":
                sid = input("Student ID: ").strip()
                code = input("Course code: ").strip()
                student = system.students.get(sid)
                course = system.courses.get(code)
                if not student or not course:
                    print("Student or course not found.")
                else:
                    ok, issues = enroll_student(student, course, system.courses, system.activities)
                    print("Enrollment successful." if ok else f"Enrollment failed: {issues}")

            elif choice == "4":
                sid = input("Student ID: ").strip()
                code = input("Course code: ").strip()
                student = system.students.get(sid)
                course = system.courses.get(code)
                if student and course:
                    withdraw_student(student, course)
                    print("Withdrawn.")
                else:
                    print("Student or course not found.")

            elif choice == "5":
                show_schedule(system, input("Student ID: ").strip())

            elif choice == "6":
                sid = input("Student ID: ").strip()
                day = int(input("Day 1-7: "))
                min_len = int(input("Minimum consecutive periods: "))
                s = system.students[sid]
                print(query_free_periods(s, system.courses, system.activities, day, min_length=min_len))

            elif choice == "7":
                sid = input("Student ID: ").strip()
                print(schedule_statistics(system.students[sid], system.courses, system.activities))

            elif choice == "8":
                code = input("Activity code: ").strip()
                activity = system.activities[code]
                suitable, rejected = system.activity_manager.suitable_classrooms(
                    activity, system.classrooms, system.courses
                )
                print("Suitable:", suitable)
                if not suitable:
                    print("Rejected reasons:", rejected)

            elif choice == "9":
                start = input("Start building: ").strip()
                goal = input("Destination building: ").strip()
                path, minutes = system.campus_map.dijkstra(start, goal)
                print("Path:", " -> ".join(path) if path else "No path")
                print("Minutes:", minutes)

            elif choice == "10":
                start = input("Previous building: ").strip()
                goal = input("Next building: ").strip()
                break_minutes = int(input("Available break minutes: "))
                print(check_travel_feasibility(start, goal, break_minutes, system.campus_map))

            elif choice == "11":
                codes = input("Candidate course codes (comma separated): ").split(",")
                candidates = [system.courses[c.strip()] for c in codes if c.strip() in system.courses]
                required = [x.strip() for x in input("Required codes: ").split(",") if x.strip()]
                min_cr = int(input("Minimum credits: "))
                max_cr = int(input("Maximum credits: "))
                ranked, nodes = ranked_schedules(candidates, min_cr, max_cr, required, top_n=5)
                print("Search nodes:", nodes)
                for i, (sch, score) in enumerate(ranked, 1):
                    print(i, [c.code for c in sch], "score=", score)

            elif choice == "12":
                print("Types: course_full / teacher_time_change / classroom_unavailable / mandatory_activity")
                typ = input("Event type: ").strip()
                if typ == "course_full":
                    event = {"type": typ, "course_code": input("Course code: ").strip()}
                elif typ == "classroom_unavailable":
                    event = {"type": typ, "classroom": input("Classroom: ").strip()}
                elif typ == "mandatory_activity":
                    event = {"type": typ, "activity_code": input("Activity code: ").strip()}
                elif typ == "teacher_time_change":
                    code = input("Course code: ").strip()
                    day = int(input("New day: "))
                    period = input("New period: ").strip()
                    event = {"type": typ, "course_code": code, "timeslots": [{"day": day, "period": period}]}
                else:
                    raise ValueError("unsupported event")
                print(handle_dynamic_event(event, system.courses, system.classrooms, system.activities))

            elif choice == "13":
                system.save()
                print("Saved.")

            elif choice == "0":
                system.save()
                print("Saved. Goodbye.")
                break

            else:
                print("Invalid selection.")
        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    main()
