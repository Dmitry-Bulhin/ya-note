# tests/test_logic.py
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from notes.models import Note
from pytils.translit import slugify

from .common_test import BaseTestContent


class NoteCreationTest(BaseTestContent):

    def test_anonymous_user_cant_create_note(self):
        notes_count = Note.objects.count()
        self.client.logout()
        self.client.post(self.ADD_URL, data=self.form_data)
        self.assertEqual(Note.objects.count(), notes_count)

    def test_user_can_create_note(self):
        required_fields = ['title', 'text', 'slug']
        for field in required_fields:
            with self.subTest(field=field):
                self.assertIn(field, self.form_data)
        existing_note_ids = set(Note.objects.values_list('id', flat=True))
        response = self.client.post(self.ADD_URL, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        new_notes = Note.objects.exclude(id__in=existing_note_ids)
        self.assertEqual(new_notes.count(), 1)
        new_note = new_notes.first()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)


class NoteEditDeleteTest(BaseTestContent):

    def test_author_can_edit_note(self):
        url = self.get_edit_url(self.note.slug)
        original_id = self.note.id
        original_author = self.note.author
        initial_count = Note.objects.count()
        response = self.client.post(url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), initial_count)
        updated_note = Note.objects.get(pk=original_id)
        self.assertEqual(updated_note.title, self.form_data['title'])
        self.assertEqual(updated_note.text, self.form_data['text'])
        self.assertEqual(updated_note.slug, self.form_data['slug'])
        self.assertEqual(updated_note.author, original_author)

    def test_other_user_cant_edit_note(self):
        self.login_reader()
        url = self.get_edit_url(self.note.slug)
        response = self.client.post(url, self.form_data)
        self.assertEqual(response.status_code, 404)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        url = self.get_delete_url(self.note.slug)
        response = self.client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        self.login_reader()
        url = self.get_delete_url(self.note.slug)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Note.objects.count(), 1)


class NoteSlugTest(BaseTestContent):

    def test_empty_slug(self):
        form_data = {
            'title': 'Заголовок для пустого slug',
            'text': 'Текст заметки',
            'slug': ''
        }
        self.client.post(self.ADD_URL, data=form_data)
        note = Note.objects.get(title=form_data['title'])
        expected_slug = slugify(form_data['title'])[:100]
        self.assertEqual(note.slug, expected_slug)

    def test_not_unique_slug(self):
        # Используем slug из существующей заметки
        form_data = {
            'title': 'Заголовок',
            'text': 'Текст заметки',
            'slug': self.note.slug
        }
        response = self.client.post(self.ADD_URL, data=form_data)
        self.assertEqual(Note.objects.count(), 1)
        warning_message = (
            f'{self.note.slug} - такой slug уже существует, '
            'придумайте уникальное значение!'
        )
        self.assertContains(response, warning_message)