# Настраиваем пагинатор на 10 позиций
# Пагинатор на главную, страницу пользователя и страницу категории
# Для реализации функций используем FBV, CBV, миксины

from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import (
    DetailView, CreateView, ListView, UpdateView, DeleteView
)

from .models import Category, Comment, Post, User
from .forms import CommentForm, PostForm, UserForm

PAGINATOR_POST = 10
PAGINATOR_CATEGORY = 10
PAGINATOR_PROFILE = 10


def filtered_post(posts, is_count_comments=True):
    """
    Фильтрация публикаций по условиям:
    - Опубликованные публикации.
    - Дата публикации не превышает текущую.
    - Категория публикации должна быть опубликована.
    """
    posts_query = posts.filter(
        pub_date__lte=datetime.today(),
        is_published=True,
        category__is_published=True
    ).order_by(
        '-pub_date'
    )
    return posts_query.annotate(
        comment_count=Count('comments')
    ).order_by("-pub_date") if is_count_comments else posts_query


class PostListView(ListView):
    """Представление для отображения списка публикаций на главной странице"""

    paginate_by = PAGINATOR_POST
    template_name = 'blog/index.html'

    def get_queryset(self):
        """Получение списка публикаций с использованием фильтрации"""
        return filtered_post(Post.objects.all())


class PostDetailView(DetailView):
    """Представление для отображения деталей конкретной публикации"""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        """
        Дополнение контекста данными о комментариях и формой для добавления
                                                                    комментариев
        """
        return dict(
            **super().get_context_data(**kwargs),
            form=CommentForm(),
            comments=self.object.comments.select_related('author')
        )

    def get_object(self):
        """
        Получение объекта публикации с учётом её статуса публикации.
        Автор видит даже неопубликованные публикации
        """
        posts = Post.objects
        return get_object_or_404(
            posts.filter(
                is_published=True
            ) or posts.filter(
                author=self.request.user
            )
            if self.request.user and self.request.user.is_authenticated
            else filtered_post(Post.objects, is_count_comments=False),
            pk=self.kwargs["post_id"],
        )


class PostCategoryView(ListView):
    """Представление для отображения списка публикаций в категории"""

    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'page_obj'
    paginate_by = PAGINATOR_CATEGORY

    def get_queryset(self):
        """Получение публикаций, отфильтрованных по категории"""
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return filtered_post(self.category.posts.all())

    def get_context_data(self, **kwargs):
        """Добавление информации о категории в контекст"""
        return dict(
            **super().get_context_data(**kwargs),
            category=self.category
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    """Представление для создания публикации"""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        """Автоматическое назначение автором текущего пользователя"""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """
        Перенаправление на профиль автора после успешного создания
                                                                публикации
        """
        return reverse(
            'blog:profile', args=[self.request.user.username]
        )


class PostMixin(LoginRequiredMixin):
    """
    Миксин для проверки, что публикация принадлежит текущему пользователю
    Используется для обновления и удаления публикаций
    """

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        """Проверка авторства публикации"""
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if post.author != self.request.user:
            return redirect(
                'blog:post_detail',
                post_id=self.kwargs['post_id']
            )
        return super().dispatch(request, *args, **kwargs)


class PostUpdateView(PostMixin, UpdateView):
    """Представление для редактирования публикации"""

    def get_success_url(self):
        """Перенаправление на страницу деталей публикации после обновления"""
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])


class PostDeleteView(PostMixin, DeleteView):
    """Представление для удаления публикации"""

    def get_success_url(self):
        """Перенаправление на профиль пользователя после удаления публикации"""
        return reverse('blog:profile', args=[self.request.user.username])


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Представление для редактирования данных профиля пользователя"""

    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self):
        """Получение текущего пользователя"""
        return self.request.user

    def get_success_url(self):
        """Перенаправление на профиль пользователя после обновления"""
        return reverse('blog:profile', args=[self.request.user.username])


class ProfileListView(ListView):
    """Представление для отображения профиля пользователя и его публикаций"""

    paginate_by = PAGINATOR_PROFILE
    template_name = 'blog/profile.html'
    model = Post

    def get_object(self):
        """Получение объекта пользователя по имени пользователя"""
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self):
        """Получение публикаций пользователя"""
        return self.get_object().posts.all()

    def get_context_data(self, **kwargs):
        """Добавление данных профиля в контекст"""
        return dict(
            **super().get_context_data(**kwargs),
            profile=self.get_object()
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Представление для создания комментария к публикации"""

    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        """Добавление формы в контекст"""
        return dict(**super().get_context_data(**kwargs), form=CommentForm())

    def form_valid(self, form):
        """Назначение автором текущего пользователя и привязка к публикации"""
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        """
        Перенаправление на страницу деталей публикации после добавления
                                                                    комментария
        """
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])


class CommentMixin(LoginRequiredMixin):
    """Миксин для проверки принадлежности комментария текущему пользователю"""

    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        """Перенаправление на детали публикации после выполнения действия"""
        return reverse('blog:post_detail', args=[self.kwargs['comment_id']])

    def dispatch(self, request, *args, **kwargs):
        """Проверка авторства комментария"""
        coment = get_object_or_404(Comment, id=self.kwargs['comment_id'])
        if coment.author != self.request.user:
            return redirect('blog:post_detail',
                            post_id=self.kwargs['comment_id']
                            )
        return super().dispatch(request, *args, **kwargs)


class CommentUpdateView(CommentMixin, UpdateView):
    """Представление для редактирования комментария"""

    form_class = CommentForm


class CommentDeleteView(CommentMixin, DeleteView):
    """Представление для удаления комментария"""

    ...
