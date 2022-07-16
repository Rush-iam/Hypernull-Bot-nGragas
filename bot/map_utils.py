import math
from typing import Generator

from client.message.extra_types import XY

from .constants import X, Y, DIRECTIONS


class MapUtilsMixin:
    size: XY

    def position_diff(self, pt1: XY, pt2: XY) -> XY:
        diff = [0, 0]
        for i in range(2):
            if pt1[i] != pt2[i]:
                d1 = (pt2[i] - pt1[i]) % self.size[i]
                d2 = d1 - self.size[i]
                diff[i] = d1 if abs(d1) < abs(d2) else d2
        return diff[0], diff[1]

    def position_add(self, pt: XY, diff: XY) -> XY:
        return (
            (pt[X] + diff[X]) % self.size[X],
            (pt[Y] + diff[Y]) % self.size[Y],
        )

    def position_sub(self, pt: XY, diff: XY) -> XY:
        return (
            (pt[X] - diff[X]) % self.size[X],
            (pt[Y] - diff[Y]) % self.size[Y],
        )

    def distance(self, pt1: XY, pt2: XY) -> int:
        return max(map(abs, self.position_diff(pt1, pt2)))

    def distance_euclidean(self, pt1: XY, pt2: XY) -> float:
        dx = abs(pt1[X] - pt2[X])
        dy = abs(pt1[Y] - pt2[Y])
        return math.hypot(
            min(dx, self.size[X] - dx),
            min(dy, self.size[Y] - dy),
        )

    def fit_to_map(self, pt: XY) -> XY:
        return pt[X] % self.size[X], pt[Y] % self.size[Y]

    def neighbours(
            self, pt: XY, directions: tuple[XY, ...] = DIRECTIONS
    ) -> Generator[XY, None, None]:
        return (self.position_add(pt, d) for d in directions)
