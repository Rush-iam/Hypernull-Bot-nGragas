import logging

from .bot_base import BotImpl
from .client import HypernullClient
from .message import messages
from .message.extra_types import BotInfo


class BotMatchRunner:
    def __init__(self, bot: BotImpl, client: HypernullClient):
        self.bot = bot
        self.client = client

    def run(self) -> int:
        self.client.register(self.bot)

        match_info: messages.MatchStarted = self.client.get()
        bot_id: int = match_info.your_id
        self.bot.on_match_start(match_info)

        bots = []
        while update := self.client.get_update():
            bots = update.bot
            if direction := self.bot.on_update(update):
                self.client.move(*direction)
            else:
                logging.warning('bot did not provide move direction')
                self.client.move(0, 0)

        self.bot.on_match_over()

        bot: BotInfo = next(bot for bot in bots if bot.id == bot_id)
        return bot.coins
