import requests
import logging
from requests.exceptions import HTTPError
from json.decoder import JSONDecodeError

from ..settings import SMART_HOME_ACCESS_TOKEN, SMART_HOME_API_URL

logger = logging.getLogger(__name__)


def get_api_smart_home(url=SMART_HOME_API_URL, token=SMART_HOME_ACCESS_TOKEN):
    headers = {'Authorization': f'Bearer {token}'}
    try:
        res = requests.get(
            url, headers=headers
        ).json()
        if res['status'] == 'ok':
            return res['data']
        else:
            return []
    except HTTPError as http_err:
        logger.error(f'HTTP error occurred: {http_err}')
        return []
    except JSONDecodeError as j_error:
        logger.error(f'Can not load json of response data: {j_error}')
        return []
    except ValueError as val_err:
        logger.error(f'Can not load json of response data: {val_err}')
        return []
    except KeyError as k_err:
        logger.error(f'Key error of response data: {k_err}')
        return []
    except Exception as err:
        logger.error(f'Other error occurred: {err}, response answer: {res}')
        return []


def post_api_smart_home(url=SMART_HOME_API_URL, token=SMART_HOME_ACCESS_TOKEN, data={}):
    headers = {'Authorization': f'Bearer {token}'}
    try:
        requests.post(
            url,
            headers=headers,
            json=data
        )
    except HTTPError as http_err:
        logger.error(f'HTTP error occurred: {http_err}')
    except JSONDecodeError as j_error:
        logger.error(f'Can not encode data: {j_error}')
        return []
    except Exception as err:
        logger.error(f'Other error occurred: {err}')
        return []
