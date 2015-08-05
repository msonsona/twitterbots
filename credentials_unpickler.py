#!/usr/bin/python3
from sys import argv
import pickle

script, account = argv

filename = "%s.pickle" % account

with open(filename, 'rb') as f:
    credentials = pickle.load(f)
    print(credentials)