import spotipy
import logging
import configparser
import os
import argparse

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

# ------------------------------------------------------------------
#   ArgParser
# ------------------------------------------------------------------

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--update", action='store_true', help='Update playlist instead of creating a new one')
args = parser.parse_args()
update = args.update

# ------------------------------------------------------------------

def main():
    """
    Main function used to interact with all other functions.

    Keyword arguments:
    None

    Returns:
    None
    """

    file_paths = config.get("CONFIG", "PATHS")
    file_paths = file_paths.split(",")

    debug.info("***********************************************************************************************")
    debug.info("Starting Program...")
    debug.info(f"Paths grabbed: {file_paths}")

    for i in file_paths:
        debug.info(f"Getting tracks from: {i}")
        tracks = get_tracks_from_playlist(i)
        playlist_name = i.split("\\")[-1].split(".")[0]
        debug.info(f"Playlist name: {playlist_name}")
        spotify_interaction(tracks, playlist_name)


def get_tracks_from_playlist(path_to_file):
    """
    Gets the individual tracks from an M3U file and returns the list of tracks.

    The file passed in is parsed using M3uParser.
    Loops through the list generated by the parser and appends the track names to a list.

    Keyword arguments:
    path_to_file -- string -- Path to the M3U file.

    Returns:
    tracks -- list -- List of track names got from the M3U file.
    """

    tracks = []
    useragent = config.get("CONFIG", "USER_AGENT")
    parser = M3uParser(timeout=5, useragent=useragent)
    parser.parse_m3u(path_to_file)

    debug.info(f"Tracks found: {len(parser.get_list())}")

    for i in range(len(parser.get_list())):
        tracks.append(parser.get_list()[i]["name"])

    return tracks


def spotify_interaction(playlist_tracks, playlist_name):
    """
    Handles all the Spotify interactions with Spotipy.

    Tries to connect to the Spotify app created by the user with Spotipy.
    If an exception occurs, it logs the exception and exits the program.
    Creates the playlist and gets the playlist ID.
    Gets a list of the track IDs form the list of track names.
    Updates the playlist with the new list of track IDs.

    Keyword arguments:
    playlist_tracks -- list -- List of track names got from the M3U file.
    playlist_name -- string -- The name of the playlist, got from the name of the M3U file.

    Returns:
    None
    """

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
    
    playlist_track_ids = get_track_ids(sp, playlist_tracks)

    if update:
        playlist_id = get_playlist_id(sp, playlist_name)
        playlist_track_ids = check_for_duplicates(sp, playlist_id, playlist_track_ids)
    else:
        playlist_id = create_playlist(sp, playlist_name)

    update_playlist(sp, playlist_track_ids, playlist_id)


def get_playlist_id(sp, playlist_name):
    """
    Gets the playlist id of the named playlist.

    Keyword arguments:
    sp -- object -- Spotipy object containing the details to connect to the Spotify app created by the user.
    playlist_name -- string -- The name of the playlist, got from the name of the M3U file.

    Returns:
    playlist_id -- string -- The ID of the playlist.
    """

    results = sp.current_user_playlists(limit=50)
    for item in results['items']:
        if item["name"] == playlist_name:
            return item["id"]


def check_for_duplicates(sp, playlist_id, playlist_track_ids):
    """
    Checks for duplicates in the playlist.

    Checks the list of playlist tracks against the list of track IDs gotten from the m3u file.
    If duplicates are found, the duplicates are removed from the playlist_track_ids list.

    Keyword arguments:
    sp -- object -- Spotipy object containing the details to connect to the Spotify app created by the user.
    playlist_id -- string -- The ID of the playlist.
    playlist_track_ids -- list -- List of track IDs to be added.

    Returns:
    playlist_track_ids -- list -- Updated list of track IDs to be added.
    """

    results = sp.user_playlist_tracks(sp.current_user()["id"],playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])

    for i in tracks:
        if i["track"]["id"] in playlist_track_ids:
            playlist_track_ids.remove(i["track"]["id"])
    
    return playlist_track_ids


def create_playlist(sp, playlist_name):
    """
    Creates a Sporify playlist and returns the ID.

    Creates a Playlist with the following details:
        - The ID of the current user.
        - The name of the playlist (playlist_name).
        - Sets the playlist to public.
        - Sets collaborative to False.
    Gets the ID of the playlist created.
    If an exception occurs, it logs the exception and exits the program.

    Keyword arguments:
    sp -- object -- Spotipy object containing the details to connect to the Spotify app created by the user.
    playlist_name -- string -- The name of the playlist, got from the name of the M3U file.

    Returns:
    playlist_id -- string -- The ID of the playlist created.
    """

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
    """
    Gets the Spotify ID of each track.

    Loops through the list of tracks.
    Searches the track in Spotify with the following details:
        - The name of the track.
        - Limtis the search to 1.
        TODO As it only return 1 track, the returned track in some cases may be wrong, need to add a check to make sure the correct song is being grabbed.
        - Search type is set to tracks.
        - Market is set to the user defined country code in the config.
        TODO Add error handling if user enters wrong/unusable country code.
    Gets the Spotify URL of the track from the response of tracks searched.
    Split the string and grabs everything after the last / AKA the track ID.
    Replaces the track name with the track ID in the list.

    Keyword arguments:
    sp -- object -- Spotipy object containing the details to connect to the Spotify app created by the user.
    playlist_tracks -- list -- List of track names got from the M3U file.

    Returns:
    playlist_tracks -- list -- List of track IDs got from Spotify.
    """

    debug.info("Getting Track IDs...")

    for i in range(len(playlist_tracks)):
        track_url = sp.search(playlist_tracks[i],limit=1,type="track",market=config.get("CONFIG", "COUNTRY_CODE"))["tracks"]["items"][0]["external_urls"]["spotify"]
        track_id = track_url.split("/")[-1]
        # debug.info(f"Track ID for {playlist_tracks[i]}: {track_id}")
        
        playlist_tracks[i] = track_id
        # debug.info(f"{track_id} added to list of tracks")

    # debug.info(f"New list of tracks: {playlist_tracks}")
    return playlist_tracks


def update_playlist(sp, tracks, id):
    """
    Updates the playlist on Spotify.

    Uses the replace_tracks class to replace all tracks so to not double up on songs already added.
        - The current user's ID.
        - ID of the playlist.
        - List of track IDs.
    TODO add arguments for user to append songs to playlist instead of replacing everything. Can use remove_duplicates to removed duplicate tracks.
    If an exception occurs, it logs the exception and exits the program.
    Updates the description of the playlist with today's datetime.
        - The current user's ID.
        - ID of the playlist.
        - The description to be added.
    If an exception occurs, it logs the exception.
    TODO You can add a maximum of 100 tracks per request

    Keyword arguments:
    sp -- object -- Spotipy object containing the details to connect to the Spotify app created by the user.
    tracks -- list -- List of track names got from the M3U file.
    id -- string -- The ID of the playlist.

    Returns:
    None
    """

    if update:
        try:
            sp.playlist_add_items(id, tracks)
            debug.info("Playlist updated successfully")
            debug.info(f"{len(tracks)} tracks added")
        except Exception as e:
            debug.error("Error replacing tracks")
            debug.error("e")
            debug.info("Exiting Program...")
            exit()
    else:
        try:
            sp.user_playlist_replace_tracks(sp.current_user()["id"], id, tracks)
            debug.info("Playlist updated successfully")
            debug.info(f"{len(tracks)} tracks added")
        except Exception as e:
            debug.error("Error replacing tracks")
            debug.error("e")
            debug.info("Exiting Program...")
            exit()

    try:
        sp.user_playlist_change_details(sp.current_user()["id"], id, description=f"Playlist updated on {datetime.now()}")
        debug.info("Playlist description updated successfully")
    except Exception as e:
        debug.warning("Error updating description")
        debug.warning("e")


if __name__ == "__main__":
    main()