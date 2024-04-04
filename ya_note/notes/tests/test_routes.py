from http import HTTPStatus

from django.contrib.auth import get_user_model  # type: ignore
from django.test import TestCase  # type: ignore
from django.urls import reverse  # type: ignore

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.not_author = User.objects.create(username='not author')
        cls.note = Note.objects.create(
            title='Note title',
            text='Some text',
            slug='note_1',
            author=cls.author
        )

    def test_pages_availability_for_anonymus(self):
        """Страницы доступны анониму"""
        names = (
            'notes:home', 'users:login', 'users:logout', 'users:signup',
        )
        for name in names:
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_user(self):
        """Страницы доступны юзеру"""
        names = ('notes:list', 'notes:success', 'notes:add',)
        self.client.force_login(self.not_author)
        for name in names:
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_edit_delete_availability(self):
        """Доступ к заметке, ее редактированию и удалению"""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.not_author, HTTPStatus.NOT_FOUND),
        )
        names = (
            'notes:detail', 'notes:edit', 'notes:delete',
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in names:
                with self.subTest(user=user, name=name):
                    response = self.client.get(
                        reverse(name, args=(self.note.slug,))
                    )
                    self.assertEqual(response.status_code, status)

    def test_redirects_for_anonymus(self):
        """Редирект анонима на страницу логина"""
        urls = (
            ('notes:list', None), ('notes:success', None), ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        login_url = reverse('users:login')
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                expected_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, expected_url)
