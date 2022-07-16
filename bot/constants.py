from enum import Enum

from client.message.extra_types import XY


class MapChar(str, Enum):
    UNKNOWN = '?'
    EMPTY = '.'
    BLOCK = '■'
    MY_BLOCK = '◪'
    COIN = '$'
    PLAYER = '♦'
    OPPONENT = '!'


MAP_CHAR_BLOCKS: set[MapChar] = {MapChar.BLOCK, MapChar.MY_BLOCK}

X, Y = 0, 1

DIRECTIONS: tuple[XY, ...] = \
    (-1, -1), (-1, 1), (1, 1), (1, -1), (-1, 0), (0, 1), (1, 0), (0, -1)

# DO NOT REORDER
DIRECTIONS_ROUND: tuple[XY, ...] = \
    (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)

# DO NOT REORDER
DIRECTIONS_XY_OPTIMAL: tuple[XY, ...] = \
    (-1, 0), (0, 1), (1, 0), (0, -1), (-1, -1), (-1, 1), (1, 1), (1, -1)


class Color(int, Enum):
    CLEAR = 00
    RED = 91
    GREEN = 92
    YELLOW = 93
    BLUE = 94
    PURPLE = 95
    CYAN = 96
    LIGHT_GRAY = 97
    BLACK = 98
