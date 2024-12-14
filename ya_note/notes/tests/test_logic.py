from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()
URL_TO_DONE = reverse('notes:success')
URL_TO_ADD = reverse('notes:add')


class TestNoteCreation(TestCase):
    NOTE_TEXT = 'Текст заметки'
    NOTE_TITLE = 'Текст заголовка'
    NOTE_SLUG = 'slug'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Денис Зуев')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'text': cls.NOTE_TEXT,
            'title': cls.NOTE_TITLE,
            'slug': cls.NOTE_SLUG
        }

    def setUp(self):
        Note.objects.all().delete()

    def test_create_note(self):
        notes_count = Note.objects.count()
        response = self.auth_client.post(
            URL_TO_ADD,
            data=self.form_data
        )
        self.assertRedirects(
            response,
            URL_TO_DONE
        )
        note_count = Note.objects.count()
        self.assertEqual(note_count, notes_count + 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.author, self.user)

    def test_anon_cant_create_note(self):
        notes_count = Note.objects.count()
        self.client.post(URL_TO_ADD, data=self.form_data)
        note_count = Note.objects.count()
        self.assertEqual(note_count, notes_count)

    def test_empty_slug(self):
        self.form_data.pop('slug')
        notes_count = Note.objects.count()
        response = self.auth_client.post(
            URL_TO_ADD,
            data=self.form_data
        )
        self.assertRedirects(response, URL_TO_DONE)
        self.assertEqual(
            Note.objects.count(),
            notes_count + 1
        )
        new_note = Note.objects.get()
        slug_ex = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, slug_ex)


class TestEditDeleteNote(TestCase):
    NOTE_TITLE = 'Текст заголовка'
    NOTE_TEXT = 'Текст заметки'
    NOTE_SLUG = 'slug'
    NEW_NOTE_TEXT = 'Новая заметка'
    NEW_NOTE_TITLE = 'Новый заголовок заметки'
    NEW_NOTE_SLUG = 'new_slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Денис Зуев')
        cls.reader = User.objects.create(username='Читатель')
        cls.author_client = Client()
        cls.reader_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок',
            slug='Slug',
            author=cls.author,
            text=cls.NOTE_TEXT
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'text': cls.NEW_NOTE_TEXT,
            'title': cls.NEW_NOTE_TITLE,
            'slug': cls.NEW_NOTE_SLUG
        }

    def setUp(self):
        Note.objects.all().delete()
        self.note = Note.objects.create(
            title='Заголовок',
            slug='Slug',
            author=self.author,
            text=self.NOTE_TEXT
        )

    def test_auth_can_edit(self):
        response = self.author_client.post(
            self.edit_url,
            data=self.form_data
        )
        self.assertRedirects(response, URL_TO_DONE)
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.author)

    def test_auth_can_delete(self):
        notes_count = Note.objects.count()
        response = self.author_client.post(self.delete_url)
        self.assertRedirects(response, URL_TO_DONE)
        note_count = Note.objects.count()
        self.assertEqual(note_count, notes_count - 1)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.author)

    def test_user_cant_delete_note_of_another_user(self):
        notes_count_before = Note.objects.count()
        response = self.reader_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, notes_count_before)

    def test_not_unique_slug(self):
        self.form_data['slug'] = self.note.slug
        notes_count = Note.objects.count()
        response = self.author_client.post(
            URL_TO_ADD,
            data=self.form_data
        )
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), notes_count)
