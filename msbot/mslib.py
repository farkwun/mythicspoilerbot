import requests
import json
import settings
from spoiler import Spoiler
import sqlite3

url_base = 'http://mythicspoilerapi.dungeonmastering.net/'

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

