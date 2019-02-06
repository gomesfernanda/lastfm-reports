# lastfm-reports

This projects aims to build a report of a user's data.

Available functions (ready to use):

- `lastfm_get_artist_bio.py`: function that prints on the screen the bio of the artist/band as it is on last.fm or their tags.
- `lastfm_get_loved_tracks.py`: function that prints on the screen the loved tracks for a given user.

How to use on the command line:

1. Clone this repo
2. Add dependencies: `$ pip install requirements.txt`
3. Run the desired file:
  - `$ py3 lastfm_get_artist_bio.py -a [ARTIST NAME] -f [FUNCTION]`
    - where the function can be `bio` or `tags`
  - `$ py3 lastfm_get_loved_tracks.py -u [LASTFM USER] -l [LIMIT]`
    - where the default limit is 50; the user can use any integer to collect the desired number of loved tracks or `all` to collect all loved tracks.