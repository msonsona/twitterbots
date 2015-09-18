#!/usr/bin/python3
from sys import argv
from datetime import datetime
import credentials_unpickler
import tweepy

script, account = argv
credentials = credentials_unpickler.unpickle(account)

auth = tweepy.OAuthHandler(credentials['consumer_key'], credentials['consumer_secret'])
auth.set_access_token(credentials['access_token'], credentials['access_token_secret'])

api = tweepy.API(auth)

candidats = [
    'inesarrimadas', # Inés Arrimadas (C's)
    'antoniobanos_', # Antonio Baños (CUP)
    'ramon_espadaler', # Ramon Espadaler (UDC)
    'albiol_xg', # Xavier García Albiol (PP)
    'miqueliceta', # Miquel Iceta (PSC)
    'lluisrabell', # Lluís Rabell (CSQEP)
    'raulromeva', # Raül Romeva (JxS)
    ]

texts = []

for candidat in candidats:
    print("Fetching tweets for candidate", candidat)
    tweets = api.user_timeline(id=candidat)
    
    for tweet in tweets:
        texts.append(tweet.text)

print(texts)

words = []

for text in texts:
    words.append(text.split())

print(words)
