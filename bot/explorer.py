from __future__ import annotations

from collections import defaultdict

from client.message.extra_types import XY

from .bfs import BFS
from .constants import MapChar, MAP_CHAR_BLOCKS, X, Y, DIRECTIONS
from .map import Map
from .map_utils import MapUtilsMixin


class Explorer(MapUtilsMixin):
    def __init__(self, size: XY, game_map: Map, bfs: BFS):
        self.size: XY = size
        self._map: Map = game_map
        self._bfs: BFS = bfs
        self.gradient_to_unknown: dict[XY, int] = defaultdict(int)

    # TODO: what use of it?
    def update_gradient_to_unknown(self):
        self.gradient_to_unknown.clear()
        pts = sorted(self._bfs.pts_near_unknown, key=lambda p: self._bfs[p])
        for edge_pt in pts:
            collection = set()
            step = self._bfs[edge_pt]
            self._bfs.collect_tree(edge_pt, step, collection)
            for pt in collection:
                self.gradient_to_unknown[pt] += 1

    def get_not_seen_dir(
            self, bot: XY, current_round: int, allowed_dirs: list[XY] | None
    ) -> XY:
        directions = allowed_dirs if allowed_dirs else DIRECTIONS

        best_direction = None
        best_direction_score = -1
        for direction in directions:
            pt = self.position_add(bot, direction)
            map_char = self._map[pt[Y]][pt[X]]
            if (allowed_dirs and map_char is MapChar.BLOCK) or \
                    (allowed_dirs is None and map_char in MAP_CHAR_BLOCKS):
                continue

            seen_score = 0
            for edge_out_pt in self._map.view_area.outside_edge[direction]:
                map_out_pt = self.position_add(bot, edge_out_pt)
                if not self._map.is_block(map_out_pt):
                    last_seen_round = self._map.last_seen[map_out_pt[Y]][map_out_pt[X]]
                    seen_score += current_round - last_seen_round

            if seen_score > best_direction_score:
                best_direction = direction
                best_direction_score = seen_score

        return best_direction
