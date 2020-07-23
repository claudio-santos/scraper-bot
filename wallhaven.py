from bs4 import BeautifulSoup
import requests

home_url = 'https://wallhaven.cc/'
search_url = 'https://wallhaven.cc/search?{}categories=110&purity=100&sorting={}&order=desc'
img_url = 'https://w.wallhaven.cc/full/{}/wallhaven-{}'


def featured():
    req = requests.get(home_url)
    if req.status_code != 200:
        return

    print(req.url)
    soup = BeautifulSoup(req.content, 'html.parser')
    res = []
    for finds in soup.find('div', 'feat-row').find_all('img'):
        res += gen_img_url(finds.get('src'))

    return res


def relevance(query):
    return search(query, 'relevance')


def random(query):
    return search(query, 'random')


def date_added(query):
    return search(query, 'date_added')


def views(query):
    return search(query, 'views')


def favorites(query):
    return search(query, 'favorites')


def toplist(query):
    return search(query, 'toplist')


def search(query, sorting):
    req = requests.get(gen_search_url(query, sorting))
    if req.status_code != 200:
        return

    print(req.url)
    soup = BeautifulSoup(req.content, 'html.parser')
    res = []
    for finds in soup.find_all('figure'):
        aux1 = finds.find('img').get('data-src')
        aux2 = finds.find('span', 'png')
        aux = aux1 if not aux2 else aux1[:-3] + 'png'
        res += gen_img_url(aux)

    return res


def gen_search_url(query, sorting):
    query = '' if not query else 'q=' + query.replace(' ', '%20') + '&'
    return search_url.format(query, sorting)


def gen_img_url(source):
    splits = source.rsplit('/', 2)
    return [img_url.format(splits[1], splits[2])]
