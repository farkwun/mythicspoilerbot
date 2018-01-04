import requests
import json
import settings
from spoiler import Spoiler
import sqlite3

url_base = 'http://mythicspoilerapi.dungeonmastering.net/'

conn = sqlite3.connect('../db/msbot_tables.db')

c = conn.cursor()

def getCardsBySet(setname):
	"""
	:type setname: String
	:rtype: List[Spoiler]
	"""
	url = url_base + 'APIv2/cards/by/set'
	payload = {'key': settings.API_KEY, 'param': setname}
	r = requests.get(url, params = payload)
	cards = json.loads(r.text[1:len(r.text)-1])['item']
	output = ''
	spoiler_list = []
	for card in cards:
		spoiler_list.append(Spoiler(card))
	return spoiler_list

def getLatestSpoilers():
	"""
	:rtype: List[string]
	"""
	url = url_base + 'APIv2/cards/by/spoils'
	payload = {'key': settings.API_KEY}
	r = requests.get(url, params = payload)
	cards = json.loads(r.text[1:len(r.text)-1])['item']
	output = ''
	url_list = []
	for card in cards:
		url_list.append(url_base + 'card_images/new_spoils/' + card['cardUrl'])
	return url_list

def getSpoilersTest(num):
	if num == 0:
		return [u'http://mythicspoilerapi.dungeonmastering.net/card_images/new_spoils/duskcharger.jpg', u'http://mythicspoilerapi.dungeonmastering.net/card_images/new_spoils/tendershootdryad.jpg', u'http://mythicspoilerapi.dungeonmastering.net/card_images/new_spoils/awakenedamalgamation.jpg', u'http://mythicspoilerapi.dungeonmastering.net/card_images/new_spoils/kumenatyrantoforazca.jpg', u'http://mythicspoilerapi.dungeonmastering.net/card_images/new_spoils/riverdarter.jpg']
	if num == 1:
		return [u'http://mythicspoilerapi.dungeonmastering.net/card_images/new_spoils/gleamingbarrier.jpg', u'http://mythicspoilerapi.dungeonmastering.net/card_images/new_spoils/duskcharger.jpg', u'http://mythicspoilerapi.dungeonmastering.net/card_images/new_spoils/tendershootdryad.jpg', u'http://mythicspoilerapi.dungeonmastering.net/card_images/new_spoils/awakenedamalgamation.jpg', u'http://mythicspoilerapi.dungeonmastering.net/card_images/new_spoils/kumenatyrantoforazca.jpg', u'http://mythicspoilerapi.dungeonmastering.net/card_images/new_spoils/riverdarter.jpg', u'http://mythicspoilerapi.dungeonmastering.net/card_images/new_spoils/thrashingbrontodon.jpg', u'http://mythicspoilerapi.dungeonmastering.net/card_images/new_spoils/atzocanseer.jpg', u'http://mythicspoilerapi.dungeonmastering.net/card_images/new_spoils/angraththeflamechained.jpg', u'http://mythicspoilerapi.dungeonmastering.net/card_images/new_spoils/pendelhaven.jpg', u'http://mythicspoilerapi.dungeonmastering.net/card_images/new_spoils/spellskite.jpg', u'http://mythicspoilerapi.dungeonmastering.net/card_images/new_spoils/despondentkillbot1.jpg']

images = getSpoilersTest(0)
print('0')
for image in images:
	c.execute('''
                SELECT img FROM spoilers WHERE img = ?
                ''', (image,))
        if len(c.fetchall()) == 0:
                print(image)
		c.execute('''
                        INSERT INTO spoilers VALUES(0, ?)
                        ''', (image,))
images = getSpoilersTest(1)
print('1')
for image in images:
	c.execute('''
                SELECT img FROM spoilers WHERE img = ?
                ''', (image,))
        if len(c.fetchall()) == 0:
                print(image)
                c.execute('''
                        INSERT INTO spoilers VALUES(0, ?)
                        ''', (image,))
c.execute('''
	SELECT img FROM spoilers
	''')
print(c.fetchall())
