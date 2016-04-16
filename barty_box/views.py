import json
from django.shortcuts import render
from django.http import HttpResponse
from uber_rides.client import UberRidesClient
from uber_utils import get_auth_flow, get_product_id, get_auth_url, request_ride, get_ride_details
from yelp_utils import get_random_bar_coords
try:
    from urllib.parse import parse_qs
    from urllib.parse import urlparse
except ImportError:
    from urlparse import parse_qs
    from urlparse import urlparse

from .models import Greeting

auth_flow = None  # i hate myself
session = None  # i hate myself
req_info = {}
result = None

def index(request):
    return render(request, 'index.html')


def auth_url(request):
    config = json.load(open('conf.json', 'rb'))
    global auth_flow  # i hate myself
    auth_flow = get_auth_flow(config)
    url = get_auth_url(auth_flow)
    return HttpResponse(json.dumps({'auth_url': url}), content_type='application/json')


def get_ride_update(request):
    url = request.get_raw_uri()
    querystring = urlparse(url).query
    params = parse_qs(querystring)
    global session  # i hate myself
    # client = UberRidesClient(session, sandbox_mode=True)
    client = UberRidesClient(session)
    result = get_ride_details(client, params.get('ride_id')[0])
    return HttpResponse(json.dumps(result), content_type='application/json')


def get_ride_request(request):
    global result
    return HttpResponse(json.dumps(result), content_type='application/json')


def surge_accept(request):
    url = request.get_raw_uri()
    querystring = urlparse(url).query
    params = parse_qs(querystring)
    global req_info
    global session  # i hate myself

    # client = UberRidesClient(session, sandbox_mode=True)
    client = UberRidesClient(session)
    global result
    result = request_ride(client, req_info['pid'], req_info['st_lat'], req_info['st_lon'],
                          req_info['dest_lat'], req_info['dest_lon'], params.get('surge_confirmation_id')[0])

    return render(request, 'wait.html')


def caller(request):
    url = request.get_raw_uri()
    querystring = urlparse(url).query
    params = parse_qs(querystring)


    st_lat = params.get('latitude')[0]
    st_lon = params.get('longitude')[0]
    authorized_url = params.get('url')[0]
    radius = int(params.get('radius')[0])
    product = params.get('product')[0]
    config = json.load(open('conf.json', 'rb'))
    # auth_flow = get_auth_flow(config)
    global auth_flow  # i hate myself
    pid = get_product_id(config, st_lat, st_lon, product)
    global session  # i hate myself
    session = auth_flow.get_session(authorized_url)
    credential = session.oauth2credential
    credential_data = {
        'client_id': credential.client_id,
        'redirect_url': credential.redirect_url,
        'access_token': credential.access_token,
        'expires_in_seconds': credential.expires_in_seconds,
        'scopes': list(credential.scopes),
        'grant_type': credential.grant_type,
        'client_secret': credential.client_secret,
        'refresh_token': credential.refresh_token,
    }
    # client = UberRidesClient(session, sandbox_mode=True)
    client = UberRidesClient(session)
    dest_lat, dest_lon = get_random_bar_coords(st_lat, st_lon, radius)

    # update_surge(client, pid, 1.0)  ### try out surge pricing
    result = request_ride(client, pid, st_lat, st_lon, dest_lat, dest_lon)
    global req_info
    req_info['st_lat'] = st_lat
    req_info['st_lon'] = st_lon
    req_info['pid'] = pid
    req_info['dest_lat'] = dest_lat
    req_info['dest_lon'] = dest_lon
    return HttpResponse(json.dumps(result), content_type='application/json')


def wait(request):
    return render(request, 'wait.html')


def ride_finder(request):
    return render(None, 'ride_finder.html')