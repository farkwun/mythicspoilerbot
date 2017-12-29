import requests
import json
from spoiler import Spoiler



def getCardsBySet(setname):
       	"""
       	:type setname: String
       	:rtype: List[Spoiler]
       	"""
	url = 'http://mythicspoilerapi.dungeonmastering.net/APIv2/cards/by/set'
	payload = {'key': 'ZWdneml0QGdtYWlsLmNvbQ==', 'param': setname}
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
	url = 'http://mythicspoilerapi.dungeonmastering.net/APIv2/cards/by/spoils'
	payload = {'key': 'ZWdneml0QGdtYWlsLmNvbQ=='}
	r = requests.get(url, params = payload)
	cards = json.loads(r.text[1:len(r.text)-1])['item']
        output = ''
        url_list = []
        for card in cards:
                url_list.append('http://mythicspoilerapi.dungeonmastering.net/card_images/new_spoils/' + card['cardUrl'])
        return url_list

"""
output = ''
spoiler_list = getCardsBySet('Innistrad')
for spoil in spoiler_list:
	output += spoil.name + ', '
print(output)
output = ''
output_list = []
url_list = getLatestSpoilers()
for url in url_list:
	output += url + ','
print(output)
"""
