from __future__ import annotations

from itertools import chain

from client.message.extra_types import XY, BotInfo

from .constants import MapChar, MAP_CHAR_BLOCKS, X, Y
from .map_utils import MapUtilsMixin
from .area_mask import AreaMask


class Map(MapUtilsMixin):
    def __init__(self, size: XY, view_radius: int, mining_radius: int):
        self.size: XY = size
        self.view_area: AreaMask = AreaMask(view_radius)
        self.visible: set[XY] = set()
        self.grid = [[MapChar.UNKNOWN] * size[X] for _ in range(size[Y])]
        self.last_seen: list[list[int]] = [[0] * size[X] for _ in range(size[Y])]
        self.coins_area: AreaMask = AreaMask(mining_radius)
        self.coins_map: dict[XY, list[XY]] = dict()
        self.coins_pts: dict[XY: list[XY]] = dict()

    def __getitem__(self, i: int) -> list[MapChar]:
        return self.grid[i]

    def update(self, bot: XY, round_number: int, coins: list[XY],
               blocks: list[XY], opponents: list[BotInfo]) -> None:
        self.visible.clear()
        for diff in self.view_area:
            pt = self.position_add(bot, diff)
            self.grid[pt[Y]][pt[X]] = MapChar.EMPTY
            self.last_seen[pt[Y]][pt[X]] = round_number
            self.visible.add(pt)
        self.update_blocks(blocks)
        self.update_coins(coins)
        self.update_bots(bot, opponents)

    def update_blocks(self, blocks: list[XY]) -> None:
        for block in blocks:
            self.grid[block[Y]][block[X]] = MapChar.BLOCK

    def update_coins(self, coins: list[XY]) -> None:
        for coin in coins:
            self.grid[coin[Y]][coin[X]] = MapChar.COIN

        self.coins_map.clear()

        to_delete = [coin for coin in self.coins_pts
                     if coin in self.visible and coin not in set(coins)]
        for coin in to_delete:
            del self.coins_pts[coin]

        to_add = (coin for coin in coins if coin not in self.coins_pts)
        for coin in chain(self.coins_pts, to_add):
            self.coins_pts[coin] = []
            for diff in self.coins_area:
                pt = self.position_add(coin, diff)
                if not self.is_block(pt) and not self.is_unknown(pt):
                    self.coins_map[pt] = self.coins_map.get(pt, []) + [coin]
                    self.coins_pts[coin].append(pt)

    def update_bots(self, bot: XY, opponents: list[BotInfo]) -> None:
        for opponent in opponents:
            self.grid[opponent.y][opponent.x] = MapChar.OPPONENT
        self.grid[bot[Y]][bot[X]] = MapChar.PLAYER

    def is_empty(self, pt: XY) -> bool:
        return self.grid[pt[Y]][pt[X]] is MapChar.EMPTY

    def is_unknown(self, pt: XY) -> bool:
        return self.grid[pt[Y]][pt[X]] is MapChar.UNKNOWN

    def is_block(self, pt: XY) -> bool:
        return self.grid[pt[Y]][pt[X]] is MapChar.BLOCK

    def is_my_block(self, pt: XY) -> bool:
        return self.grid[pt[Y]][pt[X]] is MapChar.MY_BLOCK

    def in_blocks(self, pt: XY) -> bool:
        return self.grid[pt[Y]][pt[X]] in MAP_CHAR_BLOCKS

    def print(self) -> None:
        for row in self.grid[::-1]:
            print(''.join(row))

    def export(self, canvas: list[list[str]]) -> None:
        for y in range(self.size[Y]):
            for x in range(self.size[X]):
                if (char := self.grid[y][x]) is not MapChar.EMPTY:
                    canvas[y][x] = char

    def print_last_seen(self) -> None:
        for row in self.last_seen[::-1]:
            print(''.join(str(v // 10).rjust(2) for v in row))
