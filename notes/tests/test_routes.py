from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    # фикстуры
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(title='Заголовок',
                                       text='Текст',
                                       slug='note-slug',
                                       author=cls.author)
        cls.notauthor = User.objects.create(username='Неавтор')

    # доступность заглавной, логина, логаута и регистрации для анонима
    def test_home_page(self):
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for url_name in urls:
            with self.subTest(name=url_name):
                url = reverse(url_name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    # доступность списка, добавления, успеха для залогиненого
    def test_user_routes(self):
        urls = (
            'notes:list',
            'notes:add',
            'notes:success',
        )
        self.client.force_login(self.author)
        for url_name in urls:
            with self.subTest(name=url_name):
                url = reverse(url_name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    # доступность заметки, удаления, редактирования для автора
    def test_author_routes(self):
        urls_args = (
            'notes:detail',
            'notes:edit',
            'notes:delete',
        )
        self.client.force_login(self.author)
        for url_name in urls_args:
            with self.subTest(name=url_name):
                url = reverse(url_name, kwargs={'slug': self.note.slug})
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    # недоступность заметки, удаления, редактирования для неавтора
    def test_notauthor_routes(self):
        urls_args = (
            'notes:detail',
            'notes:edit',
            'notes:delete',
        )
        self.client.force_login(self.notauthor)
        for url_name in urls_args:
            with self.subTest(name=url_name):
                url = reverse(url_name, kwargs={'slug': self.note.slug})
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    # редирект анонима на логин при любых действиях
    def test_redirect_for_anonymous(self):
        # Ожидаемый адрес страницы логина
        login_url = reverse('users:login')
        urls_args = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:detail', {'slug': self.note.slug}),
            ('notes:edit', {'slug': self.note.slug}),
            ('notes:delete', {'slug': self.note.slug}),
        )
        # В цикле перебираем имена страниц, с которых ожидаем редирект:
        for urlname, kwargs in urls_args:
            with self.subTest(name=urlname):
                url = reverse(urlname, kwargs=kwargs)
                # Получаем ожидаемый адрес страницы логина
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                # Проверяем, что редирект приведёт именно на указанную ссылку.
                self.assertRedirects(response, redirect_url)
