import spotipy
import logging
import configparser
import pathlib

from spotipy.oauth2 import SpotifyOAuth
from m3u_parser import M3uParser

# ------------------------------------------------------------------
#   Logging Setup
# ------------------------------------------------------------------

logger = logging.getLogger("info")
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%d-%m-%y %H:%M:%S')

file_handler = logging.FileHandler(str(pathlib.Path().resolve()) + r"/logs/logs.log", encoding='utf8')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
# ------------------------------------------------------------------
debug = logging.getLogger("debug")
debug.setLevel(logging.INFO)

formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(message)s', datefmt='%d-%m-%y %H:%M:%S')

file_handler = logging.FileHandler(str(pathlib.Path().resolve()) + r"/logs/debug.log", encoding='utf8')
file_handler.setFormatter(formatter)

debug.addHandler(file_handler)

# ------------------------------------------------------------------
# ------------------------------------------------------------------


config = configparser.RawConfigParser()
configFilePath = str(pathlib.Path().resolve()) + r"/settings/config.txt"
config.read(configFilePath, encoding="utf-8")


def main():
    # tracks = get_tracks_from_playlist()
    # update_playlist(tracks)
    # update_playlist()

    # print(pathlib.Path().resolve())
    print(config.get("CONFIG", "CLIENT_ID"))






if __name__ == "__main__":
    main()