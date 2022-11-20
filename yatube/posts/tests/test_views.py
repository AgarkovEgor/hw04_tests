from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Post, Group

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='egor')
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
        cls.templates_pages_names = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:group_posts", kwargs={"slug": cls.group.slug}
            ): "posts/group_list.html",
            reverse(
                "posts:profile", kwargs={"username": cls.post.author}
            ): "posts/profile.html",
            reverse(
                "posts:post_detail", kwargs={"post_id": cls.post.id}
            ): "posts/post_detail.html",
            reverse(
                "posts:post_edit", kwargs={"post_id": cls.post.id}
            ): "posts/post_create.html",
            reverse("posts:post_create"): "posts/post_create.html",
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    class PaginatorViewsTest(TestCase):
        @classmethod
        def setUpClass(cls):
            super().setUpClass()
            # создал двух авторов автор1 автора2
            cls.author = User.objects.create_user(
                username='egor'
            )
            cls.group = Group.objects.create(
                title='Тестовая группа',
                slug='test-slug',
                description='Тестовое описание'
            )
            # 9 постов автора1 с группой group , 4 поста автора2 без группы
            objs = [
                Post(
                    author=cls.author,
                    text=f'Тестовый текст {i}',
                    group=cls.group
                ) for i in range(13)
            ]
            Post.objects.bulk_create(objs)

        def test_first_index_page_show_expected_number(self):
            """Проверяем  кол-во постов на главной странице(стр1)"""
            response = self.client.get(reverse('posts:index'))
            self.assertEqual(len(response.context.get('page_obj')), 10)

        def test_second_index_page_show_expected_number(self):
            """Проверяем  кол-во постов на главной странице(стр2)"""
            response = self.client.get(reverse('posts:index') + '?page=2')
            self.assertEqual(len(response.context.get('page_obj')), 3)

        def test_first_group_list_page_show_expected_number(self):
            """Проверяем  кол-во постов на странице группы(стр1)"""
            response = self.guest_client.get(
                reverse('posts:group_posts', kwargs={'slug': self.group.slug}))
            self.assertEqual(len(response.context.get('page_obj')), 10)

        def test_second_group_list_page_show_expected_number(self):
            """Проверяем  кол-во постов  странице группы(стр2)"""
            response = self.guest_client.get(
                reverse('posts:group_posts',
                        kwargs={'slug': self.group.slug}))
            self.assertEqual(len(response.context.get('page_obj')), 3)

        def test_first_profile_page_show_expected_number(self):
            """Проверяем  кол-во постов на странице профиля(стр1)"""
            response = self.guest_client.get(
                reverse('posts:profile',
                        kwargs={'username': self.post.author}))
            self.assertEqual(len(response.context.get('page_obj')), 10)

        def test_second_profile_page_show_expected_number(self):
            """Проверяем  кол-во постов на странице профиля(стр2)"""
            response = self.guest_client.get(
                reverse('posts:profile',
                        kwargs={'username': self.post.author}))
            self.assertEqual(len(response.context.get('page_obj')), 3)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """На главную страницу передается правильный контекст"""
        response = self.guest_client.get(
            reverse('posts:index'))
        post = response.context.get('page_obj')[0]
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.pk, self.post.pk)

    def test_group_list_show_correct_context(self):
        """Проверяем что на страницу группы передается правильный контекст"""
        response = self.guest_client.get(
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}))
        group = response.context.get('group')
        self.assertEqual(group.title, self.group.title)
        group_obj = response.context.get('page_obj')[0]
        self.assertEqual(group_obj.text, self.post.text)
        self.assertEqual(group_obj.author, self.post.author)
        self.assertEqual(group_obj.group, self.post.group)
        self.assertEqual(group_obj.pk, self.post.pk)

    def test_profile_page_show_correct_context(self):
        """Проверяем что на страницу профиля передается правильный контекст"""
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': self.post.author})
        )
        author = response.context.get('author')
        self.assertEqual(author.username, self.user.username)

    def test_detail_page_show_correct_context(self):
        """Проверяем что на страницу поста передается правильный контекст"""
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        post = response.context.get('post')
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.pk, self.post.pk)

    def test_post_edit_page_show_correct_context(self):
        """Проверка страницы редактирования на правильный контекст"""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_create_page_show_correct_context(self):
        """Проверяем страницу создания поста на правильный контекст"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_check_group_in_pages(self):
        """Проверяем создание поста на страницах с выбранной группой"""
        form_fields = {
            reverse("posts:index"): Post.objects.get(group=self.post.group),
            reverse(
                "posts:group_posts", kwargs={"slug": self.group.slug}
            ): Post.objects.get(group=self.post.group),
            reverse(
                "posts:profile", kwargs={"username": self.post.author}
            ): Post.objects.get(group=self.post.group),
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                form_field = response.context['page_obj']
                self.assertIn(expected, form_field)

    def test_check_group_not_in_mistake_group_list_page(self):
        """Проверяем чтобы созданный Пост с группой не попап в чужую группу."""
        form_fields = {
            reverse(
                "posts:group_posts", kwargs={'slug': self.group.slug}
            ): Post.objects.exclude(group=self.post.group),
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                form_field = response.context['page_obj']
                self.assertNotIn(expected, form_field)
