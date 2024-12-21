# Подключаем django.contrib.auth.urls для работы с авторизацией
# Создаем путь регистрации
# Настраиваем обработчики для отображения страниц ошибок

from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.urls import path, include, reverse_lazy

urlpatterns = [
    path('admin/', admin.site.urls),
    path("pages/", include('pages.urls')),
    path('', include('blog.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path(
        'auth/registration/',
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=UserCreationForm,
            success_url=reverse_lazy('login'),
        ),
        name='registration',
    ),
]


# Обработчики ошибок
handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'
