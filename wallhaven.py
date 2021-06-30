from bs4 import BeautifulSoup
import requests
from discord import Embed

home_url = 'https://wallhaven.cc/'
search_url = 'https://wallhaven.cc/search?{}categories=110&purity=100&sorting={}&order=desc'
img_url = 'https://w.wallhaven.cc/full/{}/wallhaven-{}'


def featured() -> [Embed]:
    req = requests.get(home_url)
    if req.status_code != 200:
        return [Embed(description='Error: %d' % req.status_code)]

    soup = BeautifulSoup(req.content, 'html.parser')
    res = []
    for finds in soup.find('div', 'feat-row').find_all('img'):
        img = gen_img_url(finds.get('src'))
        if requests.get(img).status_code == 404:
            img = img[:-3] + 'png'
        res.append(Embed(
            title=img,
            url=img
        ).set_image(
            url=img
        ))

    return res


def relevance(query) -> [Embed]:
    return search(query, 'relevance')


def random(query) -> [Embed]:
    return search(query, 'random')


def date_added(query) -> [Embed]:
    return search(query, 'date_added')


def views(query) -> [Embed]:
    return search(query, 'views')


def favorites(query) -> [Embed]:
    return search(query, 'favorites')


def toplist(query) -> [Embed]:
    return search(query, 'toplist')


def search(query, sorting) -> [Embed]:
    req = requests.get(gen_search_url(query, sorting))
    if req.status_code != 200:
        return [Embed(description='Error: ' + req.status_code)]

    soup = BeautifulSoup(req.content, 'html.parser')
    res = []
    for finds in soup.find_all('figure'):
        aux1 = finds.find('img').get('data-src')
        aux2 = finds.find('span', 'png')
        aux = aux1 if not aux2 else aux1[:-3] + 'png'
        img = gen_img_url(aux)
        res.append(Embed(
            title=img,
            url=img
        ).set_image(
            url=img
        ))

    return res


def gen_search_url(query, sorting):
    query = '' if not query else 'q=' + query.replace(' ', '%20') + '&'
    return search_url.format(query, sorting)


def gen_img_url(source):
    splits = source.rsplit('/', 2)
    return img_url.format(splits[1], splits[2])
