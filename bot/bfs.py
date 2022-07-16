from __future__ import annotations

import sys
from collections import deque

from client.message.extra_types import XY

from .constants import X, Y, MAP_CHAR_BLOCKS
from .dead_end_filler import DeadEndFiller
from .map import Map
from .map_utils import MapUtilsMixin
from .neighbours_cache import NeighboursCache


class BFS(MapUtilsMixin):
    breadth_limit = 20

    def __init__(self, size: XY, game_map: Map, dead_end_filler: DeadEndFiller):
        self.size: XY = size
        self._map: Map = game_map
        self._dead_end_filler: DeadEndFiller = dead_end_filler
        self._neighbours: NeighboursCache = NeighboursCache(size)
        self.nodes: dict[XY, int] = dict()
        self.pts_near_unknown: set[XY] = set()

    def __contains__(self, pt: XY) -> bool:
        return pt in self.nodes

    def __getitem__(self, pt: XY) -> int | None:
        return self.nodes.get(pt)

    def update(self, bot: XY) -> None:
        self.nodes.clear()
        self.pts_near_unknown.clear()
        queue: deque[XY] = deque([bot])
        self.nodes[bot] = 0
        while queue:
            pt = queue.popleft()
            if self._map.is_my_block(pt):
                continue
            step = self.nodes[pt]
            blocks_around = 0
            for next_pt in self._neighbours.cache[pt]:
                if self._map.in_blocks(next_pt):
                    blocks_around += 1
                    continue
                if self._map.is_unknown(next_pt):
                    self.pts_near_unknown.add(pt)  # TODO: what use of it?
                    continue
                if step < self.breadth_limit and next_pt not in self.nodes:
                    self.nodes[next_pt] = step + 1
                    queue.append(next_pt)
            if blocks_around >= 4 and self._map.is_empty(pt) \
                    and pt not in self._map.coins_map \
                    and pt in self._map.visible:
                self._dead_end_filler.fill(pt, blocks_around)

    def collect_tree(self, pt, step, collection):
        for next_pt in self._neighbours.cache[pt]:
            next_step = self.nodes.get(next_pt, sys.maxsize)
            if next_step < step and next_pt not in collection:
                collection.add(next_pt)
                if next_step == 0:
                    return
                self.collect_tree(next_pt, next_step, collection)

    def find_coins(
            self, from_pt: XY, coins_exclude: set[XY], coins_limit: int
    ) -> list[tuple[XY, XY, int]]:
        nearest_coins: list[tuple[XY, XY, int]] = []
        visited: set[XY] = {from_pt}
        coins_seen: dict[XY, int] = {}
        queue: deque[tuple[XY, int]] = deque([(from_pt, 0)])
        while queue:
            pt, step = queue.popleft()
            for coin in self._map.coins_map.get(pt, []):
                if coin not in coins_exclude and coins_seen.get(coin, step) == step:
                    nearest_coins.append((coin, pt, step))
                    coins_seen[coin] = step
            if len(coins_seen) >= coins_limit:
                break
            for next_pt in self._neighbours.cache[pt]:
                if self._map.grid[next_pt[Y]][next_pt[X]] in MAP_CHAR_BLOCKS:
                    continue
                if step < 10 and next_pt not in visited:
                    queue.append((next_pt, step + 1))
                    visited.add(next_pt)
        return nearest_coins

    def print(self) -> None:
        for y in range(self.size[Y] - 1, -1, -1):
            print(''.join(
                str(value).rjust(2) if (value := self.nodes.get((x, y))) else '..'
                for x in range(self.size[X])
            ))

    def export(self, canvas: list[list[str]]) -> None:
        for pt, value in self.nodes.items():
            if value:
                canvas[pt[Y]][pt[X]] = str(value % 10)
