import pylast
import requests
import json
from datetime import datetime
import ast
import argparse
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from file_manipulation import get_last_file, save_file, create_copy, total_rows
from get_user_recent_tracks import get_longevity
import time


def progbar(curr, total, unit, full_progbar):
    frac = curr / total
    filled_progbar = round(frac * full_progbar)
    print('\r Progress: |', '█' * filled_progbar + '-' * (full_progbar - filled_progbar), '| [{:>7.2%}]'.format(frac),
          ' [ ', unit, curr, '|', total, ']', end='')


def setup():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user', help='choose username to collect tracks from', required=True)
    args = parser.parse_args()
    return args


def open_dicts(artists_file, audio_features_file):
    try:
        with open(artists_file) as json_file:
            artists_dict = json.load(json_file)
    except Exception as e:
        artists_dict = {'none': ['']}
        with open(artists_file, 'w') as json_file:
            json.dump(artists_dict, json_file)
    try:
        with open(audio_features_file) as json_file:
            audio_features_dict = json.load(json_file)
    except Exception as e:
        audio_features_dict = {'none': {}}
        with open(audio_features_file, 'w') as json_file:
            json.dump(audio_features_dict, json_file)
    return artists_dict, audio_features_dict


def step1(new_scrobbles, user, path, dest_file, hist_file, columns):
    last_file = get_last_file(user, hist_file)
    if last_file != None:
        print("Found existing file")
        old_scrobbles, old_date = total_rows(path, last_file)
        if int(new_scrobbles) > int(old_scrobbles):
            create_copy(path, last_file, dest_file)
    else:
        print("Could not find file")
        save_file(columns, path, dest_file)
        old_scrobbles = 0
        old_date = 0
    return old_scrobbles, old_date


def get_credentials(creds_file):
    with open(creds_file, 'r') as file:
        jsonfile = json.load(file)
        API_KEY = jsonfile['API']['API_KEY']
        API_SECRET = jsonfile['API']['API_SECRET']
        username = jsonfile['API']['username']
        password = jsonfile['API']['password_hash']
        password_hash = pylast.md5(password)
    return API_KEY, API_SECRET, username, password, password_hash


def get_pages_scrobbled(username, network):
    user = network.get_user(username)
    scrobbles = user.get_playcount()
    pages = int(scrobbles / 200) + (scrobbles % 200 > 0)
    return scrobbles, pages


def get_tags(artist, network, limit=20):
    artist_ = network.get_artist(artist)
    try:
        toptags = artist_.get_top_tags(limit)
        toptags_list = []
        unify_artist = str(artist_).lower().replace(' ', '')
        bad_tags = [unify_artist, 'seen live']
        for i, tag in enumerate(toptags):
            toptag = str(tag.item).lower()
            toptag_unified = toptag.replace(' ', '')
            if toptag not in bad_tags and toptag_unified not in bad_tags:
                toptags_list.append(toptag)
    except Exception as e:
        toptags_list = []
    return toptags_list


def get_tracks(network, user, api_key, diff, start, artist_dict, audio_features_dict, path, dest_file, date_from):
        cont = 1
        url = 'http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=' + str(user) + '&api_key=' + str(
            api_key) + '&format=json&limit=200&extended=1&from=' + str(date_from)
        r = requests.get(url)
        r_json = json.loads(r.content)
        pages = int(r_json['recenttracks']['@attr']['totalPages'])
        for page in reversed(range(1, pages + 1)):
            page_lst = []
            run_limit = diff - (200) * (page - 1)
            i = start + run_limit - 1
            url = 'http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=' + str(user) + '&api_key=' + str(
                api_key) + '&format=json&limit=200&page=' + str(page) + '&extended=1&from=' + str(date_from)
            r = requests.get(url)
            r_json = json.loads(r.content)

            tracks = r_json['recenttracks']['track']
            for t in tracks:
                progbar(int(cont), int(diff), 'track', 20)
                mbid = t['mbid']
                loved = t['loved']
                artist = t['artist']['name']
                try:
                    date_epoch = t['date']['uts']
                    date_ts = int(date_epoch)
                except:
                    date_now = datetime.now()
                    date_ts = int(datetime.timestamp(date_now))
                date = (datetime.utcfromtimestamp(date_ts).strftime('%Y-%m-%d %H:%M:%S'))
                track = t['name']
                album = t['album']['#text']
                key = artist + track + album
                if key in audio_features_dict:
                    audio_features = audio_features_dict[key]
                else:
                    audio_features = get_audio_features(artist, track)
                    audio_features_dict[key] = audio_features
                if artist in artist_dict:
                    tags = artist_dict[artist]
                else:
                    tags = get_tags(artist, network, limit=20)
                l = [i, date_ts, date, mbid, artist, track, album, loved, tags]
                if type(audio_features) == str:
                    audio_features = ast.literal_eval(audio_features)
                try:
                    l = l + list(audio_features.values())
                except:
                    print(audio_features)
                page_lst.append(l)
                i -= 1
                cont += 1
            page_lst.reverse()
            if page > 1:
                save_file(page_lst, path, dest_file)
            if page % 10 == 0:
                complete_artists_file(artist, tags)
                complete_audio_features_file(key, audio_features, audio_features_dict)
        complete_artists_file(artist, tags)
        complete_audio_features_file(key, audio_features, audio_features_dict)
        save_file(page_lst, path, dest_file)


def get_audio_features(pass_artist, pass_track):
    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

    artist = str(pass_artist).replace("'", "")
    song = str(pass_track).replace("'", "")

    q = "artist:" + artist + " track:" + song
    results = sp.search(q=q)
    total = results["tracks"]["total"]

    if total > 0:
        ts = str(results)
        begin = ts[ts.find('spotify:track:') + len('spotify:track:'):]
        end = begin.find("'")
        track_id = str(begin[:end])
        features = sp.audio_features(track_id)[0]
        if features is None:
            features = {}
        else:
            try:
                del features['type']
                del features['id']
                del features['uri']
                del features['track_href']
                del features['analysis_url']
                del features['duration_ms']
                del features['time_signature']
            except:
                print('\n', features, pass_artist, pass_track, '\n')
    else:
        features = {}
    return features


def complete_artists_file(new_artist_name, new_artist_tags):
    with open('artists_tags.json') as json_file:
        artists_dict = json.load(json_file)
    artists_dict[new_artist_name] = new_artist_tags
    with open('artists_tags.json', 'w') as fp:
        json.dump(artists_dict, fp)


def complete_audio_features_file(new_track, new_audio_features, audio_features_dict):
    audio_features_dict[new_track] = new_audio_features
    with open('audio_features.json', 'w') as json_file:
        json.dump(audio_features_dict, json_file)


def main():
    args = setup()
    user = args.user
    creds_file = 'secrets.json'
    API_KEY, API_SECRET, username, password, password_hash = get_credentials(creds_file)
    todaynow = datetime.now().strftime('%Y%m%d%H%M')
    path = 'export_' + str(user) + '/'
    dest_file = 'historical_tracks_' + str(user) + '_' + str(todaynow)
    hist_file = 'historical_tracks_'
    columns = [['#scrobble', 'date', 'date_fmt', 'mbid', 'artist', 'track', 'album', 'loved', 'tags', 'danceability', 'energy', 'key', 'loudness', 'mode',
                'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']]

    network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET, username=username,
                                   password_hash=password_hash)

    recent = get_longevity(user, network, limit=5)

    if recent == True:
        # STEP 1: check if the last updated file exist.
        # if it does, we create a copy and get the old number of scrobbles
        # if it doesn't, we create a file with the headers

        new_scrobbles, pages = get_pages_scrobbled(user, network)
        old_scrobbles, old_date = step1(new_scrobbles, user, path, dest_file, hist_file, columns)
        diff_scrobbles = new_scrobbles - old_scrobbles

        print('Will scrobble', str(diff_scrobbles), 'tracks')

        start = old_scrobbles + 1

        print('New scrobbles: ', new_scrobbles)
        print('Old scrobbles: ', old_scrobbles)
        print('Start: ', start)

        # STEP 2: open the artist and audio features dictionaries

        artists_file = 'artists_tags.json'
        audio_features_file = 'audio_features.json'
        artists_dict, audio_features_dict = open_dicts(artists_file, audio_features_file)

        # STEP 3: collect data for diff scrobbles

        if diff_scrobbles > 0:
            get_tracks(network, user, API_KEY, diff_scrobbles, start, artists_dict, audio_features_dict, path, dest_file,
                        old_date)
    else: print('\n'
                '================================================================================\n'
                "**WARNING**: User has been active lately. Let's wait until they give it a break\n"
                '================================================================================')


if __name__ == '__main__':
    main()
