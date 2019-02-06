import pylast
import json
import argparse
import pandas as pd

def setup():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="user whose you wanna see loved tracks", required=True)
    parser.add_argument("-l", "--limit", help="limit of loved tracks you wanna see, default is all'", required=False)
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

def get_loved_tracks(username, network, limit):
    loved_list = [['Artist', 'Track', 'Date loved']]
    user = network.get_user(username)
    loved_tracks = user.get_loved_tracks(limit=limit)
    for loved in loved_tracks:
        loved_track = []
        artist = loved.track.artist
        artist_name = artist.get_name()
        loved_track.append(artist_name)
        loved_track.append(loved.track.title)
        loved_track.append(loved.date)
        loved_list.append(loved_track)
    loved_df = pd.DataFrame(loved_list[1:], columns=loved_list[0])
    return loved_df

def main():
    args = setup()
    user = args.user
    limit = args.limit
    if limit == None:
        limit_pass = 50
    elif limit == "all":
        limit_pass = None
    else:
        limit_pass = int(limit)
    API_KEY, API_SECRET, username, password, password_hash = get_credentials()
    network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET, username=username, password_hash=password_hash)
    loved_df = get_loved_tracks(user, network=network, limit=limit_pass)
    print(loved_df)

if __name__ == '__main__':
    main()

