from bs4 import BeautifulSoup
import requests

home_url = 'https://isthereanydeal.com/'


def bundles_specials():
    req = requests.get(home_url)
    if req.status_code != 200:
        return

    print(req.url)
    soup = BeautifulSoup(req.content, 'html.parser')

    dic = {
        'time': [],
        'details_url': [],
        'title': [],
        'title_url': [],
        'shop': [],
        'desc': []
    }

    for head in soup.find('div', 'cntBoxContent').find_all('div', 'bundle-head'):

        for time in head.find_all('div', 'bundle-time'):
            dic['time'].append(time.text)

        for details in head.find_all('a', 'more'):
            dic['details_url'].append(home_url[:-1] + details['href'])

        for title in head.find_all('div', 'bundle-title'):
            aux = title.find('a', 'lg')
            dic['title'].append(aux.text)
            dic['title_url'].append(aux['href'])
            aux = title.find('span', 'shopTitle')
            dic['shop'].append(aux.text if aux else '')

    return dic
