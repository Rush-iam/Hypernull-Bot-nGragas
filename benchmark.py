import glob
from collections import defaultdict
from os.path import basename

from bot.timing import timing_wrap
from main import run_match

server_host = 'localhost'
server_port = 2021

benchmark_maps_dir: str = r'..\maps'
timings: list[float] = []


@timing_wrap(results=timings)
def run() -> int:
    return run_match()


if __name__ == '__main__':
    match_results: dict[str, list[tuple[int, str]]] = defaultdict(list)
    collected: list[tuple[int, str]] = []
    maps = glob.glob(f'{benchmark_maps_dir}\\*')
    print(f'Found {len(maps)} maps. Starting...')
    for map_file in maps:
        filename = basename(map_file).split('.')[0]
        category, map_nb = filename.split('_', 1)
        collected_coins = run()
        match_results[category].append((collected_coins, map_nb))
        collected.append((collected_coins, filename))
    print('--------------------------------')
    for category, map_results in match_results.items():
        mi, ma = min(map_results), max(map_results)
        print(category, ', '.join(f'{r[0]} ({r[1]})' for r in map_results))
        print(f'- MinMax: {mi[0]} ({mi[1]}) - {ma[0]} ({ma[1]})')
        print('- Total:', sum(m[0] for m in map_results))

    print('===== results =====')
    mi, ma = min(collected), max(collected)
    print(f'MinMax coins: {mi[0]} ({mi[1]}) - {ma[0]} ({ma[1]})')
    print('TOTAL COINS:', sum(m[0] for m in collected))
    print('--------------------------------')
    print(f'Time: {min(timings):.2f} - {max(timings):.2f} '
          f'{collected[timings.index(max(timings))]}')
    print(f'Average: {sum(timings) / len(timings):.2f}')
