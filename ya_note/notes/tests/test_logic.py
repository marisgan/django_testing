from pytils.translit import slugify

from .fixture_constants import (
    ADD_URL, BaseFixtures, DELETE_URL, DELETE_URL, EDIT_URL,
    FORM_DATA, SUCCESS_URL,
)
from notes.forms import WARNING
from notes.models import Note


class TestLogic(BaseFixtures):

    def test_anonym_cannot_add_note(self):
        """Аноним не может создать заметку"""
        notes = set(Note.objects.all())
        self.client.post(ADD_URL, data=FORM_DATA)
        self.assertEqual(set(Note.objects.all()), notes)

    def add_note_successfully(self, form_data, expected_slug):
        notes = set(Note.objects.all())
        self.author_client.post(ADD_URL, form_data)
        notes = set(Note.objects.all()) - notes
        self.assertEqual(len(notes), 1)
        note = notes.pop()
        self.assertEqual(note.title, form_data['title'])
        self.assertEqual(note.text, form_data['text'])
        self.assertEqual(note.slug, expected_slug)
        self.assertEqual(note.author, self.author)

    def test_author_can_add_note(self):
        """Юзер может создать заметку"""
        self.add_note_successfully(FORM_DATA, FORM_DATA['slug'])

    def test_auto_slug_creation(self):
        """Если нет слага, то он формируется автоматически"""
        self.add_note_successfully(
            {'title': FORM_DATA['title'], 'text': FORM_DATA['text']},
            slugify(FORM_DATA['title'])
        )

    def test_slug_duplicate_warning(self):
        """Невозможно создать заметку с неуникальным слагом"""
        notes = set(Note.objects.all())
        data_slug_dublicate = {
            'title': FORM_DATA['title'], 'text': FORM_DATA['text'],
            'slug': self.note.slug
        }
        self.assertFormError(
            self.author_client.post(ADD_URL, data=data_slug_dublicate),
            form='form',
            field='slug',
            errors=data_slug_dublicate['slug'] + WARNING
        )
        self.assertEqual(set(Note.objects.all()), notes)

    def test_user_can_delete_own_note(self):
        """Юзер может удалить свою заметку"""
        notes_count = Note.objects.count()
        self.assertRedirects(
            self.author_client.delete(DELETE_URL),
            SUCCESS_URL
        )
        self.assertEqual(Note.objects.count(), notes_count - 1)
        self.assertEqual(Note.objects.filter(id=self.note.id).exists(), False)

    def test_user_cannot_delete_others_note(self):
        """Юзер не может удалить чужую заметку"""
        notes = set(Note.objects.all())
        self.user_client.delete(DELETE_URL)
        self.assertEqual(set(Note.objects.all()), notes)
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.note.author)

    def test_user_can_edit_own_note(self):
        """Юзер может редактировать свою заметку"""
        self.assertRedirects(
            self.author_client.post(EDIT_URL, FORM_DATA),
            SUCCESS_URL)
        edited_note = Note.objects.get(id=self.note.id)
        self.assertEqual(edited_note.title, FORM_DATA['title'])
        self.assertEqual(edited_note.text, FORM_DATA['text'])
        self.assertEqual(edited_note.slug, FORM_DATA['slug'])
        self.assertEqual(edited_note.author, self.note.author)

    def test_user_cannot_edit_others_note(self):
        """Юзер не может редактировать чужую заметку"""
        self.user_client.post(EDIT_URL, FORM_DATA)
        edited_note = Note.objects.get(id=self.note.id)
        self.assertEqual(edited_note.title, self.note.title)
        self.assertEqual(edited_note.text, self.note.text)
        self.assertEqual(edited_note.slug, self.note.slug)
        self.assertEqual(edited_note.author, self.note.author)
