import requests

import logging

from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.core.mail import send_mail
from .models import Setting, update_or_create, get_from_db
from .form import ControllerForm
from .api_smart_home import get_api_smart_home, post_api_smart_home

logger = logging.getLogger(__name__)

# def smart_home_manager():
#     logger.error('KNJKNKJNjk')
#     hot_water_target_temperature = get_from_db('hot_water_target_temperature')
#     bedroom_target_temperature = get_from_db('bedroom_target_temperature')
#     controllers = get_api_smart_home()
#     load = {}
#
#     if controllers:
#         controllers_cleaned = {x['name']: x['value'] for x in controllers}
#         if controllers_cleaned.get('leak_detector'):
#             logger.warning('Leaks detected!')
#             load['cold_water'] = False
#             load['hot_water'] = False
#             send_mail(
#                 'Leaks detected!',
#                 'Watch out! The leaks was detected!',
#                 'vicktoria.sin@yandex.ru',
#                 ['vicktoria.sin@yandex.ru'],
#                 fail_silently=False
#             )
#
#         if not controllers_cleaned.get('cold_water'):
#             logger.warning('There are no cold water!')
#             load['boiler'] = False
#             load['washing_machine'] = 'off'
#
#         if hot_water_target_temperature:
#             if controllers_cleaned.get('boiler_temperature') < hot_water_target_temperature.value * 0.9:
#                 if controllers_cleaned.get('cold_water'):
#                     logger.info('Turning boiler on!')
#                     load['boiler'] = True
#
#             if controllers_cleaned.get('boiler_temperature') > hot_water_target_temperature.value * 1.1 \
#                     and load.get('boiler'):
#                 logger.info('Turning boiler off!')
#                 load['boiler'] = False
#
#         if controllers_cleaned.get('outdoor_light') < 50 \
#                 and not controllers_cleaned.get('bedroom_light') \
#                 and not controllers_cleaned.get('curtains') == 'slightly_open':
#             logger.info('Open curtains!')
#             load['curtains'] = 'open'
#
#         if controllers_cleaned.get('outdoor_light') >= 50 or controllers_cleaned.get('bedroom_light') \
#                 and not controllers_cleaned.get('bedroom_light') \
#                 and not controllers_cleaned.get('curtains') == 'slightly_open':
#             load['curtains'] = 'close'
#             logger.info('Close curtains!')
#
#         if bedroom_target_temperature:
#             if controllers_cleaned.get('bedroom_temperature') > bedroom_target_temperature.value * 1.1:
#                 logger.info('Turning air_conditioner off!')
#                 load['air_conditioner'] = True
#             if controllers_cleaned.get('bedroom_temperature') < bedroom_target_temperature.value * 0.9:
#                 logger.info('Turning air_conditioner off!')
#                 load['air_conditioner'] = False
#
#         if controllers_cleaned.get('smoke_detector'):
#             logger.warning('Smoke detected!')
#             load['air_conditioner'] = False
#             load['bedroom_light'] = False
#             load['bathroom_light'] = False
#             load['boiler'] = False
#             load['washing_machine'] = False
#
#         if load:
#             controllers = [{'name': key, 'value': value} for key, value in load.items()]
#             post_api_smart_home(data={'controllers': controllers})

# 1. Делайте лишь один GET-запрос для получения данных из API на каждый запрос
# к вашему приложению.
# 2. Делайте не более одного POST-запроса на изменение данных в API на каждый
# запрос к вашему приложению.
# Если параметры света в форме не изменились - не надо их отправлять в API.
# Все это относится и к задаче в celery.
# 3. Обязательно отрабатывайте вариант, когда ваши запросы к API
# заканчиваются неудачно.
# 4. Помните, что запросы requests могут как бросать исключения,
# так и просто возвращать ответ с ошибочным кодом.
# 5. Пока форма невалидна в POST-запросе - не делайте каких-либо запросов к API.
# Грейдер не оценит такого внимания.

#
# >>> f = ContactForm(data)
# >>> f.is_valid()
# True
# >>> f.cleaned_data


class ControllerView(FormView):
    form_class = ControllerForm
    template_name = 'core/control.html'
    success_url = reverse_lazy('form')

    initials = {}

    def get_context_data(self, **kwargs):
        context = super(ControllerView, self).get_context_data()
        controller_data = get_api_smart_home()
        devices_context = {}
        for device in controller_data:
            devices_context[device['name']] = device['value']
        context['data'] = devices_context
        self.initials['bedroom_light'] = devices_context.get('bedroom_light', False)
        self.initials['bathroom_light'] = devices_context.get('bathroom_light', False)
        self.initials['bedroom_target_temperature'] = devices_context.get('bedroom_temperature', 21)
        self.initials['hot_water_target_temperature'] = devices_context.get('boiler_temperature', 80)
        return context

    def get_initial(self):
        # TODO сделать так чтобы обновлялось одновременно с get_context_data
        initial = super(ControllerView, self).get_initial()
        initial['bedroom_target_temperature'] = self.initials.get('bedroom_target_temperature', 21)
        initial['hot_water_target_temperature'] = self.initials.get('hot_water_target_temperature', 80)
        initial['bedroom_light'] = self.initials.get('bedroom_light', False)
        initial['bathroom_light'] = self.initials.get('bathroom_light', False)
        return initial

    def form_valid(self, form):

        form_data = {
            'bedroom_target_temperature': form.cleaned_data['bedroom_target_temperature'],
            'hot_water_target_temperature': form.cleaned_data['hot_water_target_temperature'],
            'bedroom_light': form.cleaned_data['bedroom_light'],
            'bathroom_light': form.cleaned_data['bathroom_light'],
            'smoke_detector': False
        }

        controller_data = get_api_smart_home()
        for x in controller_data:
            if x['name'] in ('bedroom_light', 'bathroom_light',
                             'bedroom_target_temperature', 'hot_water_target_temperature', 'smoke_detector'):
                # только если данные в фоме отличаются от текущих в датчиках обновляем бд
                if x['value'] != form_data.get(x['name']):
                    form_data[x['name']] = x['value']
                else:
                    form_data[x['name']] = None
        for key, value in form_data.items():
            if (value in ('bedroom_light', 'bathroom_light') and not form_data['smoke_detector']) or value:
                defaults = dict(
                    label=f'{key}_label',
                    value=int(value)
                )
                if not update_or_create(key, defaults):
                    return JsonResponse({'error': f'Can not update {key}.There are several object in db by that key.'},
                                        status=400)
        return super(ControllerView, self).form_valid(form)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        if not context.get('data'):
            return self.render_to_response(context, status=502)
        return self.render_to_response(context)
