from django.contrib.auth import get_user_model  # type: ignore
from django.test import Client, TestCase  # type: ignore
from django.urls import reverse  # type: ignore

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create(username='user1')
        cls.user2 = User.objects.create(username='user2')
        cls.note1 = Note.objects.create(
            title='Title1', text='text1', slug='title1', author=cls.user1
        )
        cls.note2 = Note.objects.create(
            title='Title2', text='text2', slug='title2', author=cls.user2
        )
        cls.user1_client = Client()
        cls.user1_client.force_login(cls.user1)

    def test_different_notes_in_and_not_in_object_list(self):
        """Своя заметка попадает в список, а чужая - нет"""
        response = self.user1_client.get(reverse('notes:list'))
        self.assertIn(self.note1, response.context['object_list'])
        self.assertNotIn(self.note2, response.context['object_list'])

    def test_add_and_edit_note_pages_contain_form(self):
        """Форма передается на страницы создания и редактирования заметки"""
        urls_args = (
            ('notes:add', None),
            ('notes:edit', (self.note1.slug,)),
        )
        for name, args in urls_args:
            with self.subTest(name=name):
                response = self.user1_client.get(reverse(name, args=args))
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
