from notes.forms import NoteForm
from .common_test import BaseTestContent


class TestContent(BaseTestContent):

    def test_note_in_list_for_author(self):
        response = self.client.get(self.NOTE_LIST_URL)
        self.assertIn('object_list', response.context,
                     msg="Ключ 'object_list' отсутствует в контексте ответа")
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)
        note_from_context = object_list.get(id=self.note.id)
        self.assertEqual(note_from_context.title, self.note.title)
        self.assertEqual(note_from_context.text, self.note.text)
        self.assertEqual(note_from_context.slug, self.note.slug)
        self.assertEqual(note_from_context.author, self.note.author)

    def test_note_not_in_list_for_another_user(self):
        self.login_reader()
        response = self.client.get(self.NOTE_LIST_URL)
        self.assertIn('object_list', response.context,
                     msg="Ключ 'object_list' отсутствует в контексте ответа")
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)
        self.assertFalse(object_list.filter(id=self.note.id).exists())

    def test_create_page_contains_form(self):
        response = self.client.get(self.get_add_url())
        self.assertIn('form', response.context,
                     msg="Ключ 'form' отсутствует в контексте ответа")
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_edit_page_contains_form(self):
        response = self.client.get(self.get_edit_url(self.note.slug))
        self.assertIn('form', response.context,
                     msg="Ключ 'form' отсутствует в контексте ответа")
        form = response.context['form']
        self.assertIsInstance(form, NoteForm)
        self.assertEqual(form.instance, self.note)
        self.assertEqual(form.initial.get('title'), self.note.title)
        self.assertEqual(form.initial.get('text'), self.note.text)
        self.assertEqual(form.initial.get('slug'), self.note.slug)