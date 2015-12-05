#!/usr/bin/python3
from sys import argv, exit
import subprocess
import random
import credentials_unpickler
import tweepy

script, account = argv
credentials = credentials_unpickler.unpickle(account)

auth = tweepy.OAuthHandler(credentials['consumer_key'], credentials['consumer_secret'])
auth.set_access_token(credentials['access_token'], credentials['access_token_secret'])

api = tweepy.API(auth)

candidats = [
    'agarzon', # Alberto Garzón (IU)
    'pablo_iglesias_', # Pablo Iglesias (Podemos)
    'marianorajoy', # Mariano Rajoy (PP)
    'albert_rivera', # Albert Rivera (C's)
    'sanchezcastejon', # Pedro Sánchez (PSOE)
    ]

input_filename = "tweets_{}.txt".format(account)
output_filename = "tagged_tweets_{}.txt".format(account)

with open(input_filename, 'w', encoding='utf-8') as f:
    texts = []
    for candidat in candidats:
        tweets = api.user_timeline(id=candidat)
        for tweet in tweets:
            texts.append(tweet.text)
    
    f.write('\n'.join(texts))

command = "analyze -f freeling_es.cfg --outf tagged <{} >{}".format(input_filename, output_filename)

try:
    subprocess.check_call(command, shell=True)
except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
    print("Error", e)
    api.update_status(status="@msonsona error with freeling!")
    sys.exit()

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
            # (introduced by the tokenizer)
            if not pos_tag in ["User", "Hashtag", "Url"]:
                word = word.replace('_', ' ')
            
            if not pos_tag in word_pos:
                word_pos[pos_tag] = []
            
            word_pos[pos_tag].append(word)
            
        line_no += 1
    
    
    tweet_ok = False
    retries = 0
    while not tweet_ok:
        tweet = ""
        
        # Randomly select a PoS structure
        sentence_pos = random.choice(tagged_lines)
        print(sentence_pos)
        
        for token, pos_tag in sentence_pos:
            # Randomly select a token for the current PoS
            selected_word = random.choice(word_pos[pos_tag])
            print("Looking for a", pos_tag, ", like ", token, ":", selected_word)
            tweet += ' ' + selected_word
        
        if len(tweet) < 140:
            # We can tweet!
            tweet_ok = True
            print("Tweet: ", tweet)
            api.update_status(status=tweet)
        else:
            # Retry for 10 times
            print("Sorry, retrying, got", tweet)
            retries += 1
        
        if retries == 10:
            print("Sorry, no tweet")
            break
