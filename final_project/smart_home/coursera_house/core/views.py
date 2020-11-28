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
