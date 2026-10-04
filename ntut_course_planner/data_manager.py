import json
from pathlib import Path
from typing import Dict, Any


def load_json(path, default):
    path = Path(path)
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


def save_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class DataStore:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)

    def load_all(self):
        return {
            "courses": load_json(self.data_dir / "courses.json", []),
            "students": load_json(self.data_dir / "students.json", []),
            "classrooms": load_json(self.data_dir / "classrooms.json", []),
            "activities": load_json(self.data_dir / "activities.json", []),
            "campus_graph": load_json(self.data_dir / "campus_graph.json", {"nodes": [], "edges": []}),
        }

    def save_all(self, courses, students, classrooms, activities, campus_graph):
        save_json(self.data_dir / "courses.json", [x.to_dict() for x in courses.values()])
        save_json(self.data_dir / "students.json", [x.to_dict() for x in students.values()])
        save_json(self.data_dir / "classrooms.json", [x.to_dict() for x in classrooms.values()])
        save_json(self.data_dir / "activities.json", [x.to_dict() for x in activities.values()])
        save_json(self.data_dir / "campus_graph.json", campus_graph)
