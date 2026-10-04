from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any


VALID_PERIODS = [str(i) for i in range(1, 10)] + ["a", "b", "c"]


@dataclass
class TimeSlot:
    day: int
    period: str

    def validate(self):
        if self.day not in range(1, 8):
            raise ValueError("day must be between 1 and 7")
        if str(self.period) not in VALID_PERIODS:
            raise ValueError("invalid period")
        self.period = str(self.period)

    def key(self):
        return (self.day, self.period)

    def to_dict(self):
        return asdict(self)


@dataclass
class Course:
    code: str
    name: str
    credits: int
    required: bool
    teacher: str
    capacity: int
    classroom: str
    timeslots: List[TimeSlot] = field(default_factory=list)
    enrolled_students: List[str] = field(default_factory=list)

    def validate(self):
        if not self.code.strip():
            raise ValueError("course code cannot be empty")
        if self.credits <= 0 or not isinstance(self.credits, int):
            raise ValueError("credits must be a positive integer")
        if self.capacity < 1:
            raise ValueError("capacity must be at least 1")
        for slot in self.timeslots:
            slot.validate()

    @property
    def remaining_seats(self):
        return self.capacity - len(self.enrolled_students)

    def to_dict(self):
        d = asdict(self)
        d["timeslots"] = [s.to_dict() for s in self.timeslots]
        return d

    @staticmethod
    def from_dict(d):
        return Course(
            code=d["code"],
            name=d["name"],
            credits=d["credits"],
            required=d["required"],
            teacher=d["teacher"],
            capacity=d["capacity"],
            classroom=d["classroom"],
            timeslots=[TimeSlot(**x) for x in d.get("timeslots", [])],
            enrolled_students=d.get("enrolled_students", []),
        )


@dataclass
class Student:
    student_id: str
    name: str
    department: str
    credit_limit: int
    selected_courses: List[str] = field(default_factory=list)
    activities: List[str] = field(default_factory=list)

    def validate(self):
        if not self.student_id.strip():
            raise ValueError("student id cannot be empty")
        if self.credit_limit <= 0:
            raise ValueError("credit limit must be positive")

    def to_dict(self):
        return asdict(self)


@dataclass
class Classroom:
    code: str
    capacity: int
    equipment: List[str] = field(default_factory=list)
    building: str = ""

    def validate(self):
        if self.capacity < 1:
            raise ValueError("classroom capacity must be at least 1")

    def to_dict(self):
        return asdict(self)


@dataclass
class Activity:
    code: str
    name: str
    day: int
    periods: List[str]
    capacity: int
    activity_type: str
    required_equipment: List[str] = field(default_factory=list)
    classroom: str = ""
    participants: List[str] = field(default_factory=list)
    cancelled: bool = False

    def validate(self):
        if self.day not in range(1, 8):
            raise ValueError("day must be between 1 and 7")
        for p in self.periods:
            if str(p) not in VALID_PERIODS:
                raise ValueError("invalid period")
        if self.capacity < 1:
            raise ValueError("activity capacity must be at least 1")

    @property
    def remaining_seats(self):
        return self.capacity - len(self.participants)

    def timeslots(self):
        return [TimeSlot(self.day, str(p)) for p in self.periods]

    def to_dict(self):
        return asdict(self)
