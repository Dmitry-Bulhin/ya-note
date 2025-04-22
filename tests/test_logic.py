from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from pytils.translit import slugify

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class NoteCreationTest(TestCase):
    """Тестирование создания заметок."""

    @classmethod
    def setUpTestData(cls):
        # Создаем двух пользователей
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        # Данные для заметки
        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Текст заметки',
            'slug': 'note-slug'
        }

    def test_anonymous_user_cant_create_note(self):
        """Проверяем, что анонимный пользователь не может создать заметку."""
        notes_count = Note.objects.count()
        self.client.post(reverse('notes:add'), data=self.form_data)
        self.assertEqual(Note.objects.count(), notes_count)

    def test_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку."""
        self.client.force_login(self.author)
        response = self.client.post(reverse('notes:add'), data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)


class NoteEditDeleteTest(TestCase):
    """Тестирование редактирования и удаления заметок."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )
        # Данные для изменения заметки
        cls.edit_data = {
            'title': 'Новый заголовок',
            'text': 'Обновленный текст',
            'slug': 'new-slug'
        }

    def test_author_can_edit_note(self):
        """Автор может редактировать свою заметку."""
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.post(url, self.edit_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.edit_data['title'])
        self.assertEqual(self.note.text, self.edit_data['text'])
        self.assertEqual(self.note.slug, self.edit_data['slug'])

    def test_other_user_cant_edit_note(self):
        """Пользователь не может редактировать чужую заметку."""
        self.client.force_login(self.reader)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.post(url, self.edit_data)
        self.assertEqual(response.status_code, 404)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку."""
        self.client.force_login(self.author)
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        """Пользователь не может удалить чужую заметку."""
        self.client.force_login(self.reader)
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Note.objects.count(), 1)


class NoteSlugTest(TestCase):
    """Тестирование slug заметок."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Пользователь')
        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Текст заметки',
            'slug': ''
        }

    def test_empty_slug(self):
        """Проверка автоматического создания slug."""
        self.client.force_login(self.user)
        self.client.post(reverse('notes:add'), data=self.form_data)
        note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])[:100]
        self.assertEqual(note.slug, expected_slug)

    def test_not_unique_slug(self):
        """Проверка на уникальность slug."""
        self.client.force_login(self.user)
        # Создаем первую заметку
        self.client.post(reverse('notes:add'), data=self.form_data)
        # Пытаемся создать вторую заметку с таким же title (и slug)
        response = self.client.post(reverse('notes:add'), data=self.form_data)
        # 1. Новая заметка не создалась (осталась одна)
        self.assertEqual(Note.objects.count(), 1)
        # 2. В ответе есть сообщение об ошибке
        expected_slug = slugify(self.form_data['title'])[:100]
        warning_message = expected_slug + ' - такой slug уже существует, придумайте уникальное значение!'
        self.assertContains(response, warning_message)
