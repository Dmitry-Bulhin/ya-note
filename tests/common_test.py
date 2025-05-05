# tests/common_test.py
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase
from notes.models import Note


class BaseTestContent(TestCase):
    NOTE_LIST_URL = reverse('notes:list')
    ADD_URL = reverse('notes:add')
    
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
            slug='test-slug'
        )
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def setUp(self):
        self.client.force_login(self.author)
    
    def get_edit_url(self, slug):
        return reverse('notes:edit', args=(slug,))
    
    def get_delete_url(self, slug):
        return reverse('notes:delete', args=(slug,))
    
    def login_author(self):
        self.client.force_login(self.author)
    
    def login_reader(self):
        self.client.force_login(self.reader)