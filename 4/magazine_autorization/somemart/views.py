import json

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
import base64
from .models import Item, Review
# from .form_mart import ItemForm, ReviewForm

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django import forms
from django.core.exceptions import ValidationError

from .models import Item, Review


# решение преподававтелей
# def basicauth(view_func):
#     """Декоратор реализующий HTTP Basic AUTH."""
#     @wraps(view_func)
#     def _wrapped_view(request, *args, **kwargs):
#         if 'HTTP_AUTHORIZATION' in request.META:
#             auth = request.META['HTTP_AUTHORIZATION'].split()
#             if len(auth) == 2:
#                 if auth[0].lower() == 'basic':
#                     token = base64.b64decode(auth[1].encode('ascii'))
#                     username, password = token.decode('utf-8').split(':')
#                     user = authenticate(username=username, password=password)
#                     if user is not None and user.is_active:
#                         request.user = user
#                         return view_func(request, *args, **kwargs)
#
#         response = HttpResponse(status=401)
#         response['WWW-Authenticate'] = 'Basic realm="Somemart staff API"'
#         return response
#     return _wrapped_view

class MyAuthorizationBackend:

    def get_authorization_header(self, request):
        return request.headers.get('HTTP_AUTHORIZATION', '')

    def authenticate(self, request, username=None, password=None):
        auth_query = self.get_authorization_header(request).split()
        if not auth_query or auth_query[0].lower() != 'basic':
            return None

        if len(auth_query) == 1 or len(auth_query) > 2:
            return None
        try:
            login, pass_ = base64.b64decode(auth_query[1].encode('ascii')).decode('utf-8').split(':')
        except (TypeError, UnicodeDecodeError):
            return None
        user = authenticate(username=login, password=pass_)
        if user is not None and  user.is_active:
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class ItemForm(forms.Form):
    title = forms.CharField(max_length=64)
    description = forms.CharField(max_length=1024)
    price = forms.IntegerField(min_value=1, max_value=1000000)

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def clean_description(self):
        if type(self.data['description']) is int:
            raise forms.ValidationError('description cant be a number!')
        return self.cleaned_data['description']

    def clean_title(self):
        if type(self.data['title']) is int:
            raise forms.ValidationError('title cant be a number!')
        return self.cleaned_data['title']


class ReviewForm(forms.Form):
    text = forms.CharField(max_length=1024)
    grade = forms.IntegerField(min_value=1, max_value=10)

    def clean_text(self):
        if type(self.data['text']) is int:
            raise forms.ValidationError('text cant be a number!')
        return self.cleaned_data['text']


@method_decorator(csrf_exempt, name='dispatch')
class AddItemView(View):
    """View для создания товара."""

    def post(self, request):
        auth = MyAuthorizationBackend()
        if not request.user.is_authenticated:
            user = auth.authenticate(request)
            if user is None:
                # не прошел аутентификацию
                return JsonResponse(data={}, status=401)
        try:
            form_json_data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponse(status=400)
        form = ItemForm(form_json_data)
        if form.is_valid():
            if self.user.is_taff:
                context = form.cleaned_data
                i = Item.objects.create(
                    title=context['title'],
                    description=context['description'],
                    price=context['price']
                )
                i.save()
                return JsonResponse(data={'id': i.pk},
                                    status=201,
                                    content_type="application/json")
            else:
                return JsonResponse(data={}, status=403)
        else:
            return JsonResponse(data={}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class PostReviewView(View):
    """View для создания отзыва о товаре."""

    def post(self, request, item_id):
        try:
            form_json_data = json.loads(request.body)
            item_to_grade = Item.objects.get(pk=item_id)
        except json.JSONDecodeError:
            return JsonResponse(data={}, status=400)
        except ObjectDoesNotExist:
            return JsonResponse(data={'error': 'товара с таким id не существует'},
                                status=404,
                                content_type="application/json")
        form = ReviewForm(form_json_data)
        if form.is_valid():
            context = form.cleaned_data
            r = Review.objects.create(
                text=context['text'],
                grade=context['grade'],
                item=item_to_grade
            )
            r.save()
            return JsonResponse(data={'id': r.pk}, status=201)
        else:
            return JsonResponse(data={}, status=400)


class GetItemView(View):
    """View для получения информации о товаре.

    Помимо основной информации выдает последние отзывы о товаре, не более 5
    штук.
    """

    def get(self, request, item_id):

        try:
            item_to_grade = Item.objects.get(pk=item_id)
            reviews = Review.objects.filter(item__pk=item_to_grade.pk).order_by('-pk')[:5].values()
            return JsonResponse(data={
                "id": item_id,
                "title": item_to_grade.title,
                "description": item_to_grade.description,
                "price": item_to_grade.price,
                "reviews": list(reviews)
            },
                status=200,
                content_type="application/json")
        except ObjectDoesNotExist:
            return JsonResponse(data={'error': 'товара с таким id не существует'}, status=404)
