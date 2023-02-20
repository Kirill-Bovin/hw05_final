import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Test')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='slug_slug'
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='test_post',
            author=cls.author,
            group=cls.group,
            image=cls.uploaded
        )
        cls.index_url = ('posts:index', None)
        cls.profile_url = (
            'posts:profile', [cls.post.author]
        )
        cls.post_detail_url = (
            'posts:post_detail',
            [cls.group.pk]
        )
        cls.edit_post_url = (
            'posts:post_edit',
            cls.post.pk
        )
        cls.new_post_url = (
            'posts:post_create',
        )
        cls.group_url = (
            'posts:group_posts',
            cls.group.slug
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized = Client()
        self.authorized.force_login(self.author)
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsPagesTests.author)
        cache.clear()

    def check_context_contains_page_or_post(self, context, post=False):
        """Проверка поста с контекстом."""
        if post:
            self.assertIn('post', context)
            post = context['post']
        else:
            self.assertIn('page_obj', context)
            post = context['page_obj'][0]
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.pub_date, self.post.pub_date)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.image, self.post.image)

    def test_index_page_context_is_correct(self):
        """Шаблон index сформирован с правильным контекстом."""
        url, args = self.index_url
        response = self.client.get(reverse(url, args=args))
        self.check_context_contains_page_or_post(response.context)

    def test_profile_page_context_is_correct(self):
        """Шаблон profile сформирован с правильным контекстом."""
        url, args = self.profile_url
        response = self.authorized.get(reverse(url, args=args))
        self.check_context_contains_page_or_post(response.context)
        self.assertEqual(response.context.get('post').author, self.author)

    def test_post_page_context_is_correct(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        url, args = self.post_detail_url
        response = self.authorized.get(reverse(url, args=args))
        self.check_context_contains_page_or_post(response.context, True)

    def test_group_page_context_is_correct(self):
        """Шаблон group сформирован с правильным контекстом."""
        url, args = self.group_url
        self.authorized.get(url, args=args)

    def test_post_added_correctly(self):
        """Проверка что пост появился там где и ожидался."""
        new_group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug2'
        )
        response = self.authorized.get(
            reverse('posts:group_list', args=[new_group.slug])
        )
        self.assertNotIn(new_group, response.context['page_obj'])
        post = Post.objects.first()
        response = self.authorized.get(
            reverse('posts:group_list', args=[self.group.slug])
        )
        self.assertIn(post, response.context['page_obj'])

    def test_index_cache(self):
        response_1 = self.client.get(reverse('posts:index'))
        Post.objects.create(
            author=self.post.author,
            text='Тестовый текст'
        )
        response_2 = self.client.get(reverse('posts:index'))
        self.assertEqual(response_1.content, response_2.content)
        cache.clear()
        response = self.client.get(reverse('posts:index'))
        self.assertNotEqual(response.content, response_2.content)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        Post.objects.bulk_create(
            [Post(author=cls.user, text=f'Тестовый пост {create_post}',
             group=cls.group)
                for create_post in range(settings.NUMBER_OF_ITERATIONS)]
        )

    def setUp(self):
        self.authorized = Client()
        self.authorized.force_login(self.user)
        cache.clear()

    def test_paginator(self):
        """Тест пагинатора."""
        pages = (
                (settings.FIRST_POST, settings.MAX_NUMB_ENTRIES),
                (settings.SECOND_POST, settings.NUMBER_OF_ITERATIONS
                 - settings.FIRST_OF_POSTS)
        )
        urls = (
            ('posts:index', None),
            ('posts:group_list', (self.group.slug,)),
            ('posts:profile', (self.user,)),
        )
        for url, args in urls:
            with self.subTest(urls, args=args):
                for page, count in pages:
                    with self.subTest(page):
                        response = self.client.get(reverse(
                            url, args=args), pages)
                        self.assertEqual(
                            len(response.context['page_obj']),
                            settings.FIRST_OF_POSTS
                        )


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_follower = User.objects.create(username='follower')
        cls.user_unfollower = User.objects.create(username='unfollower')
        cls.user_following = User.objects.create(username='following')
        Post.objects.create(author=cls.user_following, text='Тестовый пост')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_follower)
        cache.clear()

    def test_profile_follow_and_unfollow(self):
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 0)
        """Авторизованный пользователь может подписываться на пользователей."""
        response = self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': 'following'}),
            follow=True
        )
        self.assertEqual(len(response.context['page_obj']), 1)
        """Новая запись пользователя появляется у подписчика."""
        post = Post.objects.create(
            author=self.user_following, text='Тестовый пост'
        )
        cache.clear()
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 2)
        """Авторизованный пользователь
         может удалять пользователей из подписок."""
        response = self.authorized_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': 'following'}), follow=True
        )
        self.assertEqual(len(response.context['page_obj']), 0)
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех, кто не подписан."""
        self.authorized_client.force_login(self.user_unfollower)
        response = self.authorized_client.get(reverse("posts:follow_index"))
        self.assertNotIn(post, response.context["page_obj"])
