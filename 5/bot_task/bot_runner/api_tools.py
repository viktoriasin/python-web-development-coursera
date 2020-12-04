import os

from bot_runner.bot import bot
from map_api.client import Client
from db.db_api import list_places


def collect_places(user_id):
    places = list_places(user_id, 100)
    i = 0
    rows_returned = places.rowcount
    while i <= rows_returned:
        temp_places = places[i:i + 100]  # Mapquest API can handle only 100 items in one to many mode
        places_ids = []
        req_data = []
        for place in temp_places:
            places_ids.append(place[0])
            req_data.append({
                "latLng": {
                    "lat": place[1],
                    "lng": place[2]
                }})
        yield req_data, places_ids


def call_for_places_nearby(user_id, user_lat, user_lon):
    client = Client(os.environ.get('API_KEY'))
    cur_location = [{
        "latLng": {
            "lat": user_lat,
            "lng": user_lon
        }
    }]
    for places, places_ids in collect_places(user_id):
        distances = client.distance_matrix(origins=cur_location,
                                     destinations=places)['distance']
        for distance in distances[1:]:
            
