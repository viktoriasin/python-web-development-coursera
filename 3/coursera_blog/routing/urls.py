from django.conf.urls import url
from django.views.decorators.http import require_GET, require_POST

from . import views

urlpatterns = [
    url(r'^simple_route/$', views.empty_case),
    url(r'^slug_route/(?P<slug>[a-z0-9-_]{1,16})/$', views.slug_request),
    url(r'^sum_route/(?P<first_num>-?[0-9]+)/(?P<second_num>-?[0-9]+)/$', views.sum_two_num),
    url(r'^sum_get_method/$', require_GET(views.sum_get_method)),
    url(r'^sum_post_method/$', require_POST(views.sum_post_method)),
]
