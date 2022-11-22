from http import HTTPStatus
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group, User


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='egor')
        cls.user2 = User.objects.create_user(username='egor1')
        # Создадим запись в БД
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Проверка создания новой записи в БД"""
        post_count = Post.objects.count()
        form_data = {'text': 'Тестовый пост'}
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        new_post = Post.objects.last()
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertRedirects(
            response, reverse('posts:profile',
                              kwargs={'username': self.user.username}))
        self.assertTrue(Post.objects.filter(text=form_data['text']).exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue((new_post.author == self.user) and
                        (new_post.group == self.group))
    def test_post_edit(self):
        """Проверка изменения поста"""
        posts_count = Post.objects.count()
        form_data = {"text": "Измененный пост", "group": self.post.group.id}
        response = self.authorized_client.post(
            reverse("posts:post_edit", args=[self.post.id]),
            data=form_data,
            follow=True,
        )
        old_group_response = self.authorized_client.get(
            reverse('posts:group_posts', args=[self.group.slug])
        )
        self.assertRedirects(
            response, reverse("posts:post_detail", args=[self.post.id]))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(Post.objects.filter(
            text=form_data['text'], group=self.group.id).exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            old_group_response.context['page_obj'].paginator.count == 0)
