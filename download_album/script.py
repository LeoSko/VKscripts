import vk
import socket
import locale
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request
import os
import sys
from progressbar import ProgressBar, Percentage, SimpleProgress, Bar

HOST_NAME = ''
PORT_NUMBER = 80

from access_token import user_access_token

user_session = vk.Session(access_token=user_access_token)
uapi = vk.API(user_session, v='5.69')
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

# album uri example: https://vk.com/album12245505_190124834
if len(sys.argv) > 1:
	uri = sys.argv[1]
owner_id = uri.split('_')[0].split('album')[1]
album_id = uri.split('_')[1]

photos = uapi.photos.get(owner_id=owner_id, album_id=album_id, count=1000, photo_sizes=True)

pbar = ProgressBar(widgets=[
	Percentage(), 
	Bar(left='[', marker='=', right=']'),
	SimpleProgress()
	],
	maxval=int(photos['count']))

if not os.path.exists('res'):
    os.makedirs('res')	

max_n = 0
for dir_name in os.listdir('res'):
	if str(max_n) < dir_name:
		max_n = int(dir_name)
max_n = max_n + 1

if not os.path.exists('res/' + str(max_n)):
    os.makedirs('res/' + str(max_n))	

i = 1
for photo in photos['items']:
	url = photo['sizes'][-1]['src']
	urllib.request.urlretrieve(url, 'res/' + str(max_n) + '/' + os.path.basename(url))
	pbar.update(i)
	i = i + 1
	
print('\nСкачано в res/' + str(max_n))
