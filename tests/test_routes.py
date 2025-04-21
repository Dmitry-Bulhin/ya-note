from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):

        # cls.user = User.objects.create_user(
        #     username='test_user',
        #     password='testpass123'
        # )

        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
            slug="test-slug",
        )

    def test_home_page(self):
        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_detail_page(self):
        urls = (
            ('notes:home', None),
            ('notes:detail', (self.note.slug,)),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )

        self.client.force_login(self.author)
        # Итерируемся по внешнему кортежу 
        # и распаковываем содержимое вложенных кортежей:
        for name, args in urls:
            with self.subTest(name=name):
                # Передаём имя и позиционный аргумент в reverse()
                # и получаем адрес страницы для GET-запроса:
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            # Логиним пользователя в клиенте:
            self.client.force_login(user)
            # Для каждой пары "пользователь - ожидаемый ответ"
            # перебираем имена тестируемых страниц:
            for name in ('notes:edit', 'notes:delete'):  
                with self.subTest(user=user, name=name):        
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        # Сохраняем адрес страницы логина:
        login_url = reverse('users:login')
        # В цикле перебираем имена страниц, с которых ожидаем редирект:
        for name in ('notes:edit', 'notes:delete'):
            with self.subTest(name=name):
                # Получаем адрес страницы редактирования или удаления комментария:
                url = reverse(name, args=(self.note.slug,))
                # Получаем ожидаемый адрес страницы логина, 
                # на который будет перенаправлен пользователь.
                # Учитываем, что в адресе будет параметр next, в котором передаётся
                # адрес страницы, с которой пользователь был переадресован.
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                # Проверяем, что редирект приведёт именно на указанную ссылку.
                self.assertRedirects(response, redirect_url) 