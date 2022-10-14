from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(verbose_name='Название группы', max_length=200)
    slug = models.SlugField(verbose_name='Slug-Url', unique=True)
    description = models.TextField(verbose_name='Описание')

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name='Текст поста', help_text='Текст')
    pub_date = models.DateTimeField(verbose_name='Дата поста',
                                    auto_now_add=True)
    author = models.ForeignKey(
        User,
        verbose_name='Автор поста',
        on_delete=models.CASCADE,
        related_name="posts"
    )
    group = models.ForeignKey(
        Group,
        verbose_name='Группа',
        help_text='Текст2',
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост пользователя'

    def __str__(self):
        return self.text[:15]
