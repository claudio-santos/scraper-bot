from bs4 import BeautifulSoup
import requests
from discord import Embed

home_url = 'https://howlongtobeat.com/'
search_url = 'https://howlongtobeat.com/search_results.php'


def search_game(game) -> Embed:
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
        return Embed(description='Error: ' + req.status_code)

    soup = BeautifulSoup(req.text, 'html.parser').find('li', 'back_darkish')
    if not soup:
        return Embed(description='Error: Empty Soup')

    _img_url = soup.find('img')['src']

    aux = soup.find('h3', 'shadow_text').find('a')
    _url = home_url + aux['href']
    _title = aux.text

    labels = []
    for text in soup.find_all('div', 'shadow_text'):
        labels.append(text.text)

    times = []
    for time in soup.find_all('div', 'time_100'):
        times.append(time.text)

    embed = Embed(
        title=_title,
        url=_url
    ).set_thumbnail(
        url=_img_url
    )

    for i in range(len(labels)):
        embed.add_field(
            name=labels[i],
            value=times[i] if len(times) > i else '-',
            inline=True
        )

    return embed
