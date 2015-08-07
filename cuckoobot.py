#!/usr/bin/python3
from sys import argv
from datetime import datetime
import credentials_unpickler
import tweepy

script, account = argv
credentials = credentials_unpickler.unpickle(account)

now = datetime.utcnow()

hour = now.hour % 12

tweet = "It's "
if hour == 0:
    hour = 12
    tweet += "🕛"
elif hour == 1:
    tweet += "🕐"
elif hour == 2:
    tweet += "🕑"
elif hour == 3:
    tweet += "🕒"
elif hour == 4:
    tweet += "🕓"
elif hour == 5:
    tweet += "🕔"
elif hour == 6:
    tweet += "🕕"
elif hour == 7:
    tweet += "🕖"
elif hour == 8:
    tweet += "🕗"
elif hour == 9:
    tweet += "🕘"
elif hour == 10:
    tweet += "🕙"
elif hour == 11:
    tweet += "🕚"

tweet += "!\n"

for i in range(hour):
    tweet += "🐤cuckoo "

auth = tweepy.OAuthHandler(credentials['consumer_key'], credentials['consumer_secret'])
auth.set_access_token(credentials['access_token'], credentials['access_token_secret'])

api = tweepy.API(auth)

api.update_status(status=tweet)
