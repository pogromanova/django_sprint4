# Модели данных для блога:

# PublishedCreated: добавляет поля для отметки о публикации и времени создания
# Category: категория публикации
# Location: хранение местоположения публикации
# Post: публикация с возможностью добавления изображения,
#                                                   категории и местоположения
# Comment: комментарий для публикации

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class PublishedCreated(models.Model):
    """
    Модель для добавления полей отметки о публикации и времени создания
    Атрибуты:
            is_published (флаг публикации, позволяет скрывать объекты)
            created_at (автоматически заполняется при создании объекта датой)
    """

    is_published = models.BooleanField(
        default=True, verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Добавлено'
    )

    class Meta:
        abstract = True


class Category(PublishedCreated):
    """
    Модель категории для публикаций
    Атрибуты:
            title (название категории)
            description (описание категории)
            slug (идентификатор для формирования URL)
    """

    title = models.CharField(max_length=256, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=('Идентификатор страницы для URL; разрешены '
                   'символы латиницы, цифры, дефис и подчёркивание.')
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return (
            f'{self.title[:30]} - {self.description[:30]} - {self.slug}'
        )


class Location(PublishedCreated):
    """
    Модель местоположения для публикаций
    Атрибуты:
            name (название местоположения. По умолчанию "Планета Земля")
    """

    name = models.CharField(
        max_length=256, verbose_name='Название места', default='Планета Земля'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:30]


class Post(PublishedCreated):
    """
    Модель публикации
    Атрибуты:
            title (заголовок публикации)
            text (основной текст публикации)
            pub_date (дата и время публикации, поддерживает отложенные
                                                                    публикации)
            author (связь с пользователем, создавшим публикацию)
            location (связь с моделью Location)
            category (связь с моделью Category)
            image (поле для загрузки изображения)
    """

    title = models.CharField(max_length=256, verbose_name='Название')
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — '
            'можно делать отложенные публикации.'
        )
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор публикации',
        related_name='posts'
    )
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL,
        null=True, verbose_name='Местоположение',
        related_name='posts'
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, verbose_name='Категория',
        related_name='posts'
    )
    image = models.ImageField('Изображение', upload_to='post_images',
                              blank=True)

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self):
        return (
            f'{(self.author.get_username())[:30]} - {self.title[:30]} '
            f'{self.text[:50]} - {self.pub_date} '
            f'{self.location.name[:30]} - {self.category.title[:30]}'
        )


class Comment(models.Model):
    """
    Модель комментария для публикаций
    Атрибуты:
            text (текст комментария)
            created_at (дата и время добавления комментария)
            author (связь с пользователем, создавшим комментарий)
            post (связь с публикацией, к которой относится комментарий)
    """

    text = models.TextField('Текст')
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Добавлено'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='comments'
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE,
        verbose_name='Публикация',
        related_name='comments'
    )

    class Meta:
        verbose_name = 'коментарий'
        verbose_name_plural = 'коментарии'
        ordering = ('created_at',)
