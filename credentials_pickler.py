#!/usr/bin/python3
import pickle

account = input("1. Enter the account username > ")
consumer_key = input("2. Enter the consumer_key > ")
consumer_secret = input("3. Enter the consumer_secret > ")
access_token = input("4. Enter the access_token > ")
access_token_secret = input("5. Enter the access_token_secret > ")

credentials = {
    'account': account,
    'consumer_key': consumer_key,
    'consumer_secret': consumer_secret,
    'access_token': access_token,
    'access_token_secret': access_token_secret
}

print(credentials)

filename = "%s.pickle" % account
with open(filename, 'wb') as file:
    pickle.dump(credentials, file, pickle.HIGHEST_PROTOCOL)