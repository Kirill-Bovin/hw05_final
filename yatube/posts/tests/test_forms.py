from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post, User


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestAuthor')
        cls.test_group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Описание поста',
            group=cls.test_group,
        )
        cls.form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create_form(self):
        """Тест формы отправки поста."""
        Post.objects.all().delete()
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста',
            'group': self.test_group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_data, follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user.username}),
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.first()
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group_id, form_data['group'])

    def test_authorized_user_edit_post(self):
        """Автор поста может редактировать пост."""
        posts_count = Post.objects.count()
        new_group = Group.objects.create(
            title='Тестовая группа', slug='test-slug2'
        )
        form_data = {'text': 'post_text', 'group': new_group.id}
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, reverse('posts:post_detail', args=(self.post.id,))
        )
        post = Post.objects.first()
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group_id, form_data['group'])
        response = self.authorized_client.get(
            reverse('posts:group_list', args=[self.test_group.slug])
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotIn(post, response.context['page_obj'])

    def test_guest_create_post(self):
        """Гостевой клиент создает пост.
        И перенаправляется на страницу логина.
        """
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста',
            'group': self.test_group.id,
        }
        response = self.client.post(
            reverse('posts:post_create'), data=form_data, follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        redirect = reverse('login') + '?next=' + reverse('posts:post_create')
        self.assertRedirects(response, redirect)
        self.assertEqual(Group.objects.count(), posts_count)

    def test_create_comment(self):
        """Авторизоавнный клиент может добавить комментарий."""
        comments_count = self.post.comments.count()
        form_data = {'text': 'Новый комментарий'}
        response = self.authorized_client.post(
            (
                reverse(
                    'posts:add_comment', kwargs={'post_id': f'{self.post.id}'}
                )
            ),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            (
                reverse(
                    'posts:post_detail', kwargs={'post_id': f'{self.post.id}'}
                )
            ),
        )
        self.assertEqual(self.post.comments.count(), comments_count + 1)
        self.assertTrue(
            self.post.comments.filter(text='Новый комментарий').exists()
        )

    def test_anonimous_user_create_comment(self):
        """Гостевой клиент создает комментарий.
        И попадает на страницу логина.
        """
        comments_count = self.post.comments.count()
        form_data = {'text': 'Новый комментарий'}
        response = self.client.post(
            (
                reverse(
                    'posts:add_comment', kwargs={'post_id': f'{self.post.id}'}
                )
            ),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, '/auth/login/?next=/posts/1/comment/')
        self.assertEqual(self.post.comments.count(), comments_count)
        self.assertFalse(
            self.post.comments.filter(text='Новый комментарий').exists()
        )
