import pylast
import json
import argparse
import pandas as pd

def setup():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="user whose you wanna see friends", required=True)
    parser.add_argument("-l", "--limit", help="limit of friends you wanna see, default is 10'", required=False, default=10)
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

def get_friends(username, network, limit=400):
    user = network.get_user(username)
    friends_list = []
    friends_item = user.get_friends(limit)
    for i, friend in enumerate(friends_item):
        thisfriend = []
        name = friend.name
        playcount = friend.get_playcount()
        thisfriend.append(name)
        try:
            country = friend.get_country().name
        except:
            country = "None"
        thisfriend.append(country)
        thisfriend.append(playcount)
        friends_list.append(thisfriend)
    friends_df = pd.DataFrame(friends_list, columns=["Name", "Country", "Playcount"])
    friends_sorted = friends_df.sort_values(by="Playcount", ascending=False)
    return friends_sorted

def main():
    args = setup()
    user = args.user
    try:
        limit = int(args.limit)
    except:
        limit = None
    API_KEY, API_SECRET, username, password, password_hash = get_credentials()
    network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET, username=username, password_hash=password_hash)
    user_friends = get_friends(user, network, limit=limit)
    print(user_friends)

if __name__ == '__main__':
    main()