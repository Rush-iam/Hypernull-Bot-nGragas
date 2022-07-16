from client.message.extra_types import XY

from .constants import X, Y
from .map_utils import MapUtilsMixin


class NeighboursCache(MapUtilsMixin):
    def __init__(self, size: XY):
        self.size: XY = size
        self.cache: dict[XY, list[XY]] = self._generate_neighbours()

    def __contains__(self, pt: XY) -> bool:
        return pt in self.cache

    def __getitem__(self, pt: XY) -> list[XY]:
        return self.cache[pt]

    def _generate_neighbours(self) -> dict[XY, list[XY]]:
        neighbours = dict()
        for y in range(self.size[Y]):
            for x in range(self.size[X]):
                pt = (x, y)
                if pt == (0, 0):
                    neighbours[pt] = [pt for pt in self.neighbours(pt)]
                else:
                    neighbours[pt] = [
                        self.position_add(zero_pt, (x, y))
                        for zero_pt in neighbours[(0, 0)]
                    ]
        return neighbours
