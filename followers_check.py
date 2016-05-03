#!/usr/bin/python3
import tweepy
import credentials_unpickler

account = 'unaltrebot'
credentials = credentials_unpickler.unpickle(account)

auth = tweepy.OAuthHandler(credentials['consumer_key'], credentials['consumer_secret'])
auth.set_access_token(credentials['access_token'], credentials['access_token_secret'])

api = tweepy.API(auth)

user = api.get_user('@msonsona'

list_members = api.list_members(owner_screen_name='@msonsona', slug='my-twitter-bots')

members_followers = 0
for member in list_members:
    members_followers += member.followers_count

if members_followers > user.followers_count:
    tweet = "Hola @msonsona, els teus bots tenim més followers que tu! {} vs {}". format(members_followers, user.followers_count)
    api.update_status(status=tweet)
else:
    tweet = "Hola @msonsona, els teus bots encara no tenim més followers que tu: {} vs {}". format(members_followers, user.followers_count)
    api.send_direct_message("msonsona", text=tweet)

