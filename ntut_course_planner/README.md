# NTUT Course Planning System

A command-line Python project for the group assignment.

## Features
- F1 Course / student data management
- F2 Multi-level conflict and enrollment checking
- F3 Personal timetable and free-period queries
- F4 Campus activities and classroom assignment
- F5 Multi-condition course filtering
- F6 JSON persistence and automated tests
- F7 Multi-condition best timetable search
- F8 Exhaustive vs. backtracking search
- F9 Campus shortest-path planning (BFS / Dijkstra)
- F10 Dynamic event simulation and replanning
- F11 Test / quality support through modular design

## Run
```bash
python main.py
```

## Test
Install pytest if necessary:
```bash
pip install pytest
```

Then:
```bash
pytest -q
```

## Data
Sample data are stored in `data/`.

The campus building names are based on Taipei Tech's official campus map.
The graph edge travel times in `campus_graph.json` are **assignment test assumptions**,
not official measured walking times.

## Design notes
- No global system state is used.
- Core logic is separated into independently testable modules.
- CLI is only a presentation layer.
- JSON data can be reloaded after restart.
