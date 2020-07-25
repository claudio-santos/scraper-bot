from bs4 import BeautifulSoup
import requests

home_url = 'https://howlongtobeat.com/'
search_url = 'https://howlongtobeat.com/search_results.php'


def search_game(game):
    req = requests.post(search_url, data={
        'queryString': game,
        't': 'games',
        'sorthead': 'popular',
        'sortd': 'Normal Order',
        'plat': '',
        'length_type': 'main',
        'length_min': '',
        'length_max': '',
        'detail': '0'
    })
    if req.status_code != 200:
        return

    print(req.url)
    soup = BeautifulSoup(req.text, 'html.parser').find('li', 'back_darkish')

    img_url = soup.find('img')['src']

    aux = soup.find('h3', 'shadow_text').find('a')
    url = '{}{}'.format(home_url, aux['href'])
    title = aux.text

    labels = []
    for text in soup.find_all('div', 'shadow_text'):
        labels.append(text.text)

    times = []
    for time in soup.find_all('div', 'time_100'):
        times.append(time.text)

    return {
        'img_url': img_url,
        'title': title,
        'url': url,
        'labels': labels,
        'times': times
    }

print(search_game('metal gear'))
