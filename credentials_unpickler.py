#!/usr/bin/python3
from sys import argv
import pickle

script, input_file = argv

filename = "%s.pickle" % input_file

with open(filename, 'rb') as f:
    credentials = pickle.load(f)
    print(credentials)