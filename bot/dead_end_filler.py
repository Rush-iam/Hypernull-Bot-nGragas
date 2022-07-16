from client.message.extra_types import XY

from .constants import MapChar, DIRECTIONS_XY_OPTIMAL, DIRECTIONS_ROUND, X, Y
from .map import Map
from .map_utils import MapUtilsMixin


class DeadEndFiller(MapUtilsMixin):
    def __init__(self, size: XY, game_map: Map):
        self.size: XY = size
        self._map: Map = game_map

    def fill(self, pt: XY, blocks_around: int = 0) -> None:
        if blocks_around == 7 or self._is_safe_to_block(pt):
            self._map[pt[Y]][pt[X]] = MapChar.MY_BLOCK
            for new_pt in self.neighbours(pt, DIRECTIONS_XY_OPTIMAL):
                if self._map.is_empty(new_pt) and pt not in self._map.coins_map \
                        and pt in self._map.visible:
                    self.fill(new_pt)

    def _is_safe_to_block(self, pt: XY) -> bool:
        blocks_around = 0
        way_out_found = False
        way_out_found_from_start = False
        ways_out = 0
        ways_out_arr = []
        for new_pt in self.neighbours(pt, DIRECTIONS_ROUND):
            if new_pt in self._map.visible:
                is_block = self._map.in_blocks(new_pt)
            else:
                is_block = self._map.is_block(new_pt)

            if is_block:
                ways_out += way_out_found
                way_out_found = False
                blocks_around += 1
            else:
                if len(ways_out_arr) < 2:
                    ways_out_arr.append(new_pt)
                way_out_found = True
                if blocks_around == 0:
                    way_out_found_from_start = True
        if not way_out_found_from_start:
            ways_out += way_out_found

        ways_out_connected = False
        if ways_out == 2 and blocks_around == 6:
            if self.distance(ways_out_arr[0], ways_out_arr[1]) == 1:
                ways_out_connected = True

        if ways_out_connected or (ways_out == 1 and blocks_around >= 4):
            return True
        return False
