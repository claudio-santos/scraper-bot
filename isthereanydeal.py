from bs4 import BeautifulSoup
import requests
import json

home_url = 'https://isthereanydeal.com/'
specials_url = 'https://isthereanydeal.com/specials/#/'
api_url = 'https://itad.docs.apiary.io/#'


def bundles_specials():
    req = requests.get(home_url)
    if req.status_code != 200:
        return

    print(req.url)
    soup = BeautifulSoup(req.text, 'html.parser')

    dic = {
        'title': [],
        'title_url': [],
        'details_url': [],
        'shop': [],
        'time': []
    }

    for head in soup.find_all('div', 'bundle-head'):
        time = head.find('div', 'bundle-time')
        dic['time'].append(time.text)

        details = head.find('a', 'bundle-tag')
        dic['details_url'].append(home_url[:-1] + details['href'])

        title = head.find('div', 'bundle-title')

        aux = title.find('a', 'lg')
        dic['title'].append(aux.text)
        dic['title_url'].append(aux['href'])

        shop = title.find('span', 'shopTitle')
        dic['shop'].append(shop.text if shop else '')

    return __dic_to_lis__(dic)


# filter can be giveaway, other, bundle
# todo wait for all rows to load
def specials(filter_type):
    req = requests.get(specials_url)
    if req.status_code != 200:
        return

    print(req.url)
    soup = BeautifulSoup(req.text, 'html.parser')

    dic = {
        'title': [],
        'title_url': [],
        'details_url': [],
        'shop': [],
        'time': []
    }

    for row in soup.find_all('div', 'bundle-row1'):
        details = row.find('a', 'bundle-tag')
        if details.text != filter_type:
            continue

        dic['details_url'].append(home_url[:-1] + details['href'])

        time = row.find('div', 'bundle-time')
        dic['time'].append(time.text)

        title = row.find('div', 'bundle-title')

        aux = title.find('a', 'lg')
        dic['title'].append(aux.text)
        dic['title_url'].append(aux['href'])

        dic['shop'].append('')

    return __dic_to_lis__(dic)


def search_game(api_key, game, region):
    req = requests.get('https://api.isthereanydeal.com/v02/game/plain/?key={}&title={}'.format(api_key, game))
    if req.status_code != 200:
        return

    j = json.loads(req.text)
    if not j['.meta']['active']:
        req_url = [
            'https://api.isthereanydeal.com/v01/search/search/',
            '?key={}'.format(api_key),
            '&q={}'.format(game),
            '&limit=5',
            '&region=eu2',
            '&shops=battlenet%2Cepic%2Cgog%2Cmicrosoft%2Corigin%2Csteam%2Cuplay'
        ]
        req_url = ''.join(req_url)
        req = requests.get(req_url)
        return json.loads(req.text)['data']['list']

    plain = j['data']['plain']

    req = requests.get('https://api.isthereanydeal.com/v01/game/info/?key={}&plains={}'.format(api_key, plain))
    j1 = json.loads(req.text)['data'][plain]

    req = requests.get(
        'https://api.isthereanydeal.com/v01/game/prices/?key={}&plains={}&region={}'.format(api_key, plain, region))
    j = json.loads(req.text)
    c = j['.meta']['currency']
    j2 = j['data'][plain]

    req = requests.get(
        'https://api.isthereanydeal.com/v01/game/storelow/?key={}&plains={}&region={}'.format(api_key, plain, region))
    j3 = json.loads(req.text)['data'][plain]

    return {
        'title': j1['title'],
        'is_dlc': j1['is_dlc'],
        'achievements': j1['achievements'],
        'trading_cards': j1['trading_cards'],
        'url_game': j1['urls']['game'],
        'currency': c,
        'prices_list': j2['list'],
        'storelow_list': j3
    }


def __dic_to_lis__(dic):
    lis = []
    for i in range(len(dic['title'])):
        lis += ((
                    dic['title'][i],
                    dic['title_url'][i],
                    dic['details_url'][i],
                    dic['shop'][i],
                    dic['time'][i]
                ),)
    return lis
