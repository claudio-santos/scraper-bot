import requests
import json
from discord import Embed

home_url = 'https://www.nasa.gov/'
api_url = 'https://api.nasa.gov/'


def get_apod(api_key, date) -> Embed:
    date = '' if not date else '&date=' + date
    req = requests.get('https://api.nasa.gov/planetary/apod?api_key=' + api_key + date)
    if req.status_code != 200:
        return Embed(description='Error: %d' % req.status_code)

    j = json.loads(req.text)

    return Embed(
        title=j['title'],
        description=j['explanation'],
        url=j['url']
    ).set_image(
        url=j['hdurl']
    ).set_footer(
        text='{} | {}'.format(j['date'], j['copyright'])
    )
