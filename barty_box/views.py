import json
import random
import requests
# from .models import Greeting
from yelp.client import Client
from django.shortcuts import render
from django.http import HttpResponse
from yelp.oauth1_authenticator import Oauth1Authenticator


def index(request):
    return render(request, 'index.html')


def _get_bar_coords(lat, lon, radius):
    mpm = 1609.34  # meters per mile
    config = json.load(open('../conf.json', 'rb'))

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

def _call_uber(dest_lat, dest_lon):
    base_url = 'https://sandbox-api.uber.com/v1'
    requests.post()

def ride(request):
    """ Finds a bar within a certain radius of the user, and calls an uber from user's location to bar location.
        Eventually return something like.. time to arrival? type of car? etc.
    """
    latitude = request.get('latitude', 40.4443533)  # defaults to somewhere near pittsburgh
    longitude = request.get('longitude', -79.96083499999997)
    radius = request.get('radius', 3)  # default to a 3 mile search radius
    bar_lat, bar_lon = _get_bar_coords(latitude, longitude, radius)
    resp = _call_uber(bar_lat, bar_lon)
    # parse response here

    # return HttpResponse(json.dumps(result), content_type='application/json')  # return response


if __name__ == '__main__':
    print ride({
        'latitude': 40.4443533,
        'longitude': -79.96083499999997,
        'radius': 5
    })
