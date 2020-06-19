import pylast
import json
import pandas as pd
import argparse
import datetime


def setup():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="choose username to collect tracks from", required=True)
    parser.add_argument("-l", "--limit", help="how many recent tracks ytou wanna show")
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


def get_recent_tracks(user, network, limit=5):
    recent_tracks_list = [['Artist name', 'Track title', 'Date listened']]
    user = network.get_user(user)
    recent_tracks = user.get_recent_tracks(limit)
    for i, track in enumerate(recent_tracks):
        track_list = []
        track_list.append(track.track.artist.name)
        track_list.append(track.track.title)
        time_epoch = datetime.datetime.fromtimestamp(int(track.timestamp))
        track_list.append(time_epoch)
        recent_tracks_list.append(track_list)
    recent_tracks_df = pd.DataFrame(recent_tracks_list[1:], columns=recent_tracks_list[0])
    return recent_tracks_df


def get_longevity(user, network, limit=5):
    df = get_recent_tracks(user, network, limit)
    last = df['Date listened'].iloc[0]
    print('Last activity:', last)
    difference = datetime.datetime.now() - last
    seconds_in_day = 24 * 60 * 60
    interval = divmod(difference.days * seconds_in_day + difference.seconds, 60)
    mins = interval[0]
    if mins > 120:
        return True
    else:
        return False