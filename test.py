__author__ = 'samson'

import ff.fanfiction as fan

url = 'https://www.fanfiction.net/s/10541297/1/Harry-Potter-and-the-Riders-of-the-Apocalypse'

rota_user = fan.User(id=801855)

gen = rota_user.get_favourite_authors()
for g in gen:
    print g.username