from http import HTTPStatus

from pytils.translit import slugify

from .fixture_constants import (
    ADD_URL, BaseSetup, DELETE_URL, DELETE_URL, EDIT_URL,
    FORM_DATA, NOTE_SLUG, SUCCESS_URL,
)
from notes.forms import WARNING
from notes.models import Note

class TestLogic(BaseSetup):

    def test_anonym_cannot_add_note(self):
        """Аноним не может создать заметку"""
        notes_before = list(Note.objects.all())
        self.client.post(ADD_URL, data=FORM_DATA)
        self.assertEqual(list(Note.objects.all()), notes_before)

    def add_note_successfully(self, form_data):
        notes_before = set(Note.objects.all())
        self.author_client.post(ADD_URL, form_data)
        notes_after = set(Note.objects.all())
        new_notes = notes_after.difference(notes_before)
        self.assertEqual(len(new_notes), 1)
        new_note = new_notes.pop()
        self.assertEqual(new_note.title, form_data['title'])
        self.assertEqual(new_note.text, form_data['text'])
        self.assertEqual(
            new_note.slug,
            form_data.get('slug', slugify(form_data['title']))
        )
        self.assertEqual(new_note.author, self.author)

    def test_author_can_add_note(self):
        """Юзер может создать заметку"""
        self.add_note_successfully(FORM_DATA)

    def test_auto_slug_creation(self):
        """Если нет слага, то он формируется автоматически"""
        self.add_note_successfully(
            {'title': FORM_DATA['title'], 'text': FORM_DATA['text']}
        )

    def test_slug_duplicate_warning(self):
        """Невозможно создать заметку с неуникальным слагом"""
        notes_before = list(Note.objects.all())
        data_slug_dublicate = {
            'title': FORM_DATA['title'], 'text': FORM_DATA['text'],
            'slug': self.note.slug
        }
        self.assertFormError(
            self.author_client.post(ADD_URL, data=data_slug_dublicate),
            form='form',
            field='slug',
            errors=f'{self.note.slug}{WARNING}'
        )
        self.assertEqual(list(Note.objects.all()), notes_before)

    def test_user_can_delete_own_note(self):
        """Юзер может удалить свою заметку"""
        notes_before = set(Note.objects.all())
        original_note = self.note
        self.assertRedirects(
            self.author_client.delete(DELETE_URL),
            SUCCESS_URL
        )
        notes_after = set(Note.objects.all())
        deleted_notes = notes_before.difference(notes_after)
        self.assertEqual(len(deleted_notes), 1)
        deleted_note = deleted_notes.pop()
        self.assertEqual(deleted_note.title, original_note.title)
        self.assertEqual(deleted_note.text, original_note.text)
        self.assertEqual(deleted_note.slug, original_note.slug)
        self.assertEqual(deleted_note.author, original_note.author)

    def test_user_cannot_delete_others_note(self):
        """Юзер не может удалить чужую заметку"""
        notes_before = list(Note.objects.all())
        original_note = self.note
        self.user_client.delete(DELETE_URL)
        self.assertEqual(list(Note.objects.all()), notes_before)
        note = Note.objects.get(id=original_note.id)
        self.assertEqual(note.title, original_note.title)
        self.assertEqual(note.text, original_note.text)
        self.assertEqual(note.slug, original_note.slug)
        self.assertEqual(note.author, original_note.author)

    def test_user_can_edit_own_note(self):
        """Юзер может редактировать свою заметку"""
        original_note = self.note
        self.assertRedirects(
            self.author_client.post(EDIT_URL, FORM_DATA),
            SUCCESS_URL)
        edited_note = Note.objects.get(id=original_note.id)
        self.assertEqual(edited_note.title, FORM_DATA['title'])
        self.assertEqual(edited_note.text, FORM_DATA['text'])
        self.assertEqual(edited_note.slug, FORM_DATA['slug'])
        self.assertEqual(edited_note.author, original_note.author)

    def test_user_cannot_edit_others_note(self):
        """Юзер не может редактировать чужую заметку"""
        original_note = self.note
        self.user_client.post(EDIT_URL, FORM_DATA)
        edited_note = Note.objects.get(id=original_note.id)
        self.assertEqual(edited_note.title, original_note.title)
        self.assertEqual(edited_note.text, original_note.text)
        self.assertEqual(edited_note.slug, original_note.slug)
        self.assertEqual(edited_note.author, original_note.author)
