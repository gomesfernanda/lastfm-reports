import pylast
import requests
import json
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta

with open("secrets.json", 'r') as file:
    jsonfile = json.load(file)
    API_KEY = jsonfile["API"]["API_KEY"]
    API_SECRET = jsonfile["API"]["API_SECRET"]
    username = jsonfile["API"]["username"]
    password = jsonfile["API"]["password_hash"]
    password_hash = pylast.md5(password)

s = requests.Session()

network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET,
                               username=username, password_hash=password_hash)


def get_bio(artist_name):
    artist = network.get_artist(artist_name)
    bio = artist.get_bio_summary()
    return bio


def get_friends(username, limit=400):
    user = network.get_user(username)
    friends_list = []
    friends_item = user.get_friends(300)
    total_friends = len(friends_item)
    for i, friend in enumerate(friends_item):
        thisfriend = []
        try:
            name = friend.name
            playcount = friend.get_playcount()
            country = friend.get_country()
            thisfriend.append(name)
            thisfriend.append(country)
            thisfriend.append(playcount)
            friends_list.append(thisfriend)
        except:
            next
    friends_df = pd.DataFrame(friends_list, columns=["Name", "Country", "Playcount"])
    friends_sorted = friends_df.sort_values(by="Playcount", ascending=False)
    return friends_sorted


def get_loved_tracks(username):
    loved_list= []
    user = network.get_user(username)
    loved_tracks = user.get_loved_tracks()
    for loved in loved_tracks:
        loved_track = []
        loved_track.append(loved.track.artist)
        loved_track.append(loved.track.title)
        loved_list.append(loved_track)
    return loved_list


def get_recent_tracks(user, limit=20):
    recent_tracks_list = []
    user = network.get_user(user)
    recent_tracks = user.get_recent_tracks(limit)
    for i, track in enumerate(recent_tracks):
        track_list = []
        track_list.append(track.track.artist)
        track_list.append(track.track.title)
        track_list.append(track.timestamp)
        recent_tracks_list.append(track_list)
    return recent_tracks_list


def get_historical_tracks(user, API_key):
    todaynow = datetime.now().strftime("%Y%m%d%H%M")
    pages = get_pages_scrobbled(user, API_key)

    artist_lst = []
    album_lst = []
    track_lst = []
    date_lst = []
    loved_lst = []
    mbid_lst = []
    start_page = 1
    total_pages = pages

    print("Collecting", (total_pages+1-start_page), "pages of tracks for the user", user)
    for page in range(start_page, total_pages+1):
        count = 0
        time.sleep(0.05)
        URL = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user="+user+"&api_key="+API_key+"&format=json&extended=1&limit=200&page="+str(page)
        response = s.get(URL).content
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
            print(page, "/", total_pages, artist_name, "-", track_name, "-", date_local)
            # SAVE PARTIAL FILES EACH 10 PAGES

            if page % 10 == 0:
                history_tracks = pd.DataFrame(
                    np.column_stack([date_lst, artist_lst, track_lst, album_lst, loved_lst, mbid_lst]),
                    columns=['Date Spain', 'Artist', 'Track', 'Album', 'Loved', 'Tags'])
                history_tracks.to_csv("historical_tracks_" + user + "_" + todaynow + "_partial_" + page + ".csv", sep=',', encoding='utf-8')
    history_tracks = pd.DataFrame(np.column_stack([date_lst, artist_lst, track_lst, album_lst, loved_lst, mbid_lst]), columns=['Date Spain', 'Date Brazil', 'Artist', 'Track', 'Album', 'Loved', 'Tags'])
    history_tracks.to_csv("historical_tracks_" + user + "_" + todaynow + ".csv", sep=',', encoding='utf-8')
    return history_tracks


def get_pages_scrobbled(username):
    user = network.get_user(username)
    scrobbles = user.get_playcount()
    pages = int(scrobbles / 200) + (scrobbles % 200 > 0)
    return pages


def get_clean_top_tags(artist, limit=20):
    artist = network.get_artist(artist)
    toptags = artist.get_top_tags(limit)
    toptags_list = []
    unify_artist = str(artist).lower().replace(" ", "")
    bad_tags = [unify_artist, "seen live"]
    for i, tag in enumerate(toptags):
        toptag = str(tag.item).lower()
        toptag_unified = toptag.replace(" ", "")
        if toptag not in bad_tags and toptag_unified not in bad_tags:
            toptags_list.append(toptag)
    return toptags_list