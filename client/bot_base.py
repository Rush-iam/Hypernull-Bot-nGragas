from dataclasses import dataclass, field
from typing import TypeVar

from client.message.extra_types import Mode, XY
from client.message.messages import MatchStarted, Update


BotImpl = TypeVar('BotImpl', bound='BotBase')


@dataclass
class BotBase:
    name: str
    secret: str = None
    mode: Mode = Mode.FRIENDLY
    match: MatchStarted = field(init=False)
    id: int = field(init=False)

    def on_match_start(self, match_info: MatchStarted) -> None:
        raise NotImplementedError

    def on_update(self, update: Update) -> XY:
        raise NotImplementedError

    def on_match_over(self) -> None:
        raise NotImplementedError
