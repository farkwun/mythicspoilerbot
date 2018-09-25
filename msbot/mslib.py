import json
import requests
import msbot.settings
from msbot.spoiler import Spoiler

url = 'https://api.scryfall.com/cards'

def getLatestSpoilers():
	"""
	:rtype: List[string]
	"""
	try:
		r = requests.get(url)
	except Exception as e:
		print('Scryfall Connection Error')
	else:
		try:
			spoilertext = r.text.replace(u"\u2014", "-").replace(u"\u0106", "C").replace(u"\u2022", "-")
			cards = json.loads(spoilertext)["data"]
			print(type(cards))
			print(type(cards[0]))
		except ValueError as e:
			print('JSON error')
			print(e)
			return []
		else:
			return cards
