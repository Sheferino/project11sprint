from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    URL_HOME = reverse('notes:home')
    URL_LOGIN = reverse('users:login')
    URL_LOGOUT = reverse('users:logout')
    URL_SIGNUP = reverse('users:signup')
    URL_NOTES_LIST = reverse('notes:list')
    URL_ADD_NOTE = reverse('notes:add')
    URL_ADD_SUCCESS = reverse('notes:success')

    # фикстуры
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(title='Заголовок',
                                       text='Текст',
                                       slug='note-slug',
                                       author=cls.author)
        cls.notauthor = User.objects.create(username='Неавтор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.URL_NOTE_DETAIL = reverse(
            'notes:detail', kwargs={'slug': cls.note.slug})
        cls.URL_NOTE_EDIT = reverse(
            'notes:edit', kwargs={'slug': cls.note.slug})
        cls.URL_NOTE_DELETE = reverse(
            'notes:delete', kwargs={'slug': cls.note.slug})

    # доступность заглавной, логина, логаута и регистрации для анонима
    def test_home_page(self):
        urls = (
            self.URL_HOME,
            self.URL_LOGIN,
            self.URL_LOGOUT,
            self.URL_SIGNUP,
        )
        for url in urls:
            with self.subTest(name=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    # доступность списка, добавления, успеха для залогиненого
    def test_user_routes(self):
        urls = (
            self.URL_NOTES_LIST,
            self.URL_ADD_NOTE,
            self.URL_ADD_SUCCESS,
        )
        for url in urls:
            with self.subTest(name=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    # доступность заметки, удаления, редактирования для автора
    def test_author_routes(self):
        urls = (
            self.URL_NOTE_DETAIL,
            self.URL_NOTE_EDIT,
            self.URL_NOTE_DELETE,
        )
        for url in urls:
            with self.subTest(name=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    # недоступность заметки, удаления, редактирования для неавтора
    def test_notauthor_routes(self):
        urls = (
            self.URL_NOTE_DETAIL,
            self.URL_NOTE_EDIT,
            self.URL_NOTE_DELETE,
        )
        self.client.force_login(self.notauthor)
        for url in urls:
            with self.subTest(name=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    # редирект анонима на логин при любых действиях
    def test_redirect_for_anonymous(self):
        urls = (
            self.URL_NOTES_LIST,
            self.URL_ADD_NOTE,
            self.URL_ADD_SUCCESS,
            self.URL_NOTE_DETAIL,
            self.URL_NOTE_EDIT,
            self.URL_NOTE_DELETE,
        )
        # В цикле перебираем имена страниц, с которых ожидаем редирект:
        for url in urls:
            with self.subTest(name=url):
                # Получаем ожидаемый адрес страницы логина
                redirect_url = f'{self.URL_LOGIN}?next={url}'
                response = self.client.get(url)
                # Проверяем, что редирект приведёт именно на указанную ссылку.
                self.assertRedirects(response, redirect_url)
