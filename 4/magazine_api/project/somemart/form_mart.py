from django import forms
from django.core.exceptions import ValidationError


def validate_greater_than_0(value):
    if value <= 0:
        raise ValidationError(
            '%(value)s must be greater than a zero!',
            params={'value': value},
        )


class ItemForm(forms.Form):
    title = forms.CharField(max_length=64)
    description = forms.CharField(max_length=1024)
    price = forms.IntegerField(min_value=1, max_value=1000000, validators=validate_greater_than_0)


class ReviewForm(forms.Form):
    text = forms.CharField(max_length=1024)
    grade = forms.IntegerField(min_value=1, max_value=10, validators=validate_greater_than_0)
