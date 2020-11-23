import logging
import sqlite3

from datetime import date, datetime

from .extra_types import State, AnswerState

logger = logging.getLogger(__name__)


def adapt_state(state):
    return state


def convert_state(s):
    return int(s)


sqlite3.register_adapter(State, adapt_state)
sqlite3.register_converter("State", convert_state)


def ensure_connection(func):
    def connector(*args, **kwargs):
        with sqlite3.connect('user_data.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as conn:
            res = func(*args, conn=conn, **kwargs)
        return res

    return connector


@ensure_connection
def init_db(conn, force: bool = False):
    cur = conn.cursor()
    try:
        if force:
            cur.executescript('DROP TABLE IF EXISTS user_data')
            cur.executescript('DROP TABLE IF EXISTS user_state')
            conn.commit()
            logger.warning('db was cleaned')

        cur.execute("CREATE TABLE IF NOT EXISTS user_data ( \
                                    user_id integer, \
                                    place_name text, \
                                    lat real, \
                                    lon real, \
                                    dat_add timestamp, \
                                    FOREIGN KEY (user_id) REFERENCES chat_state(user_id))")

        cur.execute("CREATE TABLE IF NOT EXISTS user_state ( \
                                            user_id integer PRIMARY KEY, \
                                            state state DEFAULT 1)")
        logger.info('db was created')

        conn.commit()

    except (sqlite3.IntegrityError, sqlite3.OperationalError):
        logger.error("couldn't init db")


@ensure_connection
def add_place(conn, user_id, place_name, lat, lon):
    cur = conn.cursor()
    now = datetime.now()
    val = (user_id, place_name, lat, lon, now)
    val_check = (user_id, place_name)
    if cur.execute('SELECT place_name FROM user_data WHERE user_id=? and place_name=?',
                       val_check).fetchall():
        return AnswerState.S_ERROR
    try:
        cur.execute('INSERT INTO user_data VALUES (?, ?, ?, ?, ?)', val)
        conn.commit()
        return AnswerState.S_OK
    except (sqlite3.IntegrityError, sqlite3.OperationalError):
        logger.error("couldn't insert place with data: ({})".format(user_id, place_name, lat, lon))


@ensure_connection
def add_user(conn, user_id):
    cur = conn.cursor()
    val = (user_id,)

    try:
        cur.execute('INSERT INTO user_state(user_id) VALUES (?)', val)
        conn.commit()
        logger.info('user {} was added'.format(user_id))
    except (sqlite3.IntegrityError, sqlite3.OperationalError):
        logger.error("couldn't add user: ({})".format(user_id))


@ensure_connection
def reset_places(conn, user_id):
    cur = conn.cursor()
    val = (user_id,)
    try:
        cur.execute('DELETE FROM user_data WHERE user_id=?',
                    val).fetchall()
        conn.commit()
    except (sqlite3.IntegrityError, sqlite3.OperationalError):
        logger.error("couldn't reset users data")


@ensure_connection
def list_places(conn, user_id):
    cur = conn.cursor()
    val = (user_id,)
    try:
        return cur.execute('SELECT place_name, dat_add FROM user_data '
                           'WHERE user_id=? ORDER BY dat_add DESC LIMIT 10',
                           val).fetchall()
    except (sqlite3.IntegrityError, sqlite3.OperationalError):
        logger.error("couldn't list user place's data")


@ensure_connection
def get_user_state(conn, user_id):
    cur = conn.cursor()
    val = (user_id,)
    try:
        res = cur.execute('SELECT state FROM user_state WHERE user_id=?',
                          val).fetchone()
        if res is not None:
            return res[0]
    except (sqlite3.IntegrityError, sqlite3.OperationalError):
        logger.error("couldn't list users data")


@ensure_connection
def update_user_state(conn, user_id, state):
    cur = conn.cursor()
    val = (state, user_id)
    val_check = (user_id,)
    try:
        assert cur.execute('SELECT 1 FROM user_state WHERE user_id=? LIMIT 1',
                           val_check).fetchone() is not None, 'user {} did not exist'.format(user_id)
        cur.execute('UPDATE user_state SET state=? WHERE user_id=?',
                    val)
        logger.info('user {} state was updated to {}'.format(user_id, state))
        conn.commit()
    except (sqlite3.IntegrityError, sqlite3.OperationalError):
        print("couldn't list users data")


@ensure_connection
def get_place_by_name(conn, user_id):
    cur = conn.cursor()
    val = (user_id,)
    try:
        assert cur.execute('SELECT 1 FROM user_state WHERE user_id=? LIMIT 1',
                           val).fetchone() is not None, 'user {} did not add any places'
        return cur.execute('SELECT place_name FROM user_data WHERE user_id=?',
                           val).fetchone()[0]
    except (sqlite3.IntegrityError, sqlite3.OperationalError):
        logger.error("couldn't list users data")
