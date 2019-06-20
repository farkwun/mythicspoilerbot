import json
import requests
import msbot.settings
import msbot.utils
from msbot.spoiler import Spoiler

url_base = 'http://mythicspoilerapi.dungeonmastering.net/'


def getCardsBySet(setname):
    """
    :type setname: String
    :rtype: List[Spoiler]
    """
    url = url_base + 'APIv2/cards/by/set'
    payload = {'key': msbot.settings.API_KEY, 'param': setname}
    r = requests.get(url, params=payload)
    cards = json.loads(r.text[1:len(r.text) - 1])['item']
    spoiler_list = []
    for card in cards:
        spoiler_list.append(Spoiler(card))
    return spoiler_list


def getLatestSpoilers():
    """
    :rtype: List[string]
    """
    url = url_base + 'APIv2/cards/by/spoils'
    payload = {'key': msbot.settings.API_KEY}
    try:
        r = requests.get(url, params=payload)
    except Exception as e:
        print('MythicSpoiler Connection Error')
    else:
        try:
            cards = json.loads(r.text[1:len(r.text) - 1])['item']
            print("Received {num_cards} spoilers".format(num_cards=len(cards)))
        except ValueError:
            print('JSON error')
            return []
        else:
            url_list = []
            for card in cards:
                img_url = url_base + \
                    'card_images/new_spoils/' + card['cardUrl']
                if msbot.utils.is_url_image(img_url):
                    url_list.append(img_url)
            return url_list
