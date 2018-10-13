import pylast
import requests
import json

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


def get_bio():
    artist = network.get_artist("Elton John")
    bio = artist.get_bio_summary()
    return bio


def get_friends(username, limit=400):
    user = network.get_user(username)
    friends_list = []
    friends_item = user.get_friends(300)
    for friend in friends_item:
        friends_list.append(friend.name)
    return friends_list


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


def get_historical_tracks():
    return "TBD"


def get_pages_scrobbled(username):
    user = network.get_user(username)
    scrobbles = user.get_playcount()
    pages = int(scrobbles / 200) + (scrobbles % 200 > 0)
    return pages


def get_clean_top_tags(artist, limit=20):
    artist = network.get_artist(artist)
    toptags = artist.get_top_tags(limit)
    toptags_list = []
    for i, tag in enumerate(toptags):
        toptag = tag.item
        toptags_list.append(toptag)
    return toptags_list