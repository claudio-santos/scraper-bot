from bs4 import BeautifulSoup
import requests
import json
from discord import Embed

home_url = 'https://isthereanydeal.com/'
specials_url = 'https://isthereanydeal.com/specials/#/'
api_url = 'https://itad.docs.apiary.io/#'


def bundles_specials() -> Embed:
    req = requests.get(home_url)
    if req.status_code != 200:
        return Embed(description='Error: ' + req.status_code)

    soup = BeautifulSoup(req.text, 'html.parser')

    embed = Embed(
        title='Bundles and Special Deals',
        url=home_url
    )

    for head in soup.find_all('div', 'bundle-head'):
        time = head.find('div', 'bundle-time')
        _time = time.text

        details = head.find('a', 'bundle-tag')
        _details_url = home_url[:-1] + details['href']

        title = head.find('div', 'bundle-title')

        aux = title.find('a', 'lg')
        _title = aux.text
        _title_url = aux['href']

        shop = title.find('span', 'shopTitle')
        _shop = shop.text if shop else ''

        embed.add_field(
            name=_title,
            value='{}\n{} ({}) [details]({})'.format(_title_url, _time, _shop, _details_url)
        )

    return embed


# filter can be giveaway, other, bundle
# todo wait for all rows to load
def specials(filter_type) -> Embed:
    req = requests.get(specials_url)
    if req.status_code != 200:
        return Embed(description='Error: ' + req.status_code)

    soup = BeautifulSoup(req.text, 'html.parser')

    types = {
        'giveaway': 'Giveaways',
        'other': 'Others',
        'bundle': 'Bundles'
    }

    embed = Embed(
        title='Specials ' + types[filter_type],
        url=specials_url
    )

    for row in soup.find_all('div', 'bundle-row1'):
        details = row.find('a', 'bundle-tag')
        if details.text != filter_type:
            continue

        _details_url = home_url[:-1] + details['href']

        time = row.find('div', 'bundle-time')
        _time = time.text

        title = row.find('div', 'bundle-title')

        aux = title.find('a', 'lg')
        _title = aux.text
        _title_url = aux['href']

        embed.add_field(
            name=_title,
            value='{}\n{} [details]({})'.format(_title_url, _time, _details_url),
            inline=True
        )

    return embed


def search_game(api_key, game, region) -> Embed:
    req = requests.get('https://api.isthereanydeal.com/v02/game/plain/', params={
        'key': api_key, 'title': game
    })
    if req.status_code != 200:
        return Embed(description='Error: ' + req.status_code)

    j = json.loads(req.text)
    if not j['.meta']['active']:
        req = requests.get('https://api.isthereanydeal.com/v01/search/search/', params={
            'key': api_key,
            'q': game,
            'limit': 5,
            'region': region,
            'shops': 'battlenet,epic,gog,microsoft,origin,steam,uplay'
        })

        j = json.loads(req.text)['data']['list']
        if not j:
            return Embed(description='Error: Empty List')

        res = []
        for x in j:
            res.append('.itad {}\n'.format(x['title']))

        return Embed().add_field(name='Did you mean:', value=''.join(res))

    plain = j['data']['plain']

    req = requests.get('https://api.isthereanydeal.com/v01/game/info/', params={
        'key': api_key, 'plains': plain
    })
    j1 = json.loads(req.text)['data'][plain]

    req = requests.get(
        'https://api.isthereanydeal.com/v01/game/prices/', params={
            'key': api_key, 'plains': plain, 'region': region
        })
    j = json.loads(req.text)
    c = j['.meta']['currency']
    j2 = j['data'][plain]

    req = requests.get('https://api.isthereanydeal.com/v01/game/storelow/', params={
        'key': api_key, 'plains': plain, 'region': region
    })
    j3 = json.loads(req.text)['data'][plain]

    embed = Embed(
        title=j1['title'],
        url=j1['urls']['game']
    )

    embed.add_field(name='-', value='__Current Prices__', inline=False)

    for x in j2['list']:
        embed.add_field(
            name=x['shop']['name'],
            value='{:.2f} {} ({}% off)\n{}'.format(x['price_new'], c, x['price_cut'], x['url']),
            inline=True
        )

    embed.add_field(name='-', value='__Historical Low Prices__', inline=False)

    for x in j3:
        embed.add_field(
            name=x['shop'],
            value='{:.2f} {}'.format(x['price'], c),
            inline=True
        )

    return embed
