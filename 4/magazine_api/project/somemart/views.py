import json

from django.http import HttpResponse, JsonResponse
from django.views import View
from django.core.exceptions import ObjectDoesNotExist
from marshmallow.validate import Length

from .models import Item, Review
# from .form_mart import ItemForm, ReviewForm

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django import forms
from django.core.exceptions import ValidationError

from marshmallow import Schema, fields


class ItemSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=Length(1, 64))
    description = fields.Str(required=True, validate=Length(1, 1024))
    price = fields.Int(required=True, validate=Range(1, 1000000), strict=True)

    @post_load
    def make(self, data):
        return Item(**data)


class ReviewSchema(Schema):
    id = fields.Int(dump_only=True)
    grade = fields.Int(required=True, validate=Range(1, 10), strict=True)
    text = fields.Str(required=True, validate=Length(1, 1024))

    @post_load
    def make(self, data):
        return Review(**data)


class AddItemView(View):
    """View Ð´Ð»Ñ ÑÐ¾Ð·Ð´Ð°Ð½Ð¸Ñ Ñ‚Ð¾Ð²Ð°Ñ€Ð°."""

    def post(self, request):

        try:
            document = json.loads(request.body)
            schema = ItemSchema(strict=True)
            item = schema.load(document).data
            item.save()
        except (json.JSONDecodeError, ValidationError):
            return HttpResponse(status=400)

        return JsonResponse({'id': item.pk}, status=201)


class PostReviewView(View):
    """View Ð´Ð»Ñ ÑÐ¾Ð·Ð´Ð°Ð½Ð¸Ñ Ð¾Ñ‚Ð·Ñ‹Ð²Ð° Ð¾ Ñ‚Ð¾Ð²Ð°Ñ€Ðµ."""

    def post(self, request, item_id):

        try:
            item = Item.objects.get(pk=item_id)
            document = json.loads(request.body)
            schema = ReviewSchema(strict=True)
            review = schema.load(document).data
            review.item = item
            review.save()
        except Item.DoesNotExist:
            return HttpResponse(status=404)
        except (json.JSONDecodeError, ValidationError):
            return HttpResponse(status=400)

        return JsonResponse({'id': review.pk}, status=201)


class GetItemView(View):
    """View Ð´Ð»Ñ Ð¿Ð¾Ð»ÑƒÑ‡ÐµÐ½Ð¸Ñ Ð¸Ð½Ñ„Ð¾Ñ€Ð¼Ð°Ñ†Ð¸Ð¸ Ð¾ Ñ‚Ð¾Ð²Ð°Ñ€Ðµ.

    ÐŸÐ¾Ð¼Ð¸Ð¼Ð¾ Ð¾ÑÐ½Ð¾Ð²Ð½Ð¾Ð¹ Ð¸Ð½Ñ„Ð¾Ñ€Ð¼Ð°Ñ†Ð¸Ð¸ Ð²Ñ‹Ð´Ð°ÐµÑ‚ Ð¿Ð¾ÑÐ»ÐµÐ´Ð½Ð¸Ðµ Ð¾Ñ‚Ð·Ñ‹Ð²Ñ‹ Ð¾ Ñ‚Ð¾Ð²Ð°Ñ€Ðµ, Ð½Ðµ Ð±Ð¾Ð»ÐµÐµ 5
    ÑˆÑ‚ÑƒÐº.
    """

    def get(self, request, item_id):

        try:
            item = Item.objects.get(pk=item_id)
        except Item.DoesNotExist:
            return HttpResponse(status=404)

        schema = ItemSchema()
        data = schema.dump(item).data
        query = Review.objects.filter(item=item).order_by('-id')
        reviews = query[:5]
        schema = ReviewSchema(many=True)
        data['reviews'] = schema.dump(reviews).data
        return JsonResponse(data, status=200)

# class ItemForm(forms.Form):
#     title = forms.CharField(max_length=64)
#     description = forms.CharField(max_length=1024)
#     price = forms.IntegerField(min_value=1, max_value=1000000)
#
#     def clean_description(self):
#         if type(self.data['description']) is int:
#             raise forms.ValidationError('description cant be a number!')
#         return self.cleaned_data['description']
#
#     def clean_title(self):
#         if type(self.data['title']) is int:
#             raise forms.ValidationError('title cant be a number!')
#         return self.cleaned_data['title']
#
#
# class ReviewForm(forms.Form):
#     text = forms.CharField(max_length=1024)
#     grade = forms.IntegerField(min_value=1, max_value=10)
#
#     def clean_text(self):
#         if type(self.data['text']) is int:
#             raise forms.ValidationError('text cant be a number!')
#         return self.cleaned_data['text']

#
# @method_decorator(csrf_exempt, name='dispatch')
# class AddItemView(View):
#     """View для создания товара."""
#
#     def post(self, request):
#         try:
#             form_json_data = json.loads(request.body)
#         except json.JSONDecodeError:
#             return HttpResponse(status=400)
#         form = ItemForm(form_json_data)
#         if form.is_valid():
#             context = form.cleaned_data
#             i = Item.objects.create(
#                 title=context['title'],
#                 description=context['description'],
#                 price=context['price']
#             )
#             i.save()
#             return JsonResponse(data={'id': i.pk},
#                                 status=201,
#                                 content_type="application/json")
#         else:
#             return JsonResponse(data={}, status=400)
#
#
# @method_decorator(csrf_exempt, name='dispatch')
# class PostReviewView(View):
#     """View для создания отзыва о товаре."""
#
#     def post(self, request, item_id):
#         try:
#             form_json_data = json.loads(request.body)
#             item_to_grade = Item.objects.get(pk=item_id)
#         except json.JSONDecodeError:
#             return JsonResponse(data={}, status=400)
#         except ObjectDoesNotExist:
#             return JsonResponse(data={'error': 'товара с таким id не существует'},
#                                 status=404,
#                                 content_type="application/json")
#         form = ReviewForm(form_json_data)
#         if form.is_valid():
#             context = form.cleaned_data
#             r = Review.objects.create(
#                 text=context['text'],
#                 grade=context['grade'],
#                 item=item_to_grade
#             )
#             r.save()
#             return JsonResponse(data={'id': r.pk}, status=201)
#         else:
#             return JsonResponse(data={}, status=400)
#
#
# class GetItemView(View):
#     """View для получения информации о товаре.
#
#     Помимо основной информации выдает последние отзывы о товаре, не более 5
#     штук.
#     """
#
#     def get(self, request, item_id):
#         try:
#             item_to_grade = Item.objects.get(pk=item_id)
#             reviews = Review.objects.filter(item__pk=item_to_grade.pk).order_by('-pk')[:5].values()
#             return JsonResponse(data={
#                                     "id": item_id,
#                                     "title": item_to_grade.title,
#                                     "description": item_to_grade.description,
#                                     "price": item_to_grade.price,
#                                     "reviews": list(reviews)
#                                 },
#                                 status=200,
#                                 content_type="application/json")
#         except ObjectDoesNotExist:
#             return JsonResponse(data={'error': 'товара с таким id не существует'}, status=404)
#
