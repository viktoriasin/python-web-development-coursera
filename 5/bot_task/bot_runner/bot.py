import os
import logging
import base64

import telebot
from telebot import types

from collections import defaultdict

from db.extra_types import State, AnswerState
import db.db_api as db
from bot_runner.api_tools import call_for_places_nearby


logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

TOKEN = os.getenv('TOKEN')
TEMP_VALUES = defaultdict(str)

bot = telebot.TeleBot(TOKEN)


def add_temp_values(name, value):
    if len(TEMP_VALUES) >= 5:
        TEMP_VALUES.clear()
    TEMP_VALUES[name] = str(value)


def create_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(text=c, callback_data=c)
               for c in ('YES', 'NO')]
    keyboard.add(*buttons)
    return keyboard


def get_state(user_id):
    state = db.get_user_state(user_id=user_id)
    if state is None or user_id is None:
        return State.S_EMPTY.value
    else:
        return db.get_user_state(user_id=user_id)


def update_state(user_id, state):
    if user_id is not None:
        db.update_user_state(user_id=user_id, state=state)


@bot.message_handler(commands=['start'])
def first_greeting(message):
    bot.send_message(message.chat.id, text='Hi! Nice to meet you!')
    bot.send_message(message.chat.id, text='I help you to save all your favorite places!\n'
                                           ' Here what can I do: \n'
                                           ' /add_place - add a new place with its name and coordinates \n'
                                           ' /list_places - list all the places that you have added \n'
                                           ' /reset_places - delete all your places info')
    db.add_user(user_id=message.from_user.id)


@bot.message_handler(commands=['get_places_nearby'])
def call_places_nearby(message):
    bot.send_message(message.chat.id,
                     text='Send your current locations, please')
    update_state(message.from_user.id, State.S_GET_PLACES_NEARBY.value)


@bot.message_handler(content_types=['location'], func=lambda message: get_state(message.from_user.id) == State.S_GET_PLACES_NEARBY.value)
def get_places_nearby(message):
    if message.location is None:
        bot.send_message(message.chat.id,
                         text='You should send coordinates of your current location!')
    else:
        location = message.location
        bot.send_message(message.chat.id, text='Looking for places ...')
        ids = call_for_places_nearby(message.from_user.id,
                                     location.latitude, location.longitude)
        if not ids:
            bot.send_message(message.chat.id, text='Can not find nearby places!')
            update_state(message.from_user.id, State.S_INITIAL.value)
        else:
            bot.send_message(message.chat.id,
                             text='Nearby places are: ')
            for place in db.get_place_by_ids(place_ids=ids):
                bot.send_message(message.chat.id,
                                 text=f'Place name: {place[0]} \n'  # TODO chane to attregetter with names
                                 f'Place latitude: {place[1]} \n'
                                 f'Place longitude: {place[2]} \n')
                bot.send_location(message.chat.id,
                                  place[1],
                                  place[2])
            update_state(message.from_user.id, State.S_INITIAL.value)


@bot.message_handler(commands=['reset_places'])
def reset_places(message):
    keyboard = create_keyboard()
    bot.send_message(message.chat.id,
                     text='Are you sure you want to delete ALL your places?',
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda x: True)
def reset_places_confirmation(callback_query):
    message = callback_query.message
    if callback_query.data == 'YES':
        db.reset_places(user_id=callback_query.from_user.id)
        bot.send_message(message.chat.id, text='The history is cleared!')
    elif callback_query.data == 'NO':
        bot.send_message(message.chat.id, text='Ok, deleting process has delayed!')


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


@bot.message_handler(func=lambda message: get_state(message.from_user.id) == State.S_ADDING_COORD_TO_PLACE.value, content_types=['location'])
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
                             text='Could not add that place.Check your data validity.'
                                  'Maybe you have already added it?')
        else:
            bot.send_message(message.chat.id, text='The place {} is added'.format(place_name))
        update_state(message.from_user.id, State.S_INITIAL.value)

