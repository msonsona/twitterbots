#!/usr/bin/python3
import pickle

account = input("1. Enter the account username > ")
consumer_key = input("2. Enter the consumer_key > ")
consumer_secret = input("3. Enter the consumer_secret > ")
access_token = input("4. Enter the access_token > ")
access_token_secret = input("5. Enter the access_token_secret > ")

extra_info = 'y'
extra_tokens = {}
while extra_info == 'y':
    extra_info = input("Do you want to store any extra key - value pair? (y/n) > ")
    if extra_info == 'y':
        extra_info_key = input("First, enter the name (key) > ")
        extra_info_value = input("Second, enter the value to store > ")
        extra_tokens[extra_info_key] = extra_info_value
    

credentials = {
    'account': account,
    'consumer_key': consumer_key,
    'consumer_secret': consumer_secret,
    'access_token': access_token,
    'access_token_secret': access_token_secret
}

if len(extra_tokens):
    credentials['extra_tokens'] = extra_tokens

print(credentials)

filename = "%s.pickle" % account
with open(filename, 'wb') as file:
    pickle.dump(credentials, file, pickle.HIGHEST_PROTOCOL)