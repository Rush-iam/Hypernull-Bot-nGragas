from __future__ import annotations

import sys
from collections import defaultdict

from client.message.extra_types import XY

from .bfs import BFS
from .map_utils import MapUtilsMixin


class CoinsFinderGraph(MapUtilsMixin):
    _bot_find_coins_limit: int = 3
    _coin_find_coins_limit: int = 2
    _depth_limit: int = 5

    def __init__(self, size: XY, coins_pts: dict[XY: list[XY]], visible: set[XY], bfs: BFS):
        self.size: XY = size
        self._coins_pts: dict[XY: list[XY]] = coins_pts
        self._visible: set[XY] = visible
        self._bfs: BFS = bfs
        self._edges: dict[tuple[XY, XY], dict[tuple[XY, XY], int]] = defaultdict(dict)

    def get_best_pts(self, bot: XY) -> list[XY] | None:
        path = self.get_best_path(bot)
        if len(path) <= 1:
            return None
        target = path[1]
        steps = self._bfs[target]
        visited = {target}
        self._bfs.collect_tree(target, steps, visited)
        return [pt for pt in visited if self._bfs[pt] == 1]

    def get_best_path(self, bot: XY) -> list[XY]:
        self._edges.clear()
        near_bot_coins = self._find_coins_near_bot(self._bot_find_coins_limit)
        for coin, coin_pts, steps in near_bot_coins:
            for coin_pt in coin_pts:
                self._edges[(bot, bot)][(coin, coin_pt)] = steps
                self._create_coins_graph(coin, coin_pt)

        return self._find_best_path(bot)

    def _find_coins_near_bot(self, limit: int) -> list[tuple[XY, list[XY], int]]:
        nearest_coins: list[tuple[XY, list[XY], int]] = []
        for coin, pts in self._coins_pts.items():
            nearest_steps: int = sys.maxsize
            nearest_pts: list[XY] = []
            for pt in pts:
                if pt not in self._bfs or pt not in self._visible:
                    continue
                if nearest_steps == self._bfs[pt]:
                    nearest_pts.append(pt)
                elif nearest_steps > self._bfs[pt]:
                    nearest_pts = [pt]
                    nearest_steps = self._bfs[pt]
            if nearest_pts:
                nearest_coins.append((coin, nearest_pts, nearest_steps))
        return sorted(nearest_coins, key=lambda n: n[2])[:limit]

    def _create_coins_graph(self, from_coin: XY, from_coin_pt: XY):
        coins_visited: set[XY] = set()

        def create(coin: XY, coin_pt: XY, cur_depth: int = 1) -> None:
            coins_visited.add(coin)
            nearest_coins = self._bfs.find_coins(
                coin_pt, coins_visited, self._coin_find_coins_limit
            )
            for to_coin, to_coin_pt, to_steps in nearest_coins:
                self._edges[(coin, coin_pt)][(to_coin, to_coin_pt)] = to_steps
                if cur_depth < self._depth_limit:
                    create(to_coin, to_coin_pt, cur_depth + 1)
            coins_visited.remove(coin)

        create(from_coin, from_coin_pt)

    def _find_best_path(self, bot: XY) -> list[XY]:
        path: list[XY] = []
        path_coins: set[XY] = set()
        best_path: list[XY] = []
        best_cost: float = float('inf')

        def find(coin: XY, coin_pt: XY, total_steps: int = 0) -> None:
            nonlocal best_path, best_cost
            path.append(coin_pt)
            path_coins.add(coin)

            if len(path) > 1:
                cost = total_steps / (len(path) - 1)
                if cost < best_cost:
                    best_path = path.copy()
                    best_cost = cost
            for next_coin_next_pt, steps in self._edges[(coin, coin_pt)].items():
                next_coin, next_pt = next_coin_next_pt
                if next_coin not in path_coins:
                    find(next_coin, next_pt, total_steps + steps)

            path_coins.remove(coin)
            path.pop()

        find(bot, bot)
        return best_path
