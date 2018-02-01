import vk
import socket
from datetime import date, datetime, timedelta
import locale
from string import punctuation
import random
from difflib import SequenceMatcher
import time
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

HOST_NAME = ''
PORT_NUMBER = 80
group_with_cats = -46090184

from access_token import group_access_token, user_access_token
group_session = vk.Session(access_token=group_access_token)
gapi = vk.API(group_session, v='5.69')
user_session = vk.Session(access_token=user_access_token)
uapi = vk.API(user_session, v='5.69')
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

start_time = datetime.now()
users = set()

messages_this_session = 0

def get_random_cat_attachment():
	random_wall_number = random.randint(0, 1578 - 5)
	walls = uapi.wall.get(owner_id=group_with_cats, filter='owner', count=5, offset=random_wall_number)
	for wall in walls['items']:
		if 'attachments' in wall:
			attach = wall['attachments'][0]
			doc_type = attach['type']
			key = attach[doc_type]['access_key']
			doc_owner = attach[doc_type]['owner_id']
			doc_id = attach[doc_type]['id']
			doc_data = uapi.docs.getById(docs='{0}_{1}'.format(doc_owner, doc_id))
			if len(doc_data) < 1:
				continue
			attach_text = ''
			if key is not None:
				attach_text = '{0}{1}_{2}_{3}'.format(doc_type, doc_owner, doc_id, key)
			else:
				attach_text = '{0}{1}_{2}'.format(doc_type, doc_owner, doc_id)
			print('Send {0} from {1}'.format(attach_text, 'http://vk.com/wall{0}_{1}'.format(wall['owner_id'], wall['id'])))
			return [wall['text'], attach_text]
	print('Nothing found in {0}'.format(walls))

def get_statistics():
	return '''Я работаю без перезапуска уже {0}, за это время ответил {1} разным пользователям и в сумме отправил {2} гиф, но это не предел! :)'''.format(str(datetime.now() - start_time).replace('days', 'дней'), len(users), messages_this_session)

def get_help():
	return '''Напиши мне сообщение о том, что ты хочешь получить гифку, например:
Хочу гифку!
...
Ещё хочу!
...
Больше гифок!

Можешь также спросить у меня как дела, тогда получишь немного статистики. ;)'''

def calc_dist(msg, strings, ratio):
	for string in strings:
		for word in msg.split(' '):
			if SequenceMatcher(None, word.lower().translate(punctuation), string.lower()).ratio() > ratio:
				return True
	return False

class CatobotMessageHandler(BaseHTTPRequestHandler):
	def _set_headers(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()

	def do_POST(self):
		self._set_headers()
		content_length = int(self.headers['Content-Length'])
		post_data = self.rfile.read(content_length)
		request = json.loads(post_data)
		if request['type'] == 'message_new':
			gapi.messages.markAsRead(peer_id=request['object']['user_id'])
			print('Got message with id {0} from {1}: {2}'.format(request['object']['id'], request['object']['user_id'], request['object']['body']))
			message = request['object']['body']
			result_message = "Не могу понять о чём ты."
			result_attach = ""
			user_id = request['object']['user_id']
			users.add(user_id)

			global messages_this_session
			if calc_dist(message, ["гифку", "гиф", "котика", "кота", "кису", "милое", "хочу", "пришли", "ещё", "больше", "ага", "конечно", "разумеется", "да", "давай"], 0.6):
				[result_message, result_attach] = get_random_cat_attachment()
				messages_this_session += 1
			elif calc_dist(message, ["Привет", "здарова", "хай", "хаюшки", "здравствуй", "дарова", ], 0.6):
				result_message = "Привет! Как дела? Хочешь гифку с котиком?"
			elif calc_dist(message, ["как", "дела", "статистика", "жизнь", "поживаешь"], 0.6):
				result_message = get_statistics()
			else:
				result_message = get_help()
			gapi.messages.send(user_id=user_id, message=result_message, attachment=result_attach)
		self.wfile.write("ok".encode())
		#s.wfile.write("7f8c6697".encode())


httpd = HTTPServer((HOST_NAME, PORT_NUMBER), CatobotMessageHandler)
print("{2} Server Starts - {0}:{1}".format(HOST_NAME, PORT_NUMBER, start_time))
try:
	httpd.serve_forever()
except KeyboardInterrupt:
	pass
httpd.server_close()
print("{2} Server Stops - {0}:{1}".format(HOST_NAME, PORT_NUMBER, time.asctime()))
