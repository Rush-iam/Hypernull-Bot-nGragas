from __future__ import annotations

import sys
from collections import defaultdict
from heapq import heappop, heappush

from client.message.extra_types import XY

from .constants import X, Y
from .map import Map
from .map_utils import MapUtilsMixin


class AStar(MapUtilsMixin):
    def __init__(self, size: XY, game_map: Map):
        self.size: XY = size
        self._map: Map = game_map
        self.nodes: dict[XY, int] = defaultdict(lambda: sys.maxsize)
        self.last_path: list[XY] = []

    def get_path(self, start: XY, end: XY) -> list[XY] | None:
        path = self._traverse(start, end)
        self.last_path = path
        return path

    def _traverse(self, start: XY, end: XY) -> list[XY] | None:
        self.nodes.clear()
        if start == end:
            return [start]
        diff = self.position_diff(start, end)
        if max(abs(diff[X]), abs(diff[Y])) == 1:
            return [end]

        heap: list[tuple[int, XY]] = [(self.distance(start, end), start)]
        came_from: dict[XY, XY] = {}
        self.nodes[start] = 0
        while heap:
            _, pt = heappop(heap)
            step = self.nodes[pt]
            for next_pt in self.neighbours(pt):
                if next_pt == end:
                    came_from[next_pt] = pt
                    return self._reconstruct_path(next_pt, came_from)
                if self._map.in_blocks(next_pt):
                    continue
                if self.nodes[next_pt] > step + 1:
                    self.nodes[next_pt] = step + 1
                    came_from[next_pt] = pt
                    score = self.distance(next_pt, end) + (step + 1)
                    heappush(heap, (score, next_pt))
        return None

    @staticmethod
    def _reconstruct_path(pt: XY, came_from: dict[XY, XY]) -> list[XY]:
        path: list[XY] = []
        while pt in came_from:
            path.append(pt)
            pt = came_from[pt]
        return path[::-1]

    def export(self, canvas: list[list[str]]) -> None:
        for pt, value in self.nodes.items():
            if value:
                canvas[pt[Y]][pt[X]] = str(value % 10)
