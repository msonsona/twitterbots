#!/usr/bin/python3
import os
import pickle

def unpickle(account):
    filename = os.path.dirname(os.path.realpath(__file__))
    filename = "{}/credentials/{}.pickle".format(filename, account)
    
    with open(filename, 'rb') as f:
        credentials = pickle.load(f)
    
    return credentials