# Lastfm reports

This projects aims to build a report of a user's data in the future. I'm currently working on collecting data and organizing functions.

Available functions (ready to use):

- `lastfm_get_artist_bio_tags.py`: function that prints on the screen the bio of the artist/band as it is on last.fm or their tags.
- `lastfm_get_user_loved_tracks.py`: function that prints on the screen the loved tracks for a given user.
- `lastfm_get_user_friends.py` : function that prints on the screen the friends for a given user, sorted by largest number of scrobbles.

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


(Thanks to https://github.com/pylast/pylast)