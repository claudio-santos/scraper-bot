import requests
import json

home_url = 'https://www.nasa.gov/'
apod_url = 'https://apod.nasa.gov/apod/astropix.html'


def get_apod(api_key, date):
    date = '' if not date else '&date={}'.format(date)
    req = requests.get('https://api.nasa.gov/planetary/apod?api_key={}{}'.format(api_key, date))
    if req.status_code != 200:
        return

    print(req.url)

    return json.loads(req.text)
