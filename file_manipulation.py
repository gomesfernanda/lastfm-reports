import csv
from os import listdir
from os.path import isfile, join, exists
import shutil
import json
import pylast
import os


def get_credentials():
    with open('secrets.json', 'r') as file:
        jsonfile = json.load(file)
        API_KEY = jsonfile['API']['API_KEY']
        API_SECRET = jsonfile['API']['API_SECRET']
        username = jsonfile['API']['username']
        password = jsonfile['API']['password_hash']
        password_hash = pylast.md5(password)
    return API_KEY, API_SECRET, username, password, password_hash


def save_file(superlist, path, dest_file):
    with open(path + str(dest_file) + '.csv', mode='a', encoding='utf-8') as test_file:
        test_writer = csv.writer(test_file, delimiter=',')
        for item in superlist:
            test_writer.writerow(item)


def get_last_file(user, name_file):
    mypath = 'export_' + str(user)
    if not exists(mypath):
        os.makedirs(mypath)
    onlyfiles = [f for f in listdir(mypath + '/') if isfile(join(mypath + '/', f))
                                            if str(name_file) + str(user) in join(mypath, f)
                                            if 'partial' not in join(mypath, f)]
    if onlyfiles == []:
        return None
    else:
        return max(onlyfiles)


def create_copy(path, last_file, destfile):
    shutil.copy2(path + last_file, path + destfile + '.csv')


def total_rows(path, filename):
    file = open(path + filename, encoding='utf-8')
    reader = csv.reader(file)
    r_list = list(reader)
    lines = len(r_list)
    last_date = int(r_list[-1][1]) + 2
    return lines - 1, last_date