import pylast
import requests
import json
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import argparse


def progbar(curr, total, full_progbar):
    frac = curr/total
    filled_progbar = round(frac*full_progbar)
    print('\r', '█'*filled_progbar + '-'*(full_progbar-filled_progbar), '[{:>7.2%}]'.format(frac), "[",curr,"|",total,"]", end='')

def setup():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="choose username to collect tracks from", required=True)
    args = parser.parse_args()
    return args

def get_credentials():
    with open("secrets.json", 'r') as file:
        jsonfile = json.load(file)
        API_KEY = jsonfile["API"]["API_KEY"]
        API_SECRET = jsonfile["API"]["API_SECRET"]
        username = jsonfile["API"]["username"]
        password = jsonfile["API"]["password_hash"]
        password_hash = pylast.md5(password)
    return API_KEY, API_SECRET, username, password, password_hash

def get_pages_scrobbled(username, network):
    user = network.get_user(username)
    scrobbles = user.get_playcount()
    pages = int(scrobbles / 200) + (scrobbles % 200 > 0)
    return scrobbles, pages

def get_historical_tracks(user, API_key, network, session):
    todaynow = datetime.now().strftime("%Y%m%d%H%M")
    scrobbles, pages = get_pages_scrobbled(user, network)

    artist_lst = []
    album_lst = []
    track_lst = []
    date_lst = []
    loved_lst = []
    mbid_lst = []
    start_page = 1
    total_pages = pages
    print("Collecting", (total_pages + 1 - start_page), "pages of tracks for the user", user)
    for page in range(start_page, total_pages+1):
        progbar(page, total_pages, total_pages // 10)
        if page % 50 == 0: print("\n========== Saving partials file to disk, page", page ," ==========\n")
        count = 0
        time.sleep(0.05)
        URL = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user="+user+"&api_key="+API_key+"&format=json&extended=1&limit=200&page=" + str(page)
        response = session.get(URL).content
        response_str = response.decode('utf8')
        response_json = json.loads(response_str)
        artist_list = response_json['recenttracks']['track']
        for item in artist_list:
            count+=1
            mbid = item['artist']['mbid']
            artist_name = item['artist']['name']
            album_name = item['album']['#text']
            track_name = item['name']
            loved = item['loved']
            mbid_lst.append(mbid)
            try:
                date_epoch = item['date']['uts']
                date_local = time.strftime('%Y-%m-%d %H:%M', time.localtime(int(date_epoch)))
            except:
                date_local = "♬ now playing ♬"
            date_lst.append(date_local)
            artist_lst.append(artist_name)
            album_lst.append(album_name)
            track_lst.append(track_name)
            loved_lst.append(loved)
            # SAVE PARTIAL FILES EACH 50 PAGES
        if page % 50 == 0:
            history_tracks = pd.DataFrame(
                np.column_stack([date_lst, artist_lst, track_lst, album_lst, loved_lst, mbid_lst]),
                columns=['Date Spain', 'Artist', 'Track', 'Album', 'Loved', 'Tags'])
            history_tracks.to_csv("historical_tracks_" + user + "_" + str(todaynow) + "_partial_" + str(page) + ".csv", sep=',', encoding='utf-8')
    history_tracks = pd.DataFrame(np.column_stack([date_lst, artist_lst, track_lst, album_lst, loved_lst, mbid_lst]), columns=['Date Spain', 'Artist', 'Track', 'Album', 'Loved', 'Tags'])
    history_tracks.to_csv("historical_tracks_" + user + "_" + str(todaynow) + ".csv", sep=',', encoding='utf-8')
    return history_tracks

def main():
    args = setup()
    user = args.user
    API_KEY, API_SECRET, username, password, password_hash = get_credentials()
    s = requests.Session()
    network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET, username=username,
                                   password_hash=password_hash)
    try:
        get_historical_tracks(user, API_KEY, network, s)
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    main()