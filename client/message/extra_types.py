from enum import Enum
from typing import NamedTuple


class Mode(str, Enum):
    FRIENDLY = 'FRIENDLY'
    DEATHMATCH = 'DEATHMATCH'


XY = tuple[int, int]


class XYn(NamedTuple):
    x: int = 0
    y: int = 0

    def __add__(self, other: 'XYn') -> 'XYn':
        return XYn(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'XYn') -> 'XYn':
        return XYn(self.x - other.x, self.y - other.y)


class BotInfo(NamedTuple):
    x: int
    y: int
    coins: int
    id: int
