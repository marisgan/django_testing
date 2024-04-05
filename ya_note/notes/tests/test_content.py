from notes.forms import NoteForm

from .settings import (
    ADD_URL, BaseSetup, EDIT_URL, LIST_URL,
)


class TestContent(BaseSetup):

    def test_own_note_on_list_page(self):
        """Своя заметка передается на страницу списка заметок"""
        note_on_page = self.author_client.get(
            LIST_URL).context['object_list'].get(id=self.note.id)
        self.assertEqual(note_on_page.title, self.note.title)
        self.assertEqual(note_on_page.text, self.note.text)
        self.assertEqual(note_on_page.slug, self.note.slug)

    def test_others_note_not_on_list_page(self):
        """Чужая заметка не попадает на страницу списка заметок"""
        self.assertNotIn(
            self.note,
            self.user_client.get(LIST_URL).context['object_list']
        )

    def test_add_and_edit_note_pages_contain_form(self):
        """Форма передается на страницы создания и редактирования заметки"""
        for url in (ADD_URL, EDIT_URL):
            with self.subTest(url=url):
                self.assertIsInstance(
                    self.author_client.get(url).context.get('form', None),
                    NoteForm
                )
