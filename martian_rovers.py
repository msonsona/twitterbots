#!/usr/bin/python3
from sys import argv
import random
import credentials_unpickler
import tweepy

import os
import json
import requests

from io import BytesIO
from PIL import Image, ImageColor, ImageOps, ImageFont, ImageDraw

script, account_1, account_2 = argv
credentials_1 = credentials_unpickler.unpickle(account_1)
credentials_2 = credentials_unpickler.unpickle(account_2)

if credentials_1.get('extra_tokens'):
    nasa_api_key = credentials_1['extra_tokens']['nasa_api_key']
else:
    nasa_api_key = 'DEMO_KEY'

# Obtain rovers info
rovers_url_base = 'https://api.nasa.gov/mars-photos/api/v1/rovers/'
payload = {'api_key': nasa_api_key}
rovers_req = requests.get(rovers_url_base, params=payload)
rovers_json = rovers_req.json()

# Determine image to obtain
need_images = True
while need_images:
    # Randomly select a rover, a sol (martian day), and a camera
    rover = random.choice(rovers_json['rovers'])
    sol = random.randint(0, rover['max_sol'])
    
    # Select a camera from the intersection of the rover cams and the cool cams
    selected_camera = False
    while not selected_camera:
        camera = random.choice(rover['cameras'])
        
        # Cool cams: 
        cool_cams = ['FHAZ', 'RHAZ', 'NAVCAM', 'MINITES', 'MAST']
        if camera['name'] in cool_cams:
            selected_camera = True
    
    print("Checking images for ", rover['name'], camera['name'])
    
    # Call the NASA api and obtain an image
    payload['camera'] = camera['name']
    payload['sol'] = sol
    rover_img_req = requests.get(rovers_url_base + rover['name'] + '/photos', params=payload)
    
    # If the request is successful, we don't need more images
    if (rover_img_req.status_code == 200):
        need_images = False
    
images_json = rover_img_req.json()
selected_photo = random.choice(images_json['photos'])

# Obtain the image
r = requests.get(selected_photo['img_src'])
img = Image.open(BytesIO(r.content))
img_name = selected_photo['img_src'].split('/').pop()
print("Image ", img_name, ", mode = ", img.mode)

if img.mode != 'L':
    print("Converting image to mode 'L'")
    img = img.convert('L')
    print("Image mode = ", img.mode)

# Modify the image 1
img_tmp_1 = ImageOps.expand(img, 5, 0) # black inset border
img_tmp_2 = ImageOps.expand(img_tmp_1, 150, (255, 255, 255)) # white border

# Check if border is white
if img_tmp_2.getpixel((0,0)) == (255, 255, 255):
    # then crop
    img_tmp_2_height, img_tmp_2_width = img_tmp_2.size # obtain new image height/width
    crop_box = (100, 100, img_tmp_2_width-100, img_tmp_2_height-50) # set box to crop
    img_1 = img_tmp_2.crop(crop_box) # polaroid style
    print("White border! Cropping")
else:
    # if not, just use original image
    img_1 = img
    print("Keeping the original image")

img_1.save("polaroid_" + img_name)

# Modify the image 2
hue = random.randint(0, 360)
color1 = ImageColor.getrgb("hsl(" + 
                                str(hue) + ", " + # hue
                                str(random.randint(25, 75)) + "%, " + # saturation
                                str(random.randint(15, 50)) + "%)") # lightness
color2 = ImageColor.getrgb("hsl(" + 
                                str((hue + 180) % 360) + ", " + # opposite hue
                                str(random.randint(25, 75)) + "%, " + # saturation
                                str(random.randint(50, 85)) + "%)") # lightness
img_2 = ImageOps.colorize(img, color1, color2)

img_2.save("colorized_" + img_name)

# Tweet
tweet_1 = rover['name'] + ' on ' + selected_photo['earth_date'] + '. '

closings = ["It was #amazing", 
            "It was #cold", 
            "I was so #lonely", 
            "I was #hungry", 
            "I miss my @NASA buddies",
            "Anybody here?",
            "Do you like it?",
            "#Selfie ?",
            "#Belfie ?",
            "Is this water?",
            "Where is Matt Damon?",
            "This is #Mars",
            "I could #terraform over there",
            "#Beautiful",
            "#Stunning",
            "#Magnificent",
            "#Cool",
            "I'm so #popular in Mars",
            "I work #remote",
            "In the middle of #nowhere",
            "#Telecommuting from #Mars"
           ]
if rover['name'] == "Curiosity":
    closings.append("Hey @MarsRovers, Wanna #hangout later?")
else:
    closings.append("Hey @MarsCuriosity, Wanna #hangout later?")

tweet_1 += random.choice(closings)

print(tweet_1)

# Tweeting
auth_1 = tweepy.OAuthHandler(credentials_1['consumer_key'], credentials_1['consumer_secret'])
auth_1.set_access_token(credentials_1['access_token'], credentials_1['access_token_secret'])

api_1 = tweepy.API(auth_1)
api_1.update_with_media("polaroid_" + img_name, status=tweet_1)

auth_2 = tweepy.OAuthHandler(credentials_2['consumer_key'], credentials_2['consumer_secret'])
auth_2.set_access_token(credentials_2['access_token'], credentials_2['access_token_secret'])

api_2 = tweepy.API(auth_2)
api_2.update_with_media("colorized_" + img_name)

# Remove images
os.unlink("polaroid_" + img_name)
os.unlink("colorized_" + img_name)