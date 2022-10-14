from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from ..models import Post, Group, User

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='NoName')
        # Создадим запись в БД для проверки доступности адреса task/test-slug/
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description="Тестовое описание"
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Текстовый пост',
            group=cls.group)

        cls.templates = [
            "/",
            f"/group/{cls.group.slug}/",
            f"/profile/{cls.user}/",
            f"/posts/{cls.post.id}/"]

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            "/": "posts/index.html",
            f"/group/{self.group.slug}/": "posts/group_list.html",
            f"/profile/{self.user.username}/": "posts/profile.html",
            f"/posts/{self.post.id}/": "posts/post_detail.html",
            f"/posts/{self.post.id}/edit/": "posts/create_post.html",
            "/create/": "posts/create_post.html",
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_404(self):
        """"Проверка на ошибку 404"""
        response = self.guest_client.get("/404")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_home_url_exists_at_desired_location(self):
        """"Страница доступна любому пользователю"""
        for template in self.templates:
            with self.subTest(template):
                response = self.guest_client.get(template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_post_id_edit_url_exists_at_author(self):
        """Страница /posts/post_id/edit/ доступна только автору."""
        self.user = User.objects.get(username=self.user)
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)
        response = self.authorized_client.get(f"/posts/{self.post.id}/edit/")
        self.assertEqual(response.status_code, HTTPStatus.OK)
