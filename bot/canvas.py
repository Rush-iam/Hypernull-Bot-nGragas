from __future__ import annotations

from collections.abc import Iterable

from client.message.extra_types import XY

from .constants import X, Y, Color


class Canvas:
    def __init__(self, size: XY, fill_char: str = '·'):
        self.size: XY = size
        self.fill_char: str = fill_char
        self.grid: list[list[str]] = [
            [self.fill_char] * self.size[X] for _ in range(self.size[Y])
        ]
        self.color: list[list[Color | None]] = [
            [None] * self.size[X] for _ in range(self.size[Y])
        ]

    def clean(self) -> None:
        for y in range(self.size[Y]):
            for x in range(self.size[X]):
                self.grid[y][x] = self.fill_char
                self.color[y][x] = None

    def highlight(self, pts: Iterable[XY], color: Color) -> None:
        for pt in pts:
            self.color[pt[Y]][pt[X]] = color

    def highlight_except(self, pts: set[XY], color: Color) -> None:
        for y in range(self.size[Y]):
            for x in range(self.size[X]):
                if (x, y) not in pts:
                    self.color[y][x] = color

    @staticmethod
    def colored(s: str, color: Color) -> str:
        return f'\033[{color}m{s}\033[{Color.CLEAR}m'

    def print(self, y_reversed: bool = True):
        def tens(val: int) -> int:
            return val // 10 % 10

        lines = [
            (str(tens(y)) if tens(y) else ' ') + str(y % 10) + ' ' + ''.join(
                self.colored(ch, self.color[y][x]) if self.color[y][x] else ch
                for x, ch in enumerate(row)
            ) for y, row in enumerate(self.grid)
        ]
        if y_reversed:
            lines.reverse()

        ruler_x = [
            '   ' + ''.join(str(tens(x)) if tens(x) else ' ' for x in range(self.size[X])),
            '   ' + ''.join(str(x % 10) for x in range(self.size[X])),
        ]
        lines = ruler_x + [''] + lines + [''] + ruler_x

        print('\n'.join(lines))
