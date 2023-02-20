from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class URLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая Группа',
            slug='test_slug',
            description='тестовое описание группы'
        )
        cls.user = User.objects.create_user(username='auth_user')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author,
            group=cls.group,
        )

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)
        self.list_adress = (
            ('posts:index', None,
             '/'),
            ('posts:group_list', (self.group.slug,),
             f'/group/{self.group.slug}/'),
            ('posts:profile', (self.user,),
             f'/profile/{self.user.username}/'),
            ('posts:post_detail', (self.post.pk,),
             f'/posts/{self.post.id}/'),
            ('posts:post_create', None,
             '/create/'),
            ('posts:post_edit', (self.post.pk,),
             f'/posts/{self.post.id}/edit/'),
        )
        self.exception_name = (
            ('posts:post_edit', (self.post.pk,)),
            ('posts:post_create', None,),
        )

    def test_page_404(self):
        """"Проверка кода 404 на несуществующую страницу."""
        response = self.client.get('/somethingstrange/', follow=True)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND.value)

    def test_pages_uses_correct_quest(self):
        """Тест проверки соответствия, что хардкор ссылки равны URL."""
        for name, args, url in self.list_adress:
            with self.subTest(name=name):
                self.assertEqual((reverse(name, args=args)), url)

    def test_urls_author_client(self):
        """Тест проверки соответствия,
        что у автора поста есть доступ ко всем URL."""
        for name, args, url in self.list_adress:
            with self.subTest(name=name):
                response = self.authorized_author.get(reverse(name, args=args))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_user_client(self):
        """Тест проверки соответствия,
        что у авторизованого пользователя
        есть доступ ко всем URL,
        кроме редактирования поста если он не его автор."""
        for name, args, url in self.list_adress:
            with self.subTest(name=name):
                if name == 'posts:post_edit':
                    response = self.authorized_user.get(
                        reverse(name, args=args),
                    )
                    self.assertRedirects(
                        response,
                        reverse('posts:post_detail', args=[self.post.pk],)
                    )
                else:
                    response = self.authorized_user.get(
                        reverse(name, args=args)
                    )
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_guest_client(self):
        """Тест проверки соответствия,
        что у неавторизованного пользователя
        есть доступ ко всем URL,
        кроме создания и редактирования поста."""
        exception_name = (
            'posts:post_edit',
            'posts:post_create'
        )
        login_name = reverse('users:login')
        for name, args, url in self.list_adress:
            with self.subTest(name=name):
                reverse_name = (reverse(name, args=args))
                if name in exception_name:
                    reverse_name = (reverse(name, args=args))
                    response = self.client.get(reverse(name, args=args),)
                    self.assertRedirects(
                        response, f'{login_name}?next={reverse_name}'
                    )
                else:
                    response = self.client.get(reverse(name, args=args),)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_uses_correct_template_quest(self):
        """URL-адрес использует соответствующий шаблон"""
        url = (
            ('posts:group_list', (self.group.slug,),
             'posts/group_list.html'),
            ('posts:index', None,
             'posts/index.html'),
            ('posts:profile', (self.author,),
             'posts/profile.html'),
            ('posts:post_detail', (self.post.pk,),
             'posts/post_detail.html'),
            ('posts:post_edit', (self.post.pk,),
             'posts/create_post.html'),
            ('posts:post_create', None,
             'posts/create_post.html'),
        )
        for name, args, templates in url:
            with self.subTest(name=name):
                response = self.authorized_author.get(
                    reverse(name, args=args),
                )
                self.assertTemplateUsed(response, templates)
