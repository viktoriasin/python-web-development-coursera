from __future__ import absolute_import, unicode_literals

import logging
from celery import task
from .models import get_from_db
from ..settings import EMAIL_HOST, EMAIL_RECEPIENT
from .api_smart_home import get_api_smart_home, post_api_smart_home
from django.core.mail import EmailMessage


logger = logging.getLogger(__name__)


@task()
def smart_home_manager():
    hot_water_target_temperature = get_from_db('hot_water_target_temperature')
    bedroom_target_temperature = get_from_db('bedroom_target_temperature')
    controllers = get_api_smart_home()
    load = {}

    if controllers:
        controllers_cleaned = {x['name']: x['value'] for x in controllers}
        if controllers_cleaned.get('leak_detector'):
            logger.warning('Leaks detected!')
            if controllers_cleaned.get('cold_water'):
                load['cold_water'] = False
            if controllers_cleaned.get('hot_water'):
                load['hot_water'] = False
            if controllers_cleaned.get('boiler'):
                load['boiler'] = False
            if controllers_cleaned.get('washing_machine') == 'on':
                load['washing_machine'] = 'off'
            email = EmailMessage(
                'Leaks detected!',
                'Watch out! The leaks was detected!',
                EMAIL_HOST,
                [EMAIL_RECEPIENT],
            )
            email.send(fail_silently=False)

        if not controllers_cleaned.get('cold_water'):
            logger.warning('There are no cold water!')
            if controllers_cleaned.get('boiler'):
                load['boiler'] = False
            if controllers_cleaned.get('washing_machine') == 'on':
                load['washing_machine'] = 'off'

        if hot_water_target_temperature:
            if controllers_cleaned.get('boiler_temperature') < hot_water_target_temperature.value * 0.9:
                if controllers_cleaned.get('cold_water') and not controllers_cleaned.get('leak_detector'):
                    logger.info('Turning boiler on!')
                    if not controllers_cleaned.get('boiler'):
                        load['boiler'] = True

            if controllers_cleaned.get('boiler_temperature') > hot_water_target_temperature.value * 1.1 \
                    and load.get('boiler'):
                logger.info('Turning boiler off!')
                if controllers_cleaned.get('boiler'):
                    load['boiler'] = False

        if controllers_cleaned.get('outdoor_light') < 50 \
                and not controllers_cleaned.get('bedroom_light') \
                and not controllers_cleaned.get('curtains') == 'slightly_open':
            logger.info('Open curtains!')
            if controllers_cleaned.get('curtains') != 'open':
                load['curtains'] = 'open'

        if (controllers_cleaned.get('outdoor_light') >= 50 or controllers_cleaned.get('bedroom_light')) \
                and not controllers_cleaned.get('curtains') == 'slightly_open':
            if controllers_cleaned.get('curtains') == 'open':
                load['curtains'] = 'close'
            logger.info('Close curtains!')

        if bedroom_target_temperature:
            if controllers_cleaned.get('bedroom_temperature') > bedroom_target_temperature.value * 1.1:
                logger.info('Turning air_conditioner off!')
                if not controllers_cleaned.get('air_conditioner'):
                    load['air_conditioner'] = True
            if controllers_cleaned.get('bedroom_temperature') < bedroom_target_temperature.value * 0.9:
                logger.info('Turning air_conditioner off!')
                if controllers_cleaned.get('air_conditioner'):
                    load['air_conditioner'] = False

        if controllers_cleaned.get('smoke_detector'):
            logger.warning('Smoke detected!')
            if controllers_cleaned.get('air_conditioner'):
                load['air_conditioner'] = False
            if controllers_cleaned.get('bedroom_light'):
                load['bedroom_light'] = False
            if controllers_cleaned.get('bathroom_light'):
                load['bathroom_light'] = False
            if controllers_cleaned.get('boiler'):
                load['boiler'] = False
            if controllers_cleaned.get('washing_machine') == 'on':
                load['washing_machine'] = 'off'

        if load:
            controllers = [{'name': key, 'value': value} for key, value in load.items()]
            post_api_smart_home(data={'controllers': controllers})