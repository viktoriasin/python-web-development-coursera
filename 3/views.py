from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST


def empty_case(request):
    if request.method != 'GET':
        return HttpResponse(status=405)
    else:
        return HttpResponse(status=200)


def slug_request(request, slug):
    return HttpResponse(content=slug, status=200)


def sum_two_num(request, first_num, second_num):
    return HttpResponse(content='{}'.format(int(first_num) + int(second_num)), status=200)


def sum_get_method(request):
    items = request.GET
    try:
        a, b = items['a'], items['b']
        a, b = int(a), int(b)
        return HttpResponse(content='{}'.format(a+b), status=200)
    except Exception as e:
        return HttpResponse(status=400)


def sum_post_method(request):
    items = request.POST
    try:
        a, b = items['a'], items['b']
        a, b = int(a), int(b)
        return HttpResponse(content='{}'.format(a+b), status=200)
    except Exception as e:
        return HttpResponse(status=400)


