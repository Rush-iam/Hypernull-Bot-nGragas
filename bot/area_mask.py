import math
from collections import defaultdict

from client.message.extra_types import XY

from .constants import DIRECTIONS, X, Y


class AreaMask:
    def __init__(self, radius: int):
        self.radius: int = radius
        self.mask: list[XY] = self._generate_mask(radius)
        self.outside_edge: dict[XY, list[XY]] = self._generate_outside_edge(
            mask_edge=self._get_mask_edge(radius, self.mask),
            mask_edge_diagonal=self._get_mask_edge_diagonal(set(self.mask))
        )

    def __iter__(self):
        return self.mask.__iter__()

    @staticmethod
    def _generate_mask(radius: int) -> list[XY]:
        mask = []
        for x in range(-radius, radius + 1):
            for y in range(-radius, radius + 1):
                if math.hypot(x, y) <= radius:
                    mask.append((x, y))
        return mask

    @staticmethod
    def _generate_outside_edge(
            mask_edge: list[XY],
            mask_edge_diagonal: list[XY]
    ) -> dict[XY, list[XY]]:
        outside_edge: dict[XY, list[XY]] = defaultdict(list)
        for direction in DIRECTIONS:
            if direction[X] == 0 or direction[Y] == 0:
                outside_edge[direction] = [
                    (pt[X], direction[Y] * (pt[Y] + 1)) if direction[X] == 0
                    else (direction[X] * (pt[Y] + 1), pt[X])
                    for pt in mask_edge
                ]
            else:
                outside_edge[direction] = [
                    (direction[X] * (pt[X] + 1), direction[Y] * (pt[Y] + 1))
                    for pt in mask_edge_diagonal
                ]
        return outside_edge

    @staticmethod
    def _get_mask_edge(radius: int, mask: list[XY]) -> list[XY]:
        mask_edge: list[XY] = []
        for i in range(radius + 1):
            mask_edge.append(max(v for v in mask if v[X] == i))
        for pt in mask_edge[1:]:
            mask_edge.append((-pt[X], pt[Y]))
        return mask_edge

    @staticmethod
    def _get_mask_edge_diagonal(mask_set: set[XY]) -> list[XY]:
        mask_edge_diagonal: list[XY] = []
        for pt in mask_set:
            if pt[X] < 0 and pt[Y] < 0:
                continue
            if (pt[X] + 1, pt[Y] + 1) not in mask_set:
                mask_edge_diagonal.append(pt)
        return mask_edge_diagonal
