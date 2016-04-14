import json
import requests
import uber_rides
from uber_rides.client import UberRidesClient
from uber_rides.auth import AuthorizationCodeGrant
from uber_rides.session import Session
from uber_rides.errors import ClientError


class UberRide(object):

    def __init__(self, product, start_latitude, start_longitude):
        self.product = product
        self.st_lat = start_latitude
        self.st_lon = start_longitude
        self.config = json.load(open('../conf.json', 'rb'))
        self.redirect_url = 'https://bartybox.herokuapp.com/'
        self.auth_flow = AuthorizationCodeGrant(
            self.config['uber']['client_id'],
            ['profile'],  # permission scopes (Allow App 'Barty Box' access to your...?)
            self.config['uber']['client_secret'],
            self.redirect_url,  # redirect URL must match that on our Uber API account
            # As the name implies, it takes the user to this URL after they are authenticated by Uber
        )
        self.product_id = self._get_product_id()

    def get_auth_url(self):
        """
        The user must be directed to this URL and has to accept terms, etc. before we can call them a ride
        :return: the URL for the user to go to
        """
        return self.auth_flow.get_authorization_url()

    '''
    From Uber's Github:
        Navigate the user to the auth_url where they can grant access to your application.
        After, they will be redirected to a redirect_url with the format YOUR_REDIRECT_URL?code=UNIQUE_AUTH_CODE.
        Use this redirect_url to create a session and start UberRidesClient.
    '''

    def request(self, auth_url, dest_latitude, dest_longitude):

        session = self.auth_flow.get_session(auth_url)
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
        resp = client.get_user_profile()
        prof = resp.json
        first_name = prof.get('first_name')
        print 'hello, {}'.format(first_name)

        response = client.request_ride(  # weird error here...
            product_id=self.product_id,
            start_latitude=self.st_lat,
            start_longitude=self.st_lon,
            end_latitude=dest_latitude,
            end_longitude=dest_longitude,
        )
        ride_details = response.json
        # ride_id = ride_details.get('request_id')
        return ride_details

    def _get_product_id(self):
        """
        :return: the product ID of the uberX/XL for requesting a ride
        """
        session = Session(server_token=self.config['uber']['server_token'])  # FOR READ ONLY CALLS
        client = UberRidesClient(session)
        response = client.get_products(st_lat, st_lon)
        try:
            return filter(lambda x: x['display_name'] == self.product, response.json.get('products'))[0]['product_id']
        except Exception, e:
            raise ValueError('No Ubers of that type available')


if __name__ == '__main__':
    ride = 'uberX'
    st_lat, st_lon = 40.4443533, -79.96083499999997
    dest_lat, dest_lon = 40.4514452209, -79.9337325513
    # 1) make the ride object
    req = UberRide(ride, st_lat, st_lon)
    # 2) get authorized
    url = req.get_auth_url()
    print 'go to {} and authorize.'.format(url)
    auth_url = raw_input('Paste the URL you are redirected to here:\n').strip()
    # 3) use auth_url to request a ride and return the details
    details = req.request(auth_url, dest_lat, dest_lon)
    # 4) tweet the deets
    print details
