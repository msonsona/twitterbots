#!/usr/bin/python3
from sys import argv
from datetime import date, timedelta
import time

import tweepy

import credentials_unpickler


def insert_in_top10(top10, position, element):
    # 1- insert into corresponding position
    top10.insert(position, element)
    # 2- deleting last element of top10
    del(top10[-1])

def autofollow(api, users):
    try:
        relationships = api.lookup_friendships(screen_names=users)
        for relationship in relationships:
            if not relationship.is_following:
                print("User is not following", relationship.screen_name)
                api.create_friendship(relationship.screen_name)
            time.sleep(2)
    except tweepy.TweepError as e:
        print(e)

start = time.time()

script, account = argv
credentials = credentials_unpickler.unpickle(account)

auth = tweepy.OAuthHandler(credentials['consumer_key'], credentials['consumer_secret'])
auth.set_access_token(credentials['access_token'], credentials['access_token_secret'])

api = tweepy.API(auth)

q = ['#screenshotsaturday', '#mobilegames', '#gamedev', '#madewithunity', '#ue4', '#indiedev', '#pixelart']

today = date.today()
weekday = today.weekday()
week = timedelta(days=7)

print("Today is ", today, " | weekday ", weekday)
print("So I'll query for", q[weekday])

top10 = [{'id':0, 'likes':-1, 'user_name':''} for i in range(10)]

# Sort tweets for the given keyword by likes, keep only the top 10
num_tweets = 0
num_likes = 0
for page in tweepy.Cursor(api.search, q=q[weekday], since=today-week, count=100).pages():
    for tweet in page:
        num_tweets += 1
        num_likes += tweet.favorite_count
        
        # print(tweet.id, tweet.favorite_count)
        if tweet.favorite_count >= top10[0]['likes']:
            insert_in_top10(top10, 
                            0, 
                            {'id':tweet.id,
                             'likes':tweet.favorite_count,
                             'user_name':tweet.user.screen_name})
        elif tweet.favorite_count <= top10[-1]['likes']:
            pass
        else:
            # print("sorting")
            for i in range(9, -1, -1):
                if top10[i]['likes'] > tweet.favorite_count:
                    insert_in_top10(top10, 
                                    i+1, 
                                    {'id':tweet.id,
                                     'likes':tweet.favorite_count,
                                     'user_name':tweet.user.screen_name})
                    break
    print(num_tweets)

for t in top10:
    print(t)

e = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟']
top = 0
if top10[9]['likes'] > 0:
    # Top10
    top = 10
elif top10[4]['likes'] > 0:
    # Top5
    top = 5
elif top10[2]['likes'] > 0:
    # Top3
    top = 3
else:
    # not enough likes !?
    pass
    
if top:
    users = []
    text = "{} Top{} on {} after {} tweets and {}💚"
    ok_status = text.format(q[weekday], 
                            top, 
                            date.today(), 
                            num_tweets, 
                            num_likes)
    original_status = api.update_status(status=ok_status)
    print(original_status.text)
    original_status_id = original_status.id

    for i in range(top-1, -1, -1):
        users.append(top10[i]['user_name'])
        text = "🔝{} {}💚 to @{} https://twitter.com/{}/status/{}"
        tweet = text.format(e[i], 
                            top10[i]['likes'], 
                            top10[i]['user_name'], 
                            top10[i]['user_name'], 
                            top10[i]['id'])
        reply = api.update_status(status=tweet,
                                  in_reply_to_status_id=original_status_id)
        # keep id for iteration
        original_status_id = reply.id
        time.sleep(10)
    
    # follow users in the top ranking
    autofollow(api, users)

# Summary notification
status_update = "@msonsona "
if top:
    status_update += "top{} ".format(top)
else:
    status_update += "💩 not enough likes "

status_update += "for {} on {}, {} tweets ranked in {} secs".format(
    q[weekday], 
    date.today(), 
    num_tweets, 
    round(time.time() - start, 2)
    )
api.update_status(status=status_update)
print(status_update.text)