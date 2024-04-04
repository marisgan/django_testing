from http import HTTPStatus

from django.contrib.auth import get_user_model  # type: ignore
from django.test import Client, TestCase  # type: ignore
from django.urls import reverse  # type: ignore

from pytils.translit import slugify  # type: ignore

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TITLE, NOTE_TEXT, NOTE_SLUG = 'Some title', 'Some text', 'some_slug'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='user')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.url_add = reverse('notes:add')
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG
        }

    def test_anonymous_cannot_add_note(self):
        """Аноним не может создать заметку"""
        self.client.post(self.url_add, data=self.form_data)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_can_add_note(self):
        """Юзер может создать заметку"""
        self.user_client.post(self.url_add, data=self.form_data)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.slug, self.NOTE_SLUG)
        self.assertEqual(note.author, self.user)

    def test_slug_duplicate_warning(self):
        """Невозможно создать 2 заметки с одинаковым слагом"""
        self.user_client.post(self.url_add, data=self.form_data)
        response = self.user_client.post(self.url_add, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=f'{self.NOTE_SLUG}{WARNING}'
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_auto_slug_creation(self):
        """Если не заполнен слаг, то он формируется автоматически"""
        self.form_data.pop('slug')
        self.user_client.post(self.url_add, self.form_data)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.slug, slugify(self.NOTE_TITLE))


class TestNoteEditDelete(TestCase):
    NOTE_TITLE, NOTE_TEXT, NOTE_SLUG = 'Some title', 'Some text', 'some_slug'
    EDITED_TITLE, EDITED_TEXT, EDITED_SLUG = 'Edited', 'New text', 'new_slug'

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create(username='user1')
        cls.user1_client = Client()
        cls.user1_client.force_login(cls.user1)
        cls.note1 = Note.objects.create(
            title=cls.NOTE_TITLE, text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG, author=cls.user1
        )
        cls.user2 = User.objects.create(username='user2')
        cls.user2_client = Client()
        cls.user2_client.force_login(cls.user2)
        cls.url_edit_note1 = reverse('notes:edit', args=(cls.note1.slug,))
        cls.url_delete_note1 = reverse('notes:delete', args=(cls.note1.slug,))
        cls.url_success = reverse('notes:success')
        cls.form_data = {
            'title': cls.EDITED_TITLE,
            'text': cls.EDITED_TEXT,
            'slug': cls.EDITED_SLUG,
        }

    def test_user_can_delete_own_note(self):
        """Юзер может удалить свою заметку"""
        response = self.user1_client.delete(self.url_delete_note1)
        self.assertRedirects(response, self.url_success)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_cannot_delete_others_note(self):
        """Юзер не может удалить чужую заметку"""
        response = self.user2_client.delete(self.url_delete_note1)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def test_user_can_edit_own_note(self):
        """Юзер может редактировать свою заметку"""
        response = self.user1_client.post(self.url_edit_note1, self.form_data)
        self.assertRedirects(response, self.url_success)
        self.note1.refresh_from_db()
        self.assertEqual(self.note1.title, self.EDITED_TITLE)
        self.assertEqual(self.note1.text, self.EDITED_TEXT)
        self.assertEqual(self.note1.slug, self.EDITED_SLUG)

    def test_user_cannot_edit_others_note(self):
        """Юзер не может редактировать чужую заметку"""
        response = self.user2_client.post(self.url_edit_note1, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note1.refresh_from_db()
        self.assertEqual(self.note1.title, self.NOTE_TITLE)
        self.assertEqual(self.note1.text, self.NOTE_TEXT)
        self.assertEqual(self.note1.slug, self.NOTE_SLUG)
