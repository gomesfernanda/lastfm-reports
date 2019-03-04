import pylast
import requests
import json
import pandas as pd
import time
import argparse


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

def get_recent_tracks(user, network, limit=20):
    recent_tracks_list = [['Artist name', 'Track title', 'Date listened']]
    user = network.get_user(user)
    recent_tracks = user.get_recent_tracks(limit)
    for i, track in enumerate(recent_tracks):
        track_list = []
        track_list.append(track.track.artist.name)
        track_list.append(track.track.title)
        time_epoch = track.timestamp
        time_local = time.strftime('%Y-%m-%d %H:%M', time.localtime(int(time_epoch)))
        track_list.append(time_local)
        recent_tracks_list.append(track_list)
    recent_tracks_df = pd.DataFrame(recent_tracks_list[1:], columns=recent_tracks_list[0])
    return recent_tracks_df

def main():
    args = setup()
    API_KEY, API_SECRET, username, password, password_hash = get_credentials()
    s = requests.Session()
    network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET, username=username,
                                   password_hash=password_hash)
    user = args.user
    try:
        limit = int(args.limit)
    except:
        print("================================================\nLimit not recognized as integer, using limit=20\n================================================")
        limit=20
    try:
        print(get_recent_tracks(user, network, limit))
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()

