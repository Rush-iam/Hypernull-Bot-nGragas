from __future__ import annotations

import sys

from client.message.extra_types import XY

from bot.bfs import BFS
from bot.map_utils import MapUtilsMixin


class CoinsFinderMap(MapUtilsMixin):
    def __init__(self, size: XY, coins_map: dict[XY, list[XY]], bfs: BFS):
        self.size: XY = size
        self._coins_map: dict[XY, list[XY]] = coins_map
        self._bfs: BFS = bfs

    def get_nearest_coin(self) -> XY | None:
        nearest_coin: XY | None = None
        for pt, coins in self._coins_map.items():
            if not coins:
                continue
            if steps := self._bfs[pt]:
                if not nearest_coin or steps < self._bfs[nearest_coin]:
                    nearest_coin = pt
        return nearest_coin

    def get_best_value_pts(self) -> list[XY] | None:
        nearest_amount: dict[int, list[XY]] = dict()
        for pt, coins in self._coins_map.items():
            if (steps := self._bfs[pt]) is None:
                continue
            if steps == 0:
                return self._get_coin_pts(pt)
            amount = len(coins)
            if amount not in nearest_amount or steps < self._bfs[nearest_amount[amount][0]]:
                nearest_amount[amount] = [pt]
            elif steps == self._bfs[nearest_amount[amount][0]]:
                nearest_amount[amount].append(pt)
        if not nearest_amount:
            return None

        best_value_pt: XY | None = None
        best_value: float = 0.0
        for amount, pts in nearest_amount.items():
            steps = self._bfs[pts[0]]  # TODO: better logic here?
            value = amount / steps
            if value > best_value:
                best_value_pt = pts[0]
                best_value = value

        return self._get_coin_pts(best_value_pt)

    def _get_coin_pts_bad(self, pt: XY) -> list[XY]:
        steps = self._bfs[pt]
        visited = {pt}
        self._bfs.collect_tree(pt, steps, visited)

        best_next_pt_amount = -1
        best_next_pts = []
        for path_pt in visited:
            next_step = self._bfs.nodes.get(path_pt, sys.maxsize)
            if next_step <= 1:
                next_pt_amount = len(self._coins_map.get(path_pt, []))
                if next_pt_amount > best_next_pt_amount:
                    best_next_pts = [path_pt]
                    best_next_pt_amount = next_pt_amount
                elif next_pt_amount == best_next_pt_amount:
                    best_next_pts.append(path_pt)
        return best_next_pts

    def _get_coin_pts(self, pt: XY) -> list[XY]:
        step = self._bfs[pt]
        while step > 2:
            best_next_pt_amount = -1
            best_next_pt = None
            for next_pt in self.neighbours(pt):
                next_step = self._bfs[next_pt]
                if next_step is not None and next_step < step:
                    next_pt_amount = len(self._coins_map.get(next_pt, []))
                    if next_pt_amount > best_next_pt_amount:
                        best_next_pt = next_pt
                        best_next_pt_amount = next_pt_amount
            pt, step = best_next_pt, step - 1

        best_next_pt_amount = -1
        best_next_pts = []
        for next_pt in pt, *self.neighbours(pt):
            next_step = self._bfs[next_pt]
            if next_step is not None and next_step <= 1:
                next_pt_amount = len(self._coins_map.get(next_pt, []))
                if next_pt_amount > best_next_pt_amount:
                    best_next_pts = [next_pt]
                    best_next_pt_amount = next_pt_amount
                elif next_pt_amount == best_next_pt_amount:
                    best_next_pts.append(next_pt)

        return best_next_pts
