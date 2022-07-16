from __future__ import annotations

from client.bot_base import BotBase
from client.message.extra_types import Mode, BotInfo, XY
from client.message.messages import MatchStarted, Update

from .a_star import AStar
from .bfs import BFS
from .canvas import Canvas
from .coins_finder_graph import CoinsFinderGraph
from .constants import Color
from .dead_end_filler import DeadEndFiller
from .explorer import Explorer
from .map import Map
from .timing import timing_wrap

bot_name = 'nGragas'
bot_secret = ''
mode = Mode.FRIENDLY
# mode = Mode.DEATHMATCH
timings: list[float] = []


class Bot(BotBase):
    bot: BotInfo | None = None
    pos: XY | None = None
    opponents: list[BotInfo] = []
    canvas: Canvas
    map: Map
    dead_end_filler: DeadEndFiller
    bfs: BFS
    a_star: AStar
    explorer: Explorer
    coins_finder: CoinsFinderGraph

    def on_match_start(self, match: MatchStarted) -> None:
        print(match)
        self.match = match
        self.id = match.your_id
        self.canvas = Canvas(match.map_size)
        self.map = Map(match.map_size, match.view_radius, match.mining_radius)
        self.dead_end_filler = DeadEndFiller(match.map_size, self.map)
        self.bfs = BFS(match.map_size, self.map, self.dead_end_filler)
        self.a_star = AStar(match.map_size, self.map)
        self.explorer = Explorer(match.map_size, self.map, self.bfs)
        self.coins_finder = CoinsFinderGraph(
            match.map_size, self.map.coins_pts, self.map.visible, self.bfs
        )

    @timing_wrap(results=timings)
    def on_update(self, update: Update) -> XY:
        round_number, coins, blocks = update.round, update.coin, update.block
        self.update(update)
        # print(f'{round_number - 1} {self.bot.coins} {self.pos}')

        coin_pts = self.coins_finder.get_best_pts(self.pos)
        coin_dirs = None
        if coin_pts:
            coin_dirs = [self.map.position_diff(self.pos, pt) for pt in coin_pts]
            if len(coin_dirs) == 1:
                return coin_dirs[0]

        best_not_seen = self.explorer.get_not_seen_dir(
            self.pos, round_number, coin_dirs
        )
        return best_not_seen

    def update(self, update: Update) -> None:
        round_number, coins, blocks = update.round, update.coin, update.block
        self.opponents = [bot for bot in update.bot if bot.id != self.id]
        self.bot = next(bot for bot in update.bot if bot.id == self.id)
        self.pos = (self.bot.x, self.bot.y)
        self.map.update(self.pos, round_number, coins, blocks, self.opponents)
        self.bfs.update(self.pos)
        # self.explorer.update_gradient_to_unknown()

    def on_match_over(self) -> None:
        # print(self.explorer.gradient_to_unknown)
        # self.map.print_last_seen()
        self.print_canvas()
        print()
        print(f'Collected {self.bot.coins} coins')
        print()
        self.print_timings()

    def print_canvas(self) -> None:
        # self.bfs.export(self.canvas.grid)
        # self.a_star.export(self.canvas.grid)
        self.map.export(self.canvas.grid)
        self.canvas.highlight(self.map.visible, Color.LIGHT_GRAY)
        self.canvas.highlight(self.bfs.nodes.keys(), Color.BLUE)
        self.canvas.highlight(self.map.coins_map.keys(), Color.YELLOW)
        self.canvas.highlight(self.a_star.nodes.keys(), Color.PURPLE)
        self.canvas.highlight(self.a_star.last_path, Color.PURPLE)
        self.canvas.highlight([self.pos], Color.GREEN)
        self.canvas.highlight(((op.x, op.y) for op in self.opponents), Color.RED)
        self.canvas.print()

    def print_timings(self):
        print(f'Time: {self._remove_zero(min(timings))} - '
              f'{self._remove_zero(max(timings))} '
              f'(round #{timings.index(max(timings))})')
        print(f'Average: {self._remove_zero(sum(timings) / len(timings))}')
        timings.clear()

    @staticmethod
    def _remove_zero(value: float, precision: int = 3) -> str:
        return f'{value:.{precision}f}'.lstrip('0')
