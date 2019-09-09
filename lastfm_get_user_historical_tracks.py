import pylast
import requests
import json
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import argparse
import os
from bs4 import BeautifulSoup

def progbar(curr, total, unit, full_progbar):
    frac = curr/total
    filled_progbar = round(frac*full_progbar)
    print('\r Progress: |', '█'*filled_progbar + '-'*(full_progbar-filled_progbar), '| [{:>7.2%}]'.format(frac), " [ ", unit, curr,"|",total,"]", end='')

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


######################################
#                                    #
# BUILD A DICTIONARY OF ARTISTS TAGS #
#                                    #
######################################

def get_artists_number(user):
    url = "https://www.last.fm/user/" + str(user)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    tag_art = soup.findAll('p', {'class': "header-metadata-display"})
    artists = tag_art[1].text.replace(",","")
    return artists

def get_tags(artist, network, limit=20):
    artist_ = network.get_artist(artist)
    try:
        toptags = artist_.get_top_tags(limit)
        toptags_list = []
        unify_artist = str(artist_).lower().replace(" ", "")
        bad_tags = [unify_artist, "seen live"]
        for i, tag in enumerate(toptags):
            toptag = str(tag.item).lower()
            toptag_unified = toptag.replace(" ", "")
            if toptag not in bad_tags and toptag_unified not in bad_tags:
                toptags_list.append(toptag)
    except Exception as e:
        toptags_list = []
    return toptags_list

def get_users_artists(user, API_key, network):
    perpage = 200
    total_artists = get_artists_number(user)
    print("Collecting", total_artists, "artists for the user", user)
    pages = (int(total_artists) // perpage) + 1
    artist_dict = {}
    cont = 0
    for i in range(pages):
        print("\nPage ", i + 1)
        URL = "http://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user=" + user + "&api_key=" + API_key + "&format=json&period=overall&limit=" + str(perpage) + "&page=" + str(1 + i)
        s = requests.Session()
        r = s.get(URL).content.decode("utf-8")
        r_json = json.loads(r)
        topartists = r_json["topartists"]
        artists_list = topartists["artist"]
        for n, art in enumerate(artists_list):
            progbar(int(cont + 1), int(total_artists), "artist", 20)
            cont += 1
            artist_name = art["name"]
            artist_tags = get_tags(artist_name, network)
            artist_dict[artist_name] = artist_tags
    with open('artists_' + str(user) + '.json', 'w') as fp:
        json.dump(artist_dict, fp)
    return artist_dict


#############################
#                           #
# COLLECT HISTORICAL TRACKS #
#                           #
#############################


def get_pages_scrobbled(username, network):
    user = network.get_user(username)
    scrobbles = user.get_playcount()
    pages = int(scrobbles / 200) + (scrobbles % 200 > 0)
    return scrobbles, pages

def get_historical_tracks(user, API_key, artists_dict, network, session):
    todaynow = datetime.now().strftime("%Y%m%d%H%M")
    directory = "export_" + str(user) + "_" + str(todaynow[:8])
    scrobbles, pages = get_pages_scrobbled(user, network)
    artist_lst = []
    album_lst = []
    track_lst = []
    date_lst = []
    loved_lst = []
    tags_lst = []
    start_page = 1
    total_pages = pages
    print("Collecting", (total_pages + 1 - start_page), "pages of tracks for the user", user)
    for page in range(start_page, total_pages+1):
        progbar(page, total_pages, "page", 20)
        time.sleep(0.1)
        URL = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=" + user + "&api_key="+ API_key + "&format=json&extended=1&limit=200&page=" + str(page)
        response = session.get(URL).content
        response_str = response.decode('utf8')
        response_json = json.loads(response_str)
        artist_list = response_json['recenttracks']['track']
        for item in artist_list:
            artist_name = item['artist']['name']
            if artist_name not in artists_dict:
                top_tags = get_tags(artist_name, network)
                artists_dict[artist_name] = top_tags
                tags_lst.append(top_tags)
            elif artist_name in artists_dict:
                tags_lst.append(artists_dict[artist_name])
            album_name = item['album']['#text']
            track_name = item['name']
            loved = item['loved']
            try:
                date_epoch = item['date']['uts']
                date_local = datetime.fromtimestamp(int(date_epoch))
            except:
                date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                date_local = datetime.strptime(date_now, '%Y-%m-%d %H:%M:%S')
            date_lst.append(date_local)
            artist_lst.append(artist_name)
            album_lst.append(album_name)
            track_lst.append(track_name)
            loved_lst.append(loved)

        # SAVE PARTIAL FILES EACH 50 PAGES
        if page % 50 == 0:
            if not os.path.exists(directory):
                os.makedirs(directory)
            print("\n\n========== Saving partials file to disk, page", page, "==========\n")
            history_tracks = pd.DataFrame(
                np.column_stack([date_lst, artist_lst, track_lst, album_lst, loved_lst, tags_lst]),
                columns=['Date Spain', 'Artist', 'Track', 'Album', 'Loved', 'Tags'])
            history_tracks.to_csv(directory + "/historical_tracks_" + user + "_" + str(todaynow) + "_partial_" + str(page) + ".csv", sep=',', encoding='utf-8')
    with open('artists_' + str(user) + '.json', 'w') as fp:
        json.dump(artists_dict, fp)
    if not os.path.exists(directory):
        os.makedirs(directory)
    history_tracks = pd.DataFrame(np.column_stack([date_lst, artist_lst, track_lst, album_lst, loved_lst, tags_lst]), columns=['Date Spain', 'Artist', 'Track', 'Album', 'Loved', 'Tags'])
    history_tracks.to_csv(directory + "/historical_tracks_" + user + "_" + str(todaynow) + ".csv", sep=',', encoding='utf-8')
    return history_tracks

def main():
    args = setup()
    user = args.user
    API_KEY, API_SECRET, username, password, password_hash = get_credentials()
    s = requests.Session()
    network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET, username=username, password_hash=password_hash)
    try:
        try:
            with open('artists_' + str(user) + '.json') as json_file:
                artists_dict = json.load(json_file)
            print("A file with artists tags already exists.")
        except:
            print("A file with artists tags doesn't exist. Building the file.")
            artists_dict = get_users_artists(user, API_KEY, network)
        print("\n\n===========================================================\n")
        get_historical_tracks(user, API_KEY, artists_dict, network, s)
    except Exception as e:
        print("\n\nError:", e)

if __name__ == '__main__':
    main()