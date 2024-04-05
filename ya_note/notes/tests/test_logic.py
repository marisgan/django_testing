from http import HTTPStatus

from pytils.translit import slugify

from .settings import (
    ADD_URL, BaseSetup, DELETE_URL, DELETE_URL, EDIT_URL,
    FORM_DATA, NOTE_SLUG, SUCCESS_URL,
)
from notes.forms import WARNING
from notes.models import Note


class TestLogic(BaseSetup):

    def count_notes(self):
        return Note.objects.count()

    def test_anonym_cannot_add_note(self):
        """Аноним не может создать заметку"""
        count_before_test = self.count_notes()
        self.client.post(ADD_URL, data=FORM_DATA)
        self.assertEqual(self.count_notes(), count_before_test)

    def add_note_successfully(self):
        count_before_test = self.count_notes()
        self.author_client.post(ADD_URL, FORM_DATA)
        self.assertEqual(self.count_notes(), count_before_test + 1)

    def test_author_can_add_note(self):
        """Юзер может создать заметку"""
        self.add_note_successfully()
        new_note = Note.objects.get(slug=FORM_DATA['slug'])
        self.assertEqual(new_note.title, FORM_DATA['title'])
        self.assertEqual(new_note.text, FORM_DATA['text'])
        self.assertEqual(new_note.slug, FORM_DATA['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_slug_duplicate_warning(self):
        """Невозможно создать заметку с неуникальным слагом"""
        count_before_test = self.count_notes()
        FORM_DATA['slug'] = NOTE_SLUG
        self.assertFormError(
            self.author_client.post(ADD_URL, data=FORM_DATA),
            form='form',
            field='slug',
            errors=f'{NOTE_SLUG}{WARNING}'
        )
        self.assertEqual(self.count_notes(), count_before_test)

    def test_auto_slug_creation(self):
        """Если не заполнен слаг, то он формируется автоматически"""
        FORM_DATA.pop('slug')
        self.add_note_successfully()
        new_note = Note.objects.get(slug=slugify(FORM_DATA['title']))
        self.assertEqual(new_note.slug, slugify(FORM_DATA['title']))
        self.assertEqual(new_note.title, FORM_DATA['title'])
        self.assertEqual(new_note.text, FORM_DATA['text'])
        self.assertEqual(new_note.author, self.author)

    def test_user_can_delete_own_note(self):
        """Юзер может удалить свою заметку"""
        count_before_test = self.count_notes()
        self.assertRedirects(
            self.author_client.delete(DELETE_URL),
            SUCCESS_URL
        )
        self.assertEqual(self.count_notes(), count_before_test - 1)

    def test_user_cannot_delete_others_note(self):
        """Юзер не может удалить чужую заметку"""
        count_before_test = self.count_notes()
        self.assertEqual(
            self.user_client.delete(DELETE_URL).status_code,
            HTTPStatus.NOT_FOUND)
        self.assertEqual(self.count_notes(), count_before_test)
        note_to_check = Note.objects.get(id=self.note.id)
        self.assertEqual(note_to_check.title, self.note.title)
        self.assertEqual(note_to_check.text, self.note.text)
        self.assertEqual(note_to_check.slug, self.note.slug)
        self.assertEqual(note_to_check.author, self.note.author)

    def test_user_can_edit_own_note(self):
        """Юзер может редактировать свою заметку"""
        self.assertRedirects(
            self.author_client.post(EDIT_URL, FORM_DATA),
            SUCCESS_URL)
        edited_note = Note.objects.get(id=self.note.id)
        self.assertEqual(edited_note.title, FORM_DATA['title'])
        self.assertEqual(edited_note.text, FORM_DATA['text'])
        self.assertEqual(edited_note.slug, FORM_DATA['slug'])
        self.assertEqual(edited_note.author, self.author)

    def test_user_cannot_edit_others_note(self):
        """Юзер не может редактировать чужую заметку"""
        self.assertEqual(
            self.user_client.post(EDIT_URL, FORM_DATA).status_code,
            HTTPStatus.NOT_FOUND
        )
        note_to_check = Note.objects.get(id=self.note.id)
        self.assertEqual(note_to_check.title, self.note.title)
        self.assertEqual(note_to_check.text, self.note.text)
        self.assertEqual(note_to_check.slug, self.note.slug)
        self.assertEqual(note_to_check.author, self.note.author)
