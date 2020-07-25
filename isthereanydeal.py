from bs4 import BeautifulSoup
import requests
import sqlite3

home_url = 'https://isthereanydeal.com/'
specials_url = 'https://isthereanydeal.com/specials/#/'
notification = 'isthereanydeal'


def bundles_specials():
    req = requests.get(home_url)
    if req.status_code != 200:
        return

    print(req.url)
    soup = BeautifulSoup(req.text, 'html.parser')

    dic = {
        'title': [],
        'title_url': [],
        'details_url': [],
        'shop': [],
        'time': []
    }

    for head in soup.find_all('div', 'bundle-head'):
        time = head.find('div', 'bundle-time')
        dic['time'].append(time.text)

        details = head.find('a', 'bundle-tag')
        dic['details_url'].append(home_url[:-1] + details['href'])

        title = head.find('div', 'bundle-title')

        aux = title.find('a', 'lg')
        dic['title'].append(aux.text)
        dic['title_url'].append(aux['href'])

        shop = title.find('span', 'shopTitle')
        dic['shop'].append(shop.text if shop else '')

    return __dic_to_lis__(dic)


# filter can be giveaway, other, bundle
# todo wait for all rows to load
def specials(filter_type):
    req = requests.get(specials_url)
    if req.status_code != 200:
        return

    print(req.url)
    soup = BeautifulSoup(req.text, 'html.parser')

    dic = {
        'title': [],
        'title_url': [],
        'details_url': [],
        'shop': [],
        'time': []
    }

    for row in soup.find_all('div', 'bundle-row1'):
        details = row.find('a', 'bundle-tag')
        if details.text != filter_type:
            continue

        dic['details_url'].append(home_url[:-1] + details['href'])

        time = row.find('div', 'bundle-time')
        dic['time'].append(time.text)

        title = row.find('div', 'bundle-title')

        aux = title.find('a', 'lg')
        dic['title'].append(aux.text)
        dic['title_url'].append(aux['href'])

        dic['shop'].append('')

    return __dic_to_lis__(dic)


def check_new_bundles_specials_db(database):
    res = []

    lis = bundles_specials()

    try:
        conn = sqlite3.connect(database)
        c = conn.cursor()

        old = 0
        for li in lis:
            c.execute(
                'INSERT OR IGNORE INTO isthereanydeal '
                '( title '
                ', title_url '
                ', details_url '
                ', shop '
                ', time '
                ') VALUES (?, ?, ?, ?, ?) '
                , li
            )
            new = c.lastrowid
            if new != old:
                old = new
                res += (li,)
        conn.commit()

        c.close()
        conn.close()
    except:
        print('Exception in check_new_bundles_specials_db')

    return res


# todo
def select_notification_channel(database, server):
    conn = sqlite3.connect(database)
    c = conn.cursor()

    rows = c.execute('SELECT * FROM notifications').fetchall()

    c.close()
    conn.close()

    return rows


# todo
def insert_notification_channel(database, channel, server):
    conn = sqlite3.connect(database)
    c = conn.cursor()

    c.execute(
        'INSERT OR IGNORE INTO notifications '
        '( channel '
        ', server '
        ', type '
        ') VALUES (?, ?, ?) '
        , channel, server, notification
    )
    conn.commit()

    c.close()
    conn.close()


# todo
def delete_notification_channel_db(database, channel, server):
    conn = sqlite3.connect(database)
    c = conn.cursor()

    c.execute(
        'DELETE FROM notifications '
        'WHERE channel = ? '
        'AND server = ? '
        'AND type = ? '
        , channel, server, notification
    )
    conn.commit()

    c.close()
    conn.close()


def __dic_to_lis__(dic):
    lis = []
    for i in range(len(dic['title'])):
        lis += ((
                    dic['title'][i],
                    dic['title_url'][i],
                    dic['details_url'][i],
                    dic['shop'][i],
                    dic['time'][i]
                ),)
    return lis
