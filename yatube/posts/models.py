from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models


User = get_user_model()


class Group(models.Model):

    title = models.CharField('Название группы', max_length=200)
    slug = models.SlugField('Название URL', unique=True)
    description = models.TextField('Описание группы')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self) -> str:
        return self.title


class Post(models.Model):

    text = models.TextField('Текст поста', help_text='Введите текст')
    pub_date = models.DateTimeField('Дата', auto_now_add=True)
    group = models.ForeignKey(
        Group,
        verbose_name='Группа поста',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        help_text='Группа, к которой будет относиться пост'
    )

    author = models.ForeignKey(
        User,
        verbose_name='Автор поста',
        on_delete=models.CASCADE,
        related_name='posts',
    )

    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self) -> str:
        return self.text[:settings.SLICE_END]


class Comment(models.Model):

    text = models.TextField(verbose_name='Текст комментария')
    created = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(
        Post,
        null=True,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )
