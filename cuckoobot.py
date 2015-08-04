#!/usr/bin/python3
from datetime import datetime

now = datetime.utcnow()

hour = now.hour

hour = hour % 12
if (hour == 0):
    hour = 12

sound = ""
for i in range(hour):
    sound += "🐤cuckoo "

tweet = sound
print(tweet)
