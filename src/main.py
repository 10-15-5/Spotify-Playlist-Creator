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
    file_paths = config.get("CONFIG", "PATHS")
    file_paths = file_paths.split(",")

    for i in file_paths:
        tracks = get_tracks_from_playlist(i)
        # update_playlist(tracks)
        # update_playlist()

        # print(pathlib.Path().resolve())
        print(config.get("CONFIG", "CLIENT_ID"))

def get_tracks_from_playlist(path_to_file):
    print(path_to_file)
    useragent = config.get("CONFIG", "USER_AGENT")
    parser = M3uParser(timeout=5, useragent=useragent)
    parser.parse_m3u(path_to_file)

    playlist_list = parser.get_list()

    for i in range(len(playlist_list)):
        print(playlist_list[i]["name"])


if __name__ == "__main__":
    main()