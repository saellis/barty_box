import json
import random
from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator


def get_random_bar_coords(lat, lon, radius):
    mpm = 1609.34  # meters per mile
    config = json.load(open('conf.json', 'rb'))

    auth = Oauth1Authenticator(
        consumer_key=config['yelp']['consumer_key'],
        consumer_secret=config['yelp']['consumer_secret'],
        token=config['yelp']['token'],
        token_secret=config['yelp']['token_secret']
    )
    client = Client(auth)

    param_offset = lambda x: {
        'term': 'bars, All',
        'lang': 'en',
        'sort': 2,  # 2: only the top rated in the area
        'radius_filter': int(radius * mpm),
        'offset': x
    }

    bus_list = []
    for offset in [0, 20]:
        response = client.search_by_coordinates(lat, lon, **param_offset(offset))
        bus_list.extend(response.businesses)

    bar = random.choice(bus_list)
    while bar.name in ["Peter's Pub", "Hemingway's Cafe"]:  # Can we just
        bar = random.choice(bus_list)
    return bar.location.coordinate.latitude, bar.location.coordinate.longitude
