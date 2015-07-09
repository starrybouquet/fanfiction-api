__author__ = 'samson'

import ff.fanfiction as fan

url = 'https://www.fanfiction.net/s/10541297/1/Harry-Potter-and-the-Riders-of-the-Apocalypse'

rota = fan.Story(url)
rota_chapters = rota.get_chapters()

print rota.number_chapters

for chapter in rota_chapters:
    print chapter.title
