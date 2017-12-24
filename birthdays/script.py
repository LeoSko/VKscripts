import vk
from datetime import date, timedelta
import locale

from access_token import access_token, group_access_token
session = vk.Session(access_token=access_token)
group_session = vk.Session(access_token=group_access_token)
api = vk.API(session)
gapi = vk.API(group_session)
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

now = date.today()

startDay = now - timedelta(days=3)
endDay = now + timedelta(days=10)

users = api.groups.getMembers(group_id=75494873, fields="bdate")['users']

result_table = []

for user in users:
	if 'bdate' in user:
		bdate = date(day=int(user['bdate'].split('.')[0]), month=int(user['bdate'].split('.')[1]), year=now.year)
		if now.month == 12:
			if bdate.month != 12:
				bdate = bdate.replace(year=now.year + 1)
		if startDay <= bdate and bdate <= endDay:
			result_table.append(type('', (object,), {'date': bdate, 'id': user['uid'], 'name': '{0} {1}'.format(user['first_name'], user['last_name'])}))

result_table.sort(key=lambda x: x.date)

result_strings = []
for user in result_table:
	this_user_string = '{0}: {2}: vk.com/id{1}'.format(user.date.strftime('%d.%m'), str(user.id), user.name)
	if (user.date == now):
		this_user_string = '&#128293;' + this_user_string
	if (user.date == now + timedelta(days=1)):
		this_user_string = '&#127881;' + this_user_string
	result_strings.append(this_user_string)

result_message = 'Сегодня ' + now.strftime('%d.%m.%Y') + \
				'\nДни рождения с ' + startDay.strftime('%d.%m') + ' по ' + endDay.strftime('%d.%m') + \
				'\n' + '\n'.join(result_strings)

print(gapi.messages.send(user_ids='12245505,349758',message=result_message))
#print(result_message)
