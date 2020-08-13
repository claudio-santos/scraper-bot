from bs4 import BeautifulSoup
import requests
from discord import Embed

home_url = 'https://gg.deals/'
search_url = 'https://gg.deals/news/?availability=1&type=6'


def best_deals() -> Embed:
    req = requests.get(home_url)
    if req.status_code != 200:
        return Embed(description='Error: %d' % req.status_code)

    print(req.url)

    embed = Embed(
        title='Best Deals',
        url=home_url
    )

    soup = BeautifulSoup(req.text, 'html.parser')
    for col in soup.find_all('div', 'col-md-4'):
        preset = col.find('a', 'preset-title-link')
        if preset:
            if preset.text == 'Best deals':
                titles = []
                urls = []
                for title in col.find_all('a', 'ellipsis title'):
                    titles.append(title.text)
                    urls.append(home_url[:-1] + title['href'])

                times = []
                for time in col.find_all('time', 'timeago-short'):
                    times.append(time.text)

                shops = []
                for shop in col.find_all('div', 'tag-shop ellipsis tag with-bull'):
                    shops.append(shop.find('span').text)

                prices = []
                for price in col.find_all('span', 'price'):
                    prices.append(price.find('span').text)

                for i in range(len(titles)):
                    embed.add_field(
                        name='{} - {}'.format(titles[i], prices[i]),
                        value='{}\n{} ({})'.format(urls[i], times[i], shops[i])
                    )

    return embed


def search_freebies() -> [Embed]:
    req = requests.get(search_url)
    if req.status_code != 200:
        return Embed(description='Error: %d' % req.status_code)

    print(req.url)

    embed = Embed(
        title='Freebies',
        url=search_url
    )

    soup = BeautifulSoup(req.text, 'html.parser')
    for news in soup.find('div', 'grid-list news-list').find_all('div', 'small news-tile hoverable active'):
        title = news.find('h2', 'ellipsis title-header')

        embed.add_field(
            name=title.a.text,
            value='[details]({})'.format(home_url[:-1] + title.a['href']),
            inline=True
        )

    return embed
