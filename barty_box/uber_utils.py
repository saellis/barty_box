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
    redirect_url = 'https://bartybox.herokuapp.com/ride_finder/'
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
        return {'surge_url': url}


# def update_surge(client, pid, multiplier):
#     """Not real, just for sandboxing"""
#     return client.update_sandbox_product(
#         pid,
#         surge_multiplier=multiplier
#     ).status_code


# def update_ride(client, status, ride_id):
#     """Not real, just for sandboxing"""
#     print status
#     print ride_id
#     client.update_sandbox_product(ride_id, status)


def get_ride_details(client, ride_id):
    return client.get_ride_details(ride_id).json
