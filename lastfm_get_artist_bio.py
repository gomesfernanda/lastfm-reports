import pylast
import json
import argparse

def setup():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--artist", help="choose which artist you wanna get bio", required=True)
    parser.add_argument("-f", "--function", help="choose 'bio' or 'tags'", required=True)
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

def get_bio_tags(artist, network, limit=20):
    artist = network.get_artist(artist)
    bio = artist.get_bio_summary()
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
    return bio, toptags_list

def main():
    args = setup()
    artist = args.artist
    API_KEY, API_SECRET, username, password, password_hash = get_credentials()
    network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET, username=username, password_hash=password_hash)
    func = args.function
    bio, toptags = get_bio_tags(artist, network)
    if func == "bio":
        print(bio)
    elif func == "tags":
        print(toptags)
    else:
        print("No functions for your input")

if __name__ == '__main__':
    main()