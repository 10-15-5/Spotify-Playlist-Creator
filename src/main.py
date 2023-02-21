import spotipy
import logging
import configparser
import os

from datetime import datetime
from spotipy.oauth2 import SpotifyOAuth
from m3u_parser import M3uParser

# ------------------------------------------------------------------
#   Logging & Config Setup
# ------------------------------------------------------------------

if not os.path.exists('logs'):
    os.mkdir('logs')

debug = logging.getLogger("debug")
debug.setLevel(logging.INFO)

formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(message)s', datefmt='%d-%m-%y %H:%M:%S')

file_handler = logging.FileHandler(str(os.getcwd()) + r"/logs/debug.log", encoding='utf8')
file_handler.setFormatter(formatter)

debug.addHandler(file_handler)
# ------------------------------------------------------------------
config = configparser.RawConfigParser()
configFilePath = str(os.getcwd()) + r"/settings/config.txt"
config.read(configFilePath, encoding="utf-8")
# ------------------------------------------------------------------
# ------------------------------------------------------------------


def main():
    file_paths = config.get("CONFIG", "PATHS")
    file_paths = file_paths.split(",")

    debug.info(f"Paths grabbed: {file_paths}")

    for i in file_paths:
        debug.info(f"Getting tracks from: {i}")
        tracks = get_tracks_from_playlist(i)
        playlist_name = i.split("\\")[-1].split(".")[0]
        debug.info(f"Playlist name: {playlist_name}")
        spotify_interaction(tracks, playlist_name)

def get_tracks_from_playlist(path_to_file):
    tracks = []
    useragent = config.get("CONFIG", "USER_AGENT")
    parser = M3uParser(timeout=5, useragent=useragent)
    parser.parse_m3u(path_to_file)

    playlist_list = parser.get_list()
    debug.info(f"Tracks found: {len(playlist_list)}")

    for i in range(len(playlist_list)):
        tracks.append(playlist_list[i]["name"])

    return tracks


def spotify_interaction(playlist_tracks, playlist_name):
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=config.get("CONFIG", "CLIENT_ID"),
                                                client_secret=config.get("CONFIG", "CLIENT_SECRET"),
                                                redirect_uri="http://localhost/",
                                                scope="playlist-modify-public"))
        debug.info("Spotify connection successful")
    except Exception as e:
        debug.error("Error connecting to Spotify")
        debug.error(e)
        debug.info("Exiting Program...")
        exit()
    
    playlist_id = create_playlist(sp, playlist_name)

    playlist_track_ids = get_track_ids(sp, playlist_tracks)

    update_playlist(sp, playlist_track_ids, playlist_id)
    

def create_playlist(sp, playlist_name):
    try:
        playlist_id = sp.user_playlist_create(sp.current_user()["id"], 
                                playlist_name, 
                                public=True, 
                                collaborative=False
                                )["id"]
        debug.info("Playlist created successfully")
        debug.info(f"Playlist ID: {playlist_id}")
    except Exception as e:
        debug.error("Error creating playlist")
        debug.error(e)
        debug.info("Exiting Program...")
        exit()
    
    return playlist_id


def get_track_ids(sp, playlist_tracks):

    for i in range(len(playlist_tracks)):
        track_url = sp.search(playlist_tracks[i],limit=1,type="track",market=config.get("CONFIG", "COUNTRY_CODE"))["tracks"]["items"][0]["external_urls"]["spotify"]
        track_id = track_url.split("/")[-1]
        debug.info(f"Track ID for {playlist_tracks[i]}: {track_id}")
        
        playlist_tracks[i] = track_id
        debug.info(f"{track_id} added to list of tracks")

    debug.info(f"New list of tracks: {playlist_tracks}")
    return playlist_tracks

def update_playlist(sp, tracks, id):
    try:
        sp.user_playlist_replace_tracks(sp.current_user()["id"], id, tracks)
        debug.info("Playlist updated successfully")
    except Exception as e:
        debug.error("Error replacing tracks")
        debug.error("e")
        debug.info("Exiting Program...")
        exit()

    try:
        sp.user_playlist_change_details(sp.current_user()["id"], id, description="Auto-generated playlist updated on " + str(datetime.now()))
        debug.info("Playlist description updated successfully")
    except Exception as e:
        debug.warning("Error updating description")
        debug.warning("e")



if __name__ == "__main__":
    main()