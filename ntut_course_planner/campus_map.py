import heapq
from collections import deque


class CampusMap:
    def __init__(self, graph_data):
        self.graph = {}
        for node in graph_data.get("nodes", []):
            self.graph.setdefault(node, [])
        for edge in graph_data.get("edges", []):
            a, b, minutes = edge["from"], edge["to"], edge["minutes"]
            self.graph.setdefault(a, []).append((b, minutes))
            self.graph.setdefault(b, []).append((a, minutes))

    def bfs(self, start, goal):
        if start not in self.graph or goal not in self.graph:
            raise KeyError("unknown location")
        q = deque([(start, [start])])
        seen = {start}
        while q:
            node, path = q.popleft()
            if node == goal:
                return path
            for nxt, _ in self.graph[node]:
                if nxt not in seen:
                    seen.add(nxt)
                    q.append((nxt, path + [nxt]))
        return None

    def dijkstra(self, start, goal):
        if start not in self.graph or goal not in self.graph:
            raise KeyError("unknown location")
        pq = [(0, start, [start])]
        best = {start: 0}
        while pq:
            cost, node, path = heapq.heappop(pq)
            if node == goal:
                return path, cost
            if cost > best.get(node, float("inf")):
                continue
            for nxt, w in self.graph[node]:
                nc = cost + w
                if nc < best.get(nxt, float("inf")):
                    best[nxt] = nc
                    heapq.heappush(pq, (nc, nxt, path + [nxt]))
        return None, float("inf")


def check_travel_feasibility(previous_building, next_building, break_minutes, campus_map):
    path, travel = campus_map.dijkstra(previous_building, next_building)
    return {
        "feasible": travel <= break_minutes,
        "travel_minutes": travel,
        "break_minutes": break_minutes,
        "path": path
    }
