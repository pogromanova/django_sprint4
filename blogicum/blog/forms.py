# Формы для авторизации и публикации постов

from django import forms

from .models import Post, User, Comment


class UserForm(forms.ModelForm):
    """
    Форма для создания и редактирования профиля пользователя
    Поля из модели: first_name, last_name, email, username
    """

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username')


class PostForm(forms.ModelForm):
    """
    Форма для создания и редактирования публикаций
    Поля: из модели кроме author (он автоматически
                            задается текущим логином пользователя),
    Настройка отображения поля pub_date с помощью виджета DateInput
                            для выбора даты и времени
    """

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'datetime-local'})
        }


class CommentForm(forms.ModelForm):
    """Форма для добавления комментариев к публикациям с полем text"""

    class Meta:
        model = Comment
        fields = ('text',)
