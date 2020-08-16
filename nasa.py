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

    title = j['title']
    explanation = j['explanation'].replace('||', '|')
    url = j['url']
    date = j['date']
    cr = j['copyright'] if 'copyright' in j else ''

    hdurl = None
    if j['media_type'] == 'image':
        hdurl = j['hdurl']
    else:
        explanation = '\n'.join([explanation, url])

    embed = Embed(
        title=title,
        description=explanation,
        url=url
    ).set_footer(
        text='{} | {}'.format(date, cr)
    )

    if hdurl:
        embed.set_image(url=j['hdurl'])

    return embed
