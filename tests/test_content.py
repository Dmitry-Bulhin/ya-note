from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

class TestHomePage(TestCase):
    LIST_URL = reverse('notes:list')
    NOTES_COUNT = 5  # Выносим количество заметок в константу класса

    @classmethod
    def setUpTestData(cls):
        # Создаём тестового пользователя
        cls.author = get_user_model().objects.create(username='testuser')

        # Создаём заметки с уникальными slug
        all_notes = [
            Note(
                title=f'Заметка {index}',
                text=f'Текст заметки {index}',
                author=cls.author,
                slug=f'test-note-{index}'
            )
            for index in range(cls.NOTES_COUNT)  # Используем константу
        ]
        Note.objects.bulk_create(all_notes)

    def test_notes_count(self):
        # Авторизуем пользователя
        self.client.force_login(self.author)

        # Проверяем количество заметок
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertEqual(object_list.count(), self.NOTES_COUNT)  # Используем константу

    def test_notes_ordered_by_id_asc(self):
        """Проверяем, что заметки упорядочены по возрастанию id."""
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list = list(response.context['object_list'])
        
        # Получаем список id в том порядке, как они пришли из view
        note_ids = [note.id for note in object_list]
        
        # Проверяем, что id идут по возрастанию
        self.assertEqual(note_ids, sorted(note_ids))

    def test_all_created_notes_are_displayed(self):
        """Проверяем, что все созданные заметки отображаются."""
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        displayed_notes = set(note.id for note in response.context['object_list'])
        created_notes = set(Note.objects.filter(author=self.author).values_list('id', flat=True))
        
        # Проверяем, что все созданные заметки отображены
        self.assertEqual(displayed_notes, created_notes)

    def test_note_links_are_correct(self):
        """Проверяем, что ссылки на детальные страницы корректны."""
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        
        for note in response.context['object_list']:
            # Проверяем, что ссылка содержит правильный slug
            expected_url = reverse('notes:detail', kwargs={'slug': note.slug})
            self.assertContains(response, expected_url)
            
            # Проверяем, что заголовок заметки присутствует в ссылке
            self.assertContains(response, note.title)