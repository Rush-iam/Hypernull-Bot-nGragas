from bot.bot import Bot, bot_name, bot_secret, mode
from client.bot_match_runner import BotMatchRunner
from client.client import HypernullClient
from open_log_player import open_match_log_player

server_host = 'localhost'
server_port = 2021
# server_host = '178.216.99.141'
# server_port = 2022


def run_match() -> int:
    return BotMatchRunner(
        bot=Bot(bot_name, bot_secret, mode),
        client=HypernullClient(server_host, server_port),
    ).run()


if __name__ == '__main__':
    run_match()
    open_match_log_player()
