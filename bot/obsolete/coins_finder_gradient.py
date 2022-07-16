from __future__ import annotations

import sys
from collections import defaultdict

from client.message.extra_types import XY

from bot.bfs import BFS
from bot.constants import DIRECTIONS
from bot.map_utils import MapUtilsMixin


class CoinsFinderGradient(MapUtilsMixin):
    def __init__(self, size: XY, coins_map: dict[XY, list[XY]],
                 coins_pts: dict[XY: list[XY]], bfs: BFS):
        self.size: XY = size
        self._coins_map: dict[XY, list[XY]] = coins_map
        self._coins_pts: dict[XY: list[XY]] = coins_pts
        self._bfs: BFS = bfs
        self._gradient: dict[XY, float] = defaultdict(float)

    def best_from_gradient(self, bot: XY) -> list[XY] | None:
        self._update_gradient()
        if not self._gradient:
            return None

        if any(pt in self._coins_map for pt in self.neighbours(bot)):
            bump_mask: list[tuple[XY, float]] = []
            for direction in DIRECTIONS:
                pt = self.position_add(bot, direction)
                if pt in self._gradient:
                    opposite_pt = self.position_sub(bot, direction)
                    bump_mask.append((opposite_pt, self._gradient[pt]))
            for pt, bump in bump_mask:
                self._gradient[pt] -= bump / 2

        best_score: float = 0.0
        best_pts: list[XY] = []
        for pt in self.neighbours(bot):
            if pt in self._gradient:
                if best_score == self._gradient[pt]:
                    best_pts.append(pt)
                elif best_score < self._gradient[pt]:
                    best_pts = [pt]
                    best_score = self._gradient[pt]
        return best_pts

    def _update_gradient(self):
        self._gradient.clear()
        for coin, pts in self._get_nearest_coins_pts().items():
            for pt in pts:
                steps = self._bfs[pt]
                visited = {pt}
                self._bfs.collect_tree(pt, steps, visited)
                for path_pt in visited:
                    step = self._bfs[path_pt]
                    if step == steps:
                        self._gradient[path_pt] += 1.0
                    else:
                        self._gradient[path_pt] += (2 ** (step - steps)) / len(pts)

    def _get_nearest_coins_pts(self) -> dict[XY, list[XY]]:
        nearest_coins_pts: dict[XY, list[XY]] = {}
        for coin, pts in self._coins_pts.items():
            nearest_steps: int = sys.maxsize
            nearest_pts: list[XY] = []
            for pt in pts:
                if pt not in self._bfs.nodes:
                    continue
                if nearest_steps == self._bfs[pt]:
                    nearest_pts.append(pt)
                elif nearest_steps > self._bfs[pt]:
                    nearest_pts = [pt]
                    nearest_steps = self._bfs[pt]
            if nearest_pts:
                nearest_coins_pts[coin] = nearest_pts
        return nearest_coins_pts

    def print_gradient(self, bot: XY, view_radius: int) -> None:
        for y in range(view_radius, -view_radius - 1, -1):
            for x in range(-view_radius, view_radius):
                if x == 0 and y == 0:
                    print(' !  ', end='')
                    continue
                pt = self.position_add(bot, (x, y))
                print(f'{val:.1f} ' if (val := self._gradient.get(pt)) else '....', end='')
            print()
