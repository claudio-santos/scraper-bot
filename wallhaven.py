from bs4 import BeautifulSoup
import requests

url = 'https://wallhaven.cc/'
img = 'https://w.wallhaven.cc/full/%s/wallhaven-%s'

def featured():
    req = requests.get(url)
    if req.status_code != 200:
        print('Error: ' + req.status_code)
        return

    soup = BeautifulSoup(req.content, 'html.parser')
    res = []
    for finds in soup.find('div', 'feat-row').find_all('img'):
        splits = finds.get('src').rsplit('/', 2)
        res += [img % (splits[1], splits[2])]

    return res

#print(featured())