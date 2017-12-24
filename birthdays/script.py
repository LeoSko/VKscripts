import vk
from datetime import date, datetime, timedelta
import locale

from access_token import access_token, group_access_token
session = vk.Session(access_token=access_token)
group_session = vk.Session(access_token=group_access_token)
api = vk.API(session, v='5.69')
gapi = vk.API(group_session)
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

now = date.today()

startDay = now - timedelta(days=3)
endDay = now + timedelta(days=10)

users = api.groups.getMembers(group_id=75494873, fields="bdate")['items']

result_table = []
has_birthday_today = False

for user in users:
	if 'bdate' in user:
		bdate = date(day=int(user['bdate'].split('.')[0]), month=int(user['bdate'].split('.')[1]), year=now.year)
		if now.month == 12:
			if bdate.month != 12:
				bdate = bdate.replace(year=now.year + 1)
		if startDay <= bdate and bdate <= endDay:
			result_table.append(type('', (object,), {'date': bdate, 'id': user['id'], 'name': '{0} {1}'.format(user['first_name'], user['last_name'])}))

result_table.sort(key=lambda x: x.date)

result_strings = []
attachments = []
for user in result_table:
	this_user_string = '{0}: {2}: vk.com/id{1}'.format(user.date.strftime('%d.%m'), str(user.id), user.name)
	if (user.date == now):
		has_birthday_today = True
		this_user_string = '&#128293;' + this_user_string
		# Lets find good photos for this user
		photos = []
		tphotos = []
		all_photos = api.photos.getAll(owner_id=user.id, count=200, extended=True)['items']
		tagged_photos = api.photos.getUserPhotos(user_id=user.id, count=200, extended=True, sort=0)['items']
		all_photos.extend(tagged_photos)
		for photo in all_photos:
			photo_datetime = datetime.fromtimestamp(photo['date'])
			photo_date = date(day=photo_datetime.day, month=photo_datetime.month, year=photo_datetime.year)
			if photo_date > user.date - timedelta(days=90):
				photos.append(photo)
		for photo in tagged_photos:
			photo_datetime = datetime.fromtimestamp(photo['date'])
			photo_date = date(day=photo_datetime.day, month=photo_datetime.month, year=photo_datetime.year)
			if photo_date > user.date - timedelta(days=90):
				tphotos.append(photo)
		photos.sort(key=lambda x: x['likes']['count'], reverse=True)
		tphotos.sort(key=lambda x: x['likes']['count'], reverse=True)
		for photo_index in range(min(2, len(photos))):
			attachments.append('photo{0}_{1}'.format(photos[photo_index]['owner_id'], photos[photo_index]['id']))
		for photo_index in range(min(2, len(tphotos))):
			attachments.append('photo{0}_{1}'.format(tphotos[photo_index]['owner_id'], tphotos[photo_index]['id']))

	if (user.date == now + timedelta(days=1)):
		this_user_string = '&#127881;' + this_user_string
	result_strings.append(this_user_string)

result_message = 'Сегодня ' + now.strftime('%d.%m.%Y') + \
				'\nДни рождения с ' + startDay.strftime('%d.%m') + ' по ' + endDay.strftime('%d.%m') + \
				'\n' + '\n'.join(result_strings)

result_attachments = ','.join(attachments)
print(gapi.messages.send(user_ids='12245505,349758', message=result_message, attachment=result_attachments))
#print(result_message)
#print(result_attachments)
