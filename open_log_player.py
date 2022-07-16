import glob
import os
import subprocess


def open_match_log_player() -> None:
    jre = r'C:\Users\Rush\.jdks\liberica-11.0.15.1\bin\java.exe'
    player = r'..\player\target\player.jar'
    latest_file = max(
        glob.glob(r'..\matchlogs\*'),  # noqa
        key=os.path.getctime
    )
    subprocess.Popen([jre, '-jar', player, latest_file])
