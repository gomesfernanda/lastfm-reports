# Lastfm reports

## Introduction

This project serves two purposes:

1. Collect historical listened tracks for a given last.fm user.
2. Build a detailed statistical analysis of its listening habits.
3. Build a simple recommendation system (new artists) for the user.

### Step 0 - Installing requirements

1. Clone this repo
2. Create a virtual environment (I use [`venv`](https://docs.python.org/3/library/venv.html))
3. Activate your environment: `$ source [ENVIRONMENT_NAME]/bin/activate`
4. Install dependencies: `$ pip install -r requirements.txt`

### Step 1 - Authorizing services

After installing the requirements, you will need to authorize last.fm and Spotify to collect the data.

#### last.fm

I'm assuming here you have a last.fm account so you can analyze the data, but if you don't, you have to do it.

1. Register at last.fm ([here](https://www.last.fm/join)) or log in.
2. Create an application on last.fm developer service, since you'll need an API key and API secret ([here](https://www.last.fm/api/account/create))
3. After you create the application, you will save your credentials on this repo directory as `secrets.json` following the format:

```json
{
  "API": {
    "API_KEY": "YOUR API KEY",
    "API_SECRET": "YOUR API SECRET",
    "username": "YOUR USER",
    "password_hash": "YOUR PASSWORD"
  }
}
```

**In case of doubts regarding this service, please go to [links and documentation section](https://github.com/gomesfernanda/lastfm-reports/blob/master/README.md#helpful-links-and-documentation)**

#### Spotify

You will follow similar steps to authenticate with Spotify:

1. Register at Spotify ([here](https://www.spotify.com/signup/)) or log in.
2. Create an application on Spotify developer platform, since you'll also need credentials ([here](https://developer.spotify.com/dashboard/applications)).
3. Save your Client ID and Client Secret somewhere safe.
4. Export your Client ID and Client Secret on the terminal running the following commands (on Mac):

```bash
$ export SPOTIPY_CLIENT_ID='your-spotify-client-id'
$ export SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'
```

**In case of doubts regarding this service, please go to [links and documentation section](https://github.com/gomesfernanda/lastfm-reports/blob/master/README.md#helpful-links-and-documentation)**

### Step 2 - Data Collection

Now that we have dependencies and services up and running, we will collect the data. That's the easiest step. You'll use the command line for that.

On the terminal (inside your virtual environment and inside the cloned repo folder), you will run the command:

```
$ py lastfm_get_user_historical_tracks.py -u [LASTFM_USER]
```
The script `lastfm_get_user_historical_tracks.py` will collect the whole history of listened tracks for the given user (`LASTFM_USER`) and save it as a csv file inside a folder it will create. The script overwrites its file with collected tracks each 200 entries (following last.fm pagination).

This script still fails sometimes for API reasons mostly. You just have to run the command again because it will catch up with the last file and collect the incremental data.

The data to be collected is:

From last.fm:

- Date the track was listened to
- MBID (identifier that is permanently assigned to each entity in the database - more info [here](https://musicbrainz.org/doc/MusicBrainz_Identifier))
- Track name
- Artist name
- Album name
- Whether this track was marked as "loved" or not
- Most common tags for the artist

From Spotify (audio features):
- Danceability
- Energy
- Key
- Loudness
- Mode
- Speechiness
- Acousticness
- Intrumentalness
- Liveness
- Valence
- Tempo.

**In case of doubts regarding this service, please go to [links and documentation section](https://github.com/gomesfernanda/lastfm-reports/blob/master/README.md#helpful-links-and-documentation)**

### Descriptive Analysis and Music Recommendation

For now, the descriptive analysis and music recommendation are being done on a Jupyter Notebook and can be seen [here](https://nbviewer.jupyter.org/github/gomesfernanda/lastfm-reports/blob/master/lastfm_analysis.ipynb). You can also check more notebooks on this repo, since I'll be playing a lot with the features.

### Further functions and scripts

Available functions (ready to use):

- `lastfm_get_artist_bio_tags.py`: function that prints on the screen the bio of the artist/band as it is on last.fm or their tags.
- `lastfm_get_user_loved_tracks.py`: function that prints on the screen the loved tracks for a given user.
- `lastfm_get_user_friends.py` : function that prints on the screen the friends for a given user, sorted by largest number of scrobbles.
- `lastfm_get_user_recent_tracks.py` : function that collects and prints the last recent tracks for a given user.
- `lastfm_get_user_historical_tracks.py` : function that collects and exports in csv all the tracks a user listened to, since the account was created.

How to use on the command line:

- Run the desired script:
  - `$ py3 lastfm_get_artist_bio_tags.py -a [ARTIST NAME] -f [FUNCTION]`
    - where the function can be `bio` or `tags`
  - `$ py3 lastfm_get_user_loved_tracks.py -u [LASTFM USER] -l [LIMIT]`
    - where the default limit is 50; the user can use any integer to collect the desired number of loved tracks or `all` to collect all loved tracks.
  - `$ py3 lastfm_get_user_friends.py -u [LASTFM_USER] -l [LIMIT]`
    - where the default limit is 10; the user can use any integer to collect the desired number of friends or `all` to collect all friends.
  - `$ py3 lastfm_get_user_recent_tracks.py -u [LASTFM_USER] -l [LIMIT]`
    - where the default limit is 20; the user can use any integer to collect the desired number of recent tracks listened.
  - `$ py3 lastfm_get_user_historical_tracks -u [LASTFM_USER]`
    - the only parameter on this script is the user you wanna collect the metrics from. The exports will be saved on a file named after the user and the current date and time.

### Helpful Links and Documentation

- Thanks to [PyLast](https://github.com/pylast/pylast)
- Thanks to [Spotipy](https://spotipy.readthedocs.io/en/2.12.0/)
- [Last.fm for Developers - User Authentication](https://www.last.fm/api/authentication)
- [Spotify for Developers - Authorization Guide](https://developer.spotify.com/documentation/general/guides/authorization-guide/)
- [Spotipy Client Credentials Flow](https://spotipy.readthedocs.io/en/2.12.0/#client-credentials-flow)
- [What is MBID](https://musicbrainz.org/doc/MusicBrainz_Identifier)
- [Spotify's Audio Features](https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-features/)

I hope you enjoy running your analysis. Feel free to open issues and submit PRs.

And the most important: HAVE FUN!

![yeah](https://media.giphy.com/media/Is1O1TWV0LEJi/giphy.gif)