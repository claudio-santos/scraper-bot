import os
from dotenv import load_dotenv
from transmission_rpc import Client
from discord import Embed

load_dotenv()

HOST = os.getenv('TRANSMISSION_HOST')
PORT = int(os.getenv('TRANSMISSION_PORT'))
USER = os.getenv('TRANSMISSION_USER')
PASS = os.getenv('TRANSMISSION_PASS')


def add_torrent(url) -> Embed:
    c = Client(host=HOST, port=PORT, username=USER, password=PASS)
    t = c.add_torrent(url)

    return Embed(description=t.name)


def get_torrents() -> Embed:
    c = Client(host=HOST, port=PORT, username=USER, password=PASS)

    n = []
    for t in c.get_torrents():
        n.append('{}% | {}\n'.format(round(t.percentDone * 100), t.name))

    return Embed().add_field(name='Torrent List', value=''.join(n if n else 'None'))
