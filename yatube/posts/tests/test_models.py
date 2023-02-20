from django.conf import settings
from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый_пост_ок',
        )

    def test_model_post_have_correct_object_names(self):
        '''Проверка длины __str__ на первые пятнадцать символов поста.'''
        correct_object_names = self.post.text[:settings.FIRST_CHARACTERS_POST]
        self.assertEqual(correct_object_names, str(self.post))

    def test_model_group_have_correct_object_names(self):
        '''Проверка длины __str__ на первые пятнадцать символов группы.'''
        correct_object_names = self.group.title
        self.assertEqual(correct_object_names, str(self.group))

    def test_model_post_have_correct_verbose_names(self):
        """"Проверка атрибута verbose_name."""
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата',
            'author': 'Автор поста',
            'group': 'Группа поста',
        }
        for field, correct in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name, correct)

    def test_model_post_have_correct_help_text(self):
        """"Проверка атрибута help_text."""
        field_help_texts = {
            'text': 'Введите текст',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, correct in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, correct)
