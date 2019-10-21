# Lastfm reports

## Introduction

This project aims to build a detailed analysis of a user's data.

For now, the analysis is being done on a Jupyter Notebook and can be seen [here](https://github.com/gomesfernanda/lastfm-reports/blob/master/lastfm_analysis.ipynb).

In order to do so, I must first collect the user's historical tracks. Below you will find instructions to use this script and some helpers scripts I wrote.

It's important to keep in mind the assumptions I'm making:

1. You have a last.fm account
2. You have an application on last.fm developer service, since you'll need an API key and API secret (if you don't have it, create one [here](https://www.last.fm/api/account/create))
3. After you created the application, you saved your credentials as `secrets.json` following the format:

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

## Collecting your data

Available functions (ready to use):

- `lastfm_get_artist_bio_tags.py`: function that prints on the screen the bio of the artist/band as it is on last.fm or their tags.
- `lastfm_get_user_loved_tracks.py`: function that prints on the screen the loved tracks for a given user.
- `lastfm_get_user_friends.py` : function that prints on the screen the friends for a given user, sorted by largest number of scrobbles.
- `lastfm_get_user_recent_tracks.py` : function that collects and prints the last recent tracks for a given user.
- `lastfm_get_user_historical_tracks.py` : function that collects and exports in csv all the tracks a user listened to, since the account was created.

How to use on the command line:

1. Clone this repo
2. Add dependencies: `$ pip install requirements.txt`
3. Run the desired file:
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

(Thanks to https://github.com/pylast/pylast)