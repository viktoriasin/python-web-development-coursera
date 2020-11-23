import datetime
import requests
from collections import defaultdict


PARAMS = {'access_token': '17da724517da724517da72458517b8abce117da17da72454d235c274f1a2be5f45ee711', 'v': 5.71}

def extract_age(bdate):
    if bdate:
        parts = bdate.split('.')
        if len(parts) == 3:
            year = int(parts[-1])
            cur_year = datetime.datetime.now().year
            return cur_year - year
    return None


def load_friends_age(session, user_id):
    friends_url = 'https://api.vk.com/method/friends.get'
    result_lines = None
    params={'fields': 'bdate', 'user_id': user_id}
    r = session.get(friends_url, params=params)
    if r.encoding is None:
        r.encoding = 'utf-8'
    try:
        result_lines = r.json()['response']['items']
    except IndexError as v:
        print(v)
    except IndexError as i:
        print(i)
    return result_lines


def get_distr(session, user_id):
    distr = defaultdict(int)
    lines = load_friends_age(session, user_id)
    if lines:
        for line in lines:
            bdate = extract_age(line.get('bdate'))
            if bdate:
                distr[bdate] += 1
        distr = sorted(distr.items(), key=lambda x: (-x[1], x[0]))
    return distr


def load_user_id(session, uid):
    users_get_url = 'https://api.vk.com/method/users.get'
    params={'user_ids': uid}
    user_id = None

    try:
        r = session.get(users_get_url, params=params)
        r.raise_for_status()
        user_id = r.json()['response'][0]['id']
    except requests.HTTPError as h_er:
        print(h_er)
    except IndexError as v:
        print(v)       
    return user_id


def start_counting(uid):
    global PARAMS
    with requests.Session() as s:
        s.params = PARAMS
        res = None
        user_id = load_user_id(s, 'reigning')
        if user_id is not None:
            res = get_distr(s, user_id)
    return res


def calc_age(uid):
    return start_counting(uid)


if __name__ == '__main__':
    res = calc_age('reigning')
    print(res)
