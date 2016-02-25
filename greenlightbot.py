#!/usr/bin/python3
import credentials_unpickler
import tweepy

def insert_in_top10(top10, position, element):
    # 1- insert into corresponding position
    top10.insert(position, element)
    # 2- deleting last element of top10
    del(top10[-1])

q = ['#screenshotsaturday', '#mobilegames', '#gamedev', '#madewithunity', '#ue4', '#indiedev', '#pixelart']
w = date.today().weekday()

print("Today is ", date.today(), " | weekday ", date.today().weekday())
print("So I'll query for", q[w])

top10 = [{'id':0, 'likes':-1} for i in range(10)]

for page in tweepy.Cursor(api.search, q=q[w], since='2016-02-20', until='2016-02-21').pages(5):
    for tweet in page:
        # pprint(tweet._json)
        print(tweet.id, tweet.favorite_count)
        if tweet.favorite_count >= top10[0]['likes']:
            insert_in_top10(top10, 0, {'id':tweet.id,
                                       'likes':tweet.favorite_count})
        elif tweet.favorite_count <= top10[-1]['likes']:
            pass
        else:
            print("sorting")
            for i in range(9,-1,-1):
                if top10[i]['likes'] > tweet.favorite_count:
                    insert_in_top10(top10, i+1, {'id':tweet.id,
                                                 'likes':tweet.favorite_count})
                    break
print(top10)

for t in top10:
    print(t)