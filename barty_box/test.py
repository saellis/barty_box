import json
from uber_rides.client import UberRidesClient
from uber_rides.auth import AuthorizationCodeGrant
from uber_rides.session import Session
from uber_rides.client import SurgeError
try:
    from urllib.parse import parse_qs
    from urllib.parse import urlparse
except ImportError:
    from urlparse import parse_qs
    from urlparse import urlparse


def get_auth_flow(config):
    redirect_url = 'https://bartybox.herokuapp.com/'
    return AuthorizationCodeGrant(
        config['uber']['client_id'],
        ['request'],  # permission scopes (Allow App 'Barty Box' access to your...?)
        config['uber']['client_secret'],
        redirect_url,  # redirect URL must match that on our Uber API account
        # As the name implies, it takes the user to this URL after they are authenticated by Uber
    )


def get_product_id(config, lat, lon, product):
    """
    :return: the product ID of the uberX/XL for requesting a ride
    """
    session = Session(server_token=config['uber']['server_token'])  # FOR READ ONLY CALLS
    client = UberRidesClient(session)
    response = client.get_products(lat, lon)
    try:
        return filter(lambda x: x['display_name'] == product, response.json.get('products'))[0]['product_id']
    except Exception, e:
        raise ValueError('No Ubers of that type available')


def get_auth_url(auth_flow):
    """
    The user must be directed to this URL and has to accept terms, etc. before we can call them a ride
    :return: the URL for the user to go to
    """
    return auth_flow.get_authorization_url()


def request_ride(client, pid, slat, slon, dlat, dlon, surge_conf=None):
    try:
        return client.request_ride(
            product_id=pid,
            start_latitude=slat,
            start_longitude=slon,
            end_latitude=dlat,
            end_longitude=dlon,
            surge_confirmation_id=surge_conf
        ).json
    except SurgeError as e:
        url = e.surge_confirmation_href
        print 'go to {} and accept surge price.'.format(url)
        accept_url = raw_input('Paste the URL you are redirected to here:\n').strip()
        querystring = urlparse(accept_url).query
        query_params = parse_qs(querystring)
        surge_id = query_params.get('surge_confirmation_id')[0]
        return request_ride(client, pid, slat, slon, dlat, dlon, surge_conf=surge_id)


def update_surge(client, pid, multiplier):
    """Not real, just for sandboxing"""
    return client.update_sandbox_product(
        pid,
        surge_multiplier=multiplier
    ).status_code


def update_ride(client, status, ride_id):
    """Not real, just for sandboxing"""
    print status
    print ride_id
    client.update_sandbox_product(ride_id, status)


def get_ride_details(client, ride_id):
    return client.get_ride_details(ride_id).json


def main():
    st_lat, st_lon = 40.4443533, -79.96083499999997
    dest_lat, dest_lon = 40.4514452209, -79.9337325513
    config = json.load(open('../conf.json', 'rb'))
    auth_flow = get_auth_flow(config)
    pid = get_product_id(config, st_lat, st_lon, 'uberX')
    url = get_auth_url(auth_flow)

    print 'go to {} and authorize.'.format(url)
    authorized_url = raw_input('Paste the URL you are redirected to here:\n').strip()

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
    client = UberRidesClient(session, sandbox_mode=True)  # change this eventually
    # update_surge(client, pid, 1.5)  ### try out surge pricing
    result = request_ride(client, pid, st_lat, st_lon, dest_lat, dest_lon)
    return {
        'request_id': result['request_id']
    }