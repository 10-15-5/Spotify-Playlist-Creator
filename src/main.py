import spotipy
import logging
import configparser
import pathlib

from datetime import datetime
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
        playlist_name = i.split("\\")[-1].split(".")[0]
        spotify_interaction(tracks, playlist_name)

def get_tracks_from_playlist(path_to_file):
    tracks = []
    useragent = config.get("CONFIG", "USER_AGENT")
    parser = M3uParser(timeout=5, useragent=useragent)
    parser.parse_m3u(path_to_file)

    playlist_list = parser.get_list()

    for i in range(len(playlist_list)):
        tracks.append(playlist_list[i]["name"])

    return tracks


def spotify_interaction(playlist_tracks, playlist_name):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=config.get("CONFIG", "CLIENT_ID"),
                                                client_secret=config.get("CONFIG", "CLIENT_SECRET"),
                                                redirect_uri="http://localhost/",
                                                scope="playlist-modify-public"))
    
    playlist_id = create_playlist(sp, playlist_name)

    playlist_track_ids = get_track_ids(sp, playlist_tracks)

    update_playlist(sp, playlist_track_ids, playlist_id)
    

def create_playlist(sp, playlist_name):
    playlist_id = sp.user_playlist_create(sp.current_user()["id"], 
                            playlist_name, 
                            public=True, 
                            collaborative=False
                            )["id"]
    
    return playlist_id


def get_track_ids(sp, playlist_tracks):

    for i in range(len(playlist_tracks)):
        track_url = sp.search(playlist_tracks[i],limit=1,type="track",market=config.get("CONFIG", "COUNTRY_CODE"))["tracks"]["items"][0]["external_urls"]["spotify"]
        track_id = track_url.split("/")[-1]
        
        playlist_tracks[i] = track_id

    return playlist_tracks

def update_playlist(sp, tracks, id):

    sp.user_playlist_replace_tracks(sp.current_user()["id"], id, tracks)
    sp.user_playlist_change_details(sp.current_user()["id"], id, description="Auto-generated playlist updated on " + str(datetime.now()))


if __name__ == "__main__":
    main()