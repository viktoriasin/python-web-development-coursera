import os

from map_api.client import Client
from . import TestCase


class ClientTest(TestCase):
    def test_no_api_key(self):
        with self.assertRaises(ValueError):
            client = Client()
            client.distance_matrix(["Sydney", "Melbourne"])

    def test_invalid_api_key(self):
        with self.assertRaises(Exception):
            client = Client(key="Invalid key.")
            client.distance_matrix(["Sydney", "Melbourne"])


class DistanceMatrixCase(TestCase):
    def setUp(self):
        self.key = os.environ.get('API_KEY')
        self.client = Client(self.key)

    def test_simple_req(self):
        res = self.client.distance_matrix(origins=["Denver, CO"],
                                          destinations=['Westminster, CO'])

        assert not res['allToAll']
        assert round(res['distance'][1]) == 14

    def test_lat_lon_req(self):
        destination = [{
            "latLng": {
                "lat": 39.863462,
                "lng": -105.050335
            }
        }]
        location = [{
            "latLng": {
                "lat": 39.738453,
                "lng": -104.984853
            }
        }]
        res = self.client.distance_matrix(origins=location,
                                          destinations=destination)

        assert not res['allToAll']
        assert round(res['distance'][1]) == 14

    def tearDown(self):
        self.client.close_session()



