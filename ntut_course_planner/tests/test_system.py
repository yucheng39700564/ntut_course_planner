import json
import pytest
from pathlib import Path

from models import TimeSlot, Course, Student, Classroom, Activity
from course_manager import CourseManager
from student_manager import StudentManager
from conflict_checker import find_overlaps, check_enrollment, enroll_student, withdraw_student
from schedule_manager import build_weekly_schedule, query_free_periods, schedule_statistics
from activity_manager import ActivityManager
from course_filter import filter_courses
from schedule_optimizer import schedule_is_feasible, exhaustive_search, backtracking_search, ranked_schedules
from campus_map import CampusMap, check_travel_feasibility
from event_manager import handle_dynamic_event, replan_schedule
from data_manager import load_json, save_json


def course(code, slots, credits=3, capacity=30, enrolled=None, required=False):
    return Course(code, code, credits, required, "T", capacity, "R",
                  [TimeSlot(d,p) for d,p in slots], enrolled or [])


# ---------- Normal cases (>= 10) ----------
def test_01_valid_timeslot():
    s = TimeSlot(1,"1"); s.validate(); assert s.key() == (1,"1")

def test_02_add_course():
    m = CourseManager(); c = course("C1", [(1,"1")]); m.add_course(c); assert m.get("C1") is c

def test_03_add_student():
    m = StudentManager(); s = Student("S1","A","CS",24); m.add_student(s); assert m.get("S1") is s

def test_04_course_search_teacher():
    m = CourseManager({"C1": Course("C1","X",3,False,"Alice",30,"R",[TimeSlot(1,"1")],[])})
    assert len(m.search(teacher="ali")) == 1

def test_05_no_overlap():
    assert find_overlaps([TimeSlot(1,"1")],[TimeSlot(1,"2")]) == []

def test_06_successful_enrollment():
    c = course("C1",[(1,"1")]); s = Student("S1","A","CS",24)
    ok, issues = enroll_student(s,c,{"C1":c},{})
    assert ok and "C1" in s.selected_courses and "S1" in c.enrolled_students

def test_07_withdraw():
    c = course("C1",[(1,"1")],enrolled=["S1"]); s = Student("S1","A","CS",24,["C1"],[])
    withdraw_student(s,c); assert not s.selected_courses and not c.enrolled_students

def test_08_build_schedule():
    c = course("C1",[(2,"3")]); s = Student("S1","A","CS",24,["C1"],[])
    table = build_weekly_schedule(s,{"C1":c},{})
    assert table[2]["3"] == ["COURSE:C1"]

def test_09_free_periods():
    c = course("C1",[(1,"3")]); s = Student("S1","A","CS",24,["C1"],[])
    free = query_free_periods(s,{"C1":c},{},1,"1","5",2)
    assert ["1","2"] in free and ["4","5"] in free

def test_10_statistics():
    c = course("C1",[(1,"1"),(1,"2")],credits=3); s=Student("S1","A","CS",24,["C1"],[])
    st = schedule_statistics(s,{"C1":c},{})
    assert st["weekly_credits"] == 3 and st["daily_occupied_periods"][1] == 2

def test_11_activity_suitable_room():
    a = Activity("A","A",1,["1"],20,"x",["projector"],"",[],False)
    am = ActivityManager({"A":a})
    rooms={"R":Classroom("R",30,["projector"],"B")}
    ok,_=am.suitable_classrooms(a,rooms,{})
    assert ok == ["R"]

def test_12_filter_courses():
    c1=course("C1",[(1,"1")]); c2=course("C2",[(2,"1")])
    out,miss=filter_courses({"C1":c1,"C2":c2},forbidden_slots=[(1,"1")])
    assert [c.code for c in out] == ["C2"]

def test_13_feasible_schedule():
    a=course("A",[(1,"1")]); b=course("B",[(2,"1")])
    assert schedule_is_feasible([a,b],6,6,["A"])

def test_14_exhaustive_and_backtracking_same_solution_set():
    cs=[course("A",[(1,"1")]),course("B",[(2,"1")]),course("C",[(3,"1")])]
    e,_=exhaustive_search(cs,3,6)
    b,_=backtracking_search(cs,3,6)
    es={tuple(sorted(x.code for x in s)) for s in e}
    bs={tuple(sorted(x.code for x in s)) for s in b}
    assert es == bs

def test_15_dijkstra():
    g={"nodes":["A","B","C"],"edges":[{"from":"A","to":"B","minutes":2},{"from":"B","to":"C","minutes":3},{"from":"A","to":"C","minutes":10}]}
    path,cost=CampusMap(g).dijkstra("A","C")
    assert path==["A","B","C"] and cost==5

# ---------- Boundary cases (>= 10) ----------
def test_16_day_7_valid():
    s=TimeSlot(7,"c"); s.validate(); assert s.day == 7

def test_17_capacity_one_valid():
    c=course("C1",[(1,"1")],capacity=1); c.validate(); assert c.capacity==1

def test_18_exact_credit_limit_allowed():
    c=course("C1",[(1,"1")],credits=3); s=Student("S","A","CS",3)
    assert check_enrollment(s,c,{"C1":c},{}) == []

def test_19_one_remaining_seat_allowed():
    c=course("C1",[(1,"1")],capacity=2,enrolled=["X"]); s=Student("S","A","CS",24)
    assert not any(x["type"]=="course_full" for x in check_enrollment(s,c,{"C1":c},{}))

def test_20_minimum_free_length_one():
    s=Student("S","A","CS",24); free=query_free_periods(s,{}, {},1,"1","1",1)
    assert free == [["1"]]

def test_21_activity_exact_capacity_room():
    a=Activity("A","A",1,["1"],30,"x",[],"",[],False)
    am=ActivityManager({"A":a}); rooms={"R":Classroom("R",30,[],"B")}
    ok,_=am.suitable_classrooms(a,rooms,{})
    assert ok == ["R"]

def test_22_required_only_schedule():
    c=course("R",[(1,"1")],credits=3,required=True)
    assert schedule_is_feasible([c],3,3,["R"])

def test_23_zero_min_credits_allows_empty():
    out,_=exhaustive_search([course("A",[(1,"1")])],0,0)
    assert any(len(x)==0 for x in out)

def test_24_bfs_start_is_goal():
    g={"nodes":["A"],"edges":[]}; assert CampusMap(g).bfs("A","A")==["A"]

def test_25_travel_exact_break_is_feasible():
    g={"nodes":["A","B"],"edges":[{"from":"A","to":"B","minutes":10}]}
    out=check_travel_feasibility("A","B",10,CampusMap(g))
    assert out["feasible"] is True

def test_26_ranked_top_n():
    cs=[course("A",[(1,"1")]),course("B",[(2,"1")]),course("C",[(3,"1")])]
    ranked,_=ranked_schedules(cs,3,6,top_n=2)
    assert len(ranked)<=2

# ---------- Error / conflict cases (>= 10) ----------
def test_27_invalid_day():
    with pytest.raises(ValueError): TimeSlot(0,"1").validate()

def test_28_invalid_period():
    with pytest.raises(ValueError): TimeSlot(1,"z").validate()

def test_29_duplicate_course():
    m=CourseManager(); c=course("C1",[(1,"1")]); m.add_course(c)
    with pytest.raises(ValueError): m.add_course(course("C1",[(2,"1")]))

def test_30_duplicate_student():
    m=StudentManager(); m.add_student(Student("S","A","CS",24))
    with pytest.raises(ValueError): m.add_student(Student("S","B","CS",24))

def test_31_delete_enrolled_course_rejected():
    m=CourseManager({"C":course("C",[(1,"1")],enrolled=["S"])})
    with pytest.raises(ValueError): m.delete_course("C")

def test_32_course_conflict_detected():
    c1=course("C1",[(1,"1")]); c2=course("C2",[(1,"1")]); s=Student("S","A","CS",24,["C1"],[])
    issues=check_enrollment(s,c2,{"C1":c1,"C2":c2},{})
    assert any(x["type"]=="course_conflict" for x in issues)

def test_33_activity_conflict_detected():
    c=course("C",[(1,"1")]); a=Activity("A","A",1,["1"],20,"x",[],"",[],False)
    s=Student("S","A","CS",24,[],["A"])
    issues=check_enrollment(s,c,{"C":c},{"A":a})
    assert any(x["type"]=="activity_conflict" for x in issues)

def test_34_credit_limit_detected():
    c1=course("C1",[(1,"1")],credits=3); c2=course("C2",[(2,"1")],credits=3)
    s=Student("S","A","CS",5,["C1"],[])
    issues=check_enrollment(s,c2,{"C1":c1,"C2":c2},{})
    assert any(x["type"]=="credit_limit" for x in issues)

def test_35_full_course_detected():
    c=course("C",[(1,"1")],capacity=1,enrolled=["X"]); s=Student("S","A","CS",24)
    issues=check_enrollment(s,c,{"C":c},{})
    assert any(x["type"]=="course_full" for x in issues)

def test_36_room_capacity_rejected():
    a=Activity("A","A",1,["1"],50,"x",[],"",[],False)
    am=ActivityManager({"A":a}); rooms={"R":Classroom("R",20,[],"B")}
    ok,rejected=am.suitable_classrooms(a,rooms,{})
    assert not ok and "insufficient_capacity" in rejected["R"]

def test_37_missing_equipment_rejected():
    a=Activity("A","A",1,["1"],10,"x",["microphone"],"",[],False)
    am=ActivityManager({"A":a}); rooms={"R":Classroom("R",20,[],"B")}
    ok,rejected=am.suitable_classrooms(a,rooms,{})
    assert not ok

def test_38_infeasible_conflicting_schedule():
    a=course("A",[(1,"1")]); b=course("B",[(1,"1")])
    assert not schedule_is_feasible([a,b],6,6)

def test_39_unknown_dijkstra_node():
    g={"nodes":["A"],"edges":[]}
    with pytest.raises(KeyError): CampusMap(g).dijkstra("A","X")

def test_40_bad_json_returns_default(tmp_path):
    p=tmp_path/"bad.json"; p.write_text("{bad",encoding="utf-8")
    assert load_json(p,[]) == []

def test_41_dynamic_course_full():
    c=course("C",[(1,"1")],capacity=2)
    out=handle_dynamic_event({"type":"course_full","course_code":"C"},{"C":c},{},{})
    assert out["changed"] and c.remaining_seats==0

def test_42_replan_no_solution():
    c=course("C",[(1,"1")],credits=3,capacity=1,enrolled=["X"])
    out=replan_schedule([c],3,3,["C"])
    assert out["success"] is False

def test_43_invalid_free_range():
    s=Student("S","A","CS",24)
    with pytest.raises(ValueError):
        query_free_periods(s,{}, {},1,"5","1",1)
