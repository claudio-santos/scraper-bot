import requests
import json

home_url = 'https://www.nasa.gov/'
api_url = 'https://api.nasa.gov/'


def get_apod(api_key, date):
    date = '' if not date else '&date={}'.format(date)
    req = requests.get('https://api.nasa.gov/planetary/apod?api_key={}{}'.format(api_key, date))
    if req.status_code != 200:
        return

    return json.loads(req.text)
