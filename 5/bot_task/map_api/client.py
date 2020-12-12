import requests

from urllib.parse import urlencode

import map_api.exceptions as api_exceptions

_DEFAULT_BASE_URL = "http://www.mapquestapi.com"


def extract_body(response):
    if response.status_code != 200:
        raise requests.HTTPError(response.status_code)

    body = response.json()

    api_status = body['info']['statuscode']

    if api_status == 0:
        return body

    raise api_exceptions.ApiError(api_status,
                                  body['info'].get("messages"))


def url_encode(params):
    p = []
    for key, val in params:
        p.append((key, val))
    return urlencode(p)


class Client(object):

    def __init__(self, key=None,
                 requests_kwargs=None, base_url=_DEFAULT_BASE_URL):
        if not key:
            raise ValueError("You must provide API key"
                             "when creating client.")

        self.session = requests.Session()
        self.key = key
        self.requests_kwargs = requests_kwargs or {}
        self.base_url = base_url

    def _generate_auth_url(self, path: str, params: dict):
        params = params.items() or []
        if self.key:
            params.append(('key', self.key))
            return path + "?" + url_encode(params)
        raise ValueError("Must provide API key for this API")

    def close_session(self):
        self.session.close()

    def _request(self, url: str, params: dict, base_url: str = None,
                 requests_kwargs: dict = None, post_json: dict = None):
        if base_url is None:
            base_url = self.base_url

        authed_url = self._generate_auth_url(url, params)

        requests_kwargs = requests_kwargs or {}
        final_requests_kwargs = dict(self.requests_kwargs, **requests_kwargs)

        requests_method = self.session.get
        if post_json is not None:
            requests_method = self.session.post
            final_requests_kwargs["json"] = post_json

        try:
            response = requests_method(base_url + authed_url,
                                       **final_requests_kwargs)
        except Exception as e:
            raise api_exceptions.RequestApiError(e)

        res = extract_body(response)
        return res


from map_api.map import distance_matrix

Client.distance_matrix = distance_matrix
