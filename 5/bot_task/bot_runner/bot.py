import os
import logging

import telebot

from db.extra_types import State, AnswerState
import db.db_api as db

from collections import defaultdict

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

TOKEN = os.getenv('TOKEN')
TEMP_VALUES = defaultdict(str)

bot = telebot.TeleBot(TOKEN)


def add_temp_values(name, value):
    if len(TEMP_VALUES) >= 5:
        TEMP_VALUES.clear()
    TEMP_VALUES[name] = str(value)


def get_state(user_id):
    state = db.get_user_state(user_id=user_id)
    if state is None or user_id is None:
        return State.S_EMPTY.value
    else:
        return db.get_user_state(user_id=user_id)


def update_state(user_id, state):
    if user_id is not None:
        db.update_user_state(user_id=user_id, state=state)


@bot.message_handler(commands=['reset_places'])
def reset_places(message):
    db.reset_places(user_id=message.from_user.id)
    bot.send_message(message.chat.id, text='The history is cleared!')


@bot.message_handler(commands=['list_places'])
def list_places(message):
    places = db.list_places(user_id=message.from_user.id)
    if not places:
        bot.send_message(message.chat.id, text='You have not added any places yet!')
    else:
        bot.send_message(message.chat.id, text='Your places are:'.center(5))
        for i, place in enumerate(places, start=1):
            bot.send_message(message.chat.id,
                             text='{}. Name of the place - {}, date added - {};'.format(
                                 i, place[0], place[1].strftime('%c'))
                             )


@bot.message_handler(commands=['add_place'])
@bot.message_handler(func=lambda message: get_state(message.from_user.id) == State.S_INITIAL.value)
def add_place_name(message):
    bot.send_message(message.chat.id, text='Write name of the place')
    update_state(message.from_user.id, State.S_ADDING_NAME_TO_PLACE.value)


@bot.message_handler(func=lambda message: get_state(message.from_user.id) == State.S_ADDING_NAME_TO_PLACE.value)
def add_place_coord(message):
    place_name = message.text
    add_temp_values('name_of_place', place_name)
    bot.send_message(message.chat.id, text='Send coordinates')
    update_state(message.from_user.id, State.S_ADDING_COORD_TO_PLACE.value)


@bot.message_handler(content_types=['location'])
@bot.message_handler(func=lambda message: get_state(message.from_user.id) == State.S_ADDING_COORD_TO_PLACE.value)
def add_place_final(message):
    place_name = TEMP_VALUES['name_of_place']
    if message.location is None:
        bot.send_message(message.chat.id, text='You should send coordinates of the place {}'.format(place_name))
    else:
        location = message.location
        res = db.add_place(user_id=message.from_user.id, place_name=place_name,
                           lat=location.latitude, lon=location.longitude)
        if res == AnswerState.S_ERROR:
            bot.send_message(message.chat.id,
                             text='The place {} is already existed in db! '
                                  'Try another one'.format(place_name))
        else:
            bot.send_message(message.chat.id, text='The place {} is added'.format(place_name))
        update_state(message.from_user.id, State.S_INITIAL.value)


@bot.message_handler(content_types=['text'])
def first_greeting(message):
    bot.send_message(message.chat.id, text='Hi! Nice to meet you!')
    db.add_user(user_id=message.from_user.id)
    print(get_state(message.from_user.id))
    print(type(get_state(message.from_user.id)))
