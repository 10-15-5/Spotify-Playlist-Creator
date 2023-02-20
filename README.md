# Spotify Playlist Creator

Given an m3u file, this script will create a Spotify playlist with the songs
in the file.


*NB: This script ***can*** and ***will*** make errors*

## Usage
1. Clone codebase
2. Install requirements
    * `pip install -r requirements.txt`
3. Navigate to settings/config.txt and fill in the necessary details
    * You will need to create an app [here](https://developer.spotify.com/dashboard/applications).
    * ***Client ID***: Can be got from your app's dashboard.
    * ***Client Secret***: Same as above.
    * ***Country Code***: 2 letter code of the country you want to search from (US, GB etc.).
    * ***Paths***: paths to the m3u files, seperate multiple paths with commas.
4. Run main.py from terminal.
5. Browser window will popup, when prompted allow the app to create playlists.
6. You will then be taken to a webpage with an error, copy the URL and open terminal where main.py is running and paste the URL when it asks.


## Notes

As above, this code **will** make errors and add the wrong song to the playlist occassionally.

It is very dependent on good data from the m3u file, if the song details are wrong in the m3u file, it will be wrong in the playlist.