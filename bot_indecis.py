#!/usr/bin/python3
from sys import argv, exit
import os
import subprocess
from time import sleep
import random
import credentials_unpickler
import tweepy

def autofollow(api, users, start, end):
    try:
        relationships = api.lookup_friendships(screen_names=users[start:end])
        for relationship in relationships:
            if not relationship.is_following:
                print("User is not following", relationship.screen_name)
                api.create_friendship(relationship.screen_name)
            sleep(2)
    except tweepy.TweepError as e:
        print(e)

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

words = []
users = []
hashtags = []
urls = []

input_filename = "tweets_{}.txt".format(account)
output_filename = "tagged_tweets_{}.txt".format(account)

with open(input_filename, 'w', encoding='utf-8') as f:
    texts = []
    for candidat in candidats:
        tweets = api.user_timeline(id=candidat)
        for tweet in tweets:
            # Let's remove trailing spaces and new lines
            original_tweet_text = tweet.text.rstrip(' \n')
            final_tweet_text = []
            
            # Pre-process users, hashtags and urls
            for token in original_tweet_text.split():
                # Incomplete token
                if token.endswith('…'):
                    continue
                
                if token.startswith('@'):
                    users.append(token.rstrip('.:'))
                elif token.startswith('#'):
                    hashtags.append(token)
                elif token.startswith('http'):
                    urls.append(token)
                
                # We'll skip passing urls to the NLP system
                if not token.startswith('http'):
                    final_tweet_text.append(token)
                    
            # Finally append
            texts.append(' '.join(final_tweet_text))
    
    f.write('\n'.join(texts))

path = os.path.dirname(os.path.realpath(__file__))
command = "analyze -f {}/config/bot_indecis/freeling_ca.cfg --outf tagged <{} >{}".format(path, input_filename, output_filename)
print(command)

try:
    subprocess.check_call(command, shell=True)
except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
    print("Error", e)
    api.update_status(status="@msonsona error with freeling!")
    exit()

with open(output_filename, 'r', encoding='utf-8') as tagged_tweets_file:
    line_no = 1
    tagged_lines = []
    tagged_line = []
    joining_buffer = []
    # keep_buffering = False
    word_pos = {}
    
    for line in tagged_tweets_file:
        if line == "\n":
            tagged_lines.append(tagged_line)
            tagged_line = []
        else:
            splits = line.split()
            # If can't obtain PoS tag, continue
            if len(splits) < 3:
                continue
            
            word, lemma, pos_tag, prob = splits[0:4]
            
            if word in ['RT', ':', '…']:
                continue
            if word in ['@', '#', 'https://t.co/']:# or word.startswith('http'):
                joining_buffer = word
                continue
            
            if joining_buffer:
                if joining_buffer.startswith('@'):
                    pos_tag = "User"
                elif joining_buffer.startswith('#'):
                    pos_tag = "Hashtag"
                elif joining_buffer.startswith('http'):
                    pos_tag = "Url"
                
                word = joining_buffer + word
                joining_buffer = ''
            
            tagged_line.append((word, pos_tag))
            
            # Replace underscores for spaces on non-specific words
            # (introduced by the tokenizer for e.g. Proper Nouns)
            if pos_tag not in ["User", "Hashtag", "Url"]:
                word = word.replace('_', ' ')
            
            if pos_tag not in word_pos:
                word_pos[pos_tag] = []
            
            word_pos[pos_tag].append(word)
        
        line_no += 1
    
    tweet_ok = False
    retries = 0
    while not tweet_ok and retries < 10:
        tweet = ""
        
        # Randomly select a PoS structure
        sentence_pos = random.choice(tagged_lines)
        print(sentence_pos)
        
        for token, pos_tag in sentence_pos:
            # Randomly select a token for the current PoS
            token_ok = False
            while not token_ok:
                selected_word = random.choice(word_pos[pos_tag])
                print("Looking for a", pos_tag, ", like ", token, ":", selected_word)
                if pos_tag in ["User", "Hashtag", "Url"]:
                    # Check there are no duplicate users, HT or urls
                    if token not in tweet:
                        token_ok = True
                else:
                    token_ok = True
                
            tweet += ' ' + selected_word
        
        # Strip leading and trailing whitespace
        tweet = tweet.strip()
        
        if len(tweet) <= 140:
            # We can tweet!
            tweet_ok = True
            print("Tweet: ", tweet)
            if len(tweet) < 140:
                if tweet.startswith('@'):
                    # Add a period to make the mention public
                    tweet = '.' + tweet
                
                # Use trending hashtag
                woeid_spain = 23424950
                trends_json = api.trends_place(woeid_spain)
                trends = trends_json[0]['trends']
                whitelist = ['Arrimadas', 'Ciutadans', 'Rivera', 'Cs', 'Ciudadanos', 'CUP', 'governemnos', 'Baños', 'Espadaler', 'Unió', 'Unio', 'Rajoy', 'PP', 'popular', 'Albiol', 'PSOE', 'socialista', 'Iceta', 'PSC', 'Rabell', 'CSQEP', 'podem', 'Romeva', 'JxS', 'JuntsPelSi', 'JuntsPelSí', 'eleccions']
                relevant_trends = []
                for trend in trends:
                    if trend['name'].startswith('#'):
                        for word in whitelist:
                            if word in trend['name']:
                                print("Found {} in {}".format(word, trend))
                                relevant_trends.append(trend['name'])
                                
                if relevant_trends:
                    trend_ok = False
                    retries = 0
                    while not trend_ok and retries < 5:
                        selected_trend = random.choice(relevant_trends)
                        if selected_trend not in tweet:
                            if len(tweet + ' ' + selected_trend) <= 140:
                                tweet += ' ' + selected_trend
                                trend_ok = True
                        retries += 1
                        
                # Try to add a url too!
                if len(tweet) < 140:
                    url_ok = False
                    retries = 0
                    while not url_ok and retries < 5:
                        selected_url = random.choice(urls)
                        if len(tweet + ' ' + selected_url) <= 140:
                            tweet += ' ' + selected_url
                            url_ok = True
                        retries += 1
            
            print("Final tweet: ", tweet)
            api.update_status(status=tweet)
        else:
            # Retry for 10 times
            print("Sorry, retrying, got", tweet)
            retries += 1

# Auto-follow mentioned users
# Now it seems we must lookup batches of 100 users to check following
users = list(set(users))
previous_i = 0
step = 100
for i in range(step, len(users), step):
    autofollow(api, users, previous_i, i)
    previous_i = i
if previous_i < len(users):
    autofollow(api, users, previous_i, len(users))

