from notes.forms import NoteForm
from .common import CommonTestSetup


class TestContent(CommonTestSetup):

    def test_create_add_for_page_forms(self):
        """Тест проверяет, содержат ли add и edit форму в контексте"""
        urls = (
            self.add_url,
            self.edit_url
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)

    def test_notes_list_for_author(self):
        """Тест проверяет, может ли автор видеть свои заметки в виде списка"""
        response = self.author_client.get(self.list_url)
        notes = response.context['object_list']
        self.assertIn(self.note, notes)

    def test_notes_list_for_anon(self):
        """
        Тест проверяет,
        что пользователь не может видеть заметки другого пользователя
        """
        response = self.reader_client.get(self.list_url)
        notes = response.context['object_list']
        self.assertNotIn(self.note, notes)
