# Подключение шаблонов кастомных страниц для ошибок с помощью view-классов

from django.shortcuts import render
from django.views.generic import TemplateView


class About(TemplateView):
    """view-класс для страницы about"""

    template_name = 'pages/about.html'


class Rules(TemplateView):
    """view-класс для страницы rules"""

    template_name = 'pages/rules.html'


# view-функции для ошибок 403csrf, 404, 500
def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    return render(request, 'pages/500.html', status=500)
