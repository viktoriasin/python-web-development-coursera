import os

from map_api.client import Client
from db.db_api import list_all_places

METERS_IN_MILES_UNIT = 1609.344


def miles_to_meters_converter(miles):
    return miles * METERS_IN_MILES_UNIT


def get_places(user_id):
    places = list_all_places(user_id=user_id)
    return places


def iter_places(place_cur):
    for row in place_cur:
        yield row[0], {
            "latLng": {
                "lat": row[1],
                "lng": row[2]
            }}


def iter_distance(places, client, cur_location):
    i = 0
    while i <= len(places):
        data = places[i:i + 100]
        i += 100
        print(data)
        yield client.distance_matrix(origins=cur_location,
                                     destinations=data)['distance']


def call_for_places_nearby(user_id, user_lat, user_lon) -> list:
    res_ids = []
    client = Client(os.environ.get('API_KEY'))
    cur_location = [{
        "latLng": {
            "lat": user_lat,
            "lng": user_lon
        }
    }]
    places = get_places(user_id)
    req_data = []
    places_ids = []
    for id_, place in iter_places(places):
        req_data.append(place)
        places_ids.append(id_)
    for distances in iter_distance(req_data, client, cur_location):
        for i, distance in enumerate(distances[1:], start=1):
            if miles_to_meters_converter(distance) < 50000:
                res_ids.append(places_ids[i-1])
                if len(res_ids) == 10:
                    break

        if len(res_ids) == 10:
            break
    return res_ids
