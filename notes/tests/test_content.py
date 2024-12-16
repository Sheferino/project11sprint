# тестирование контента
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestContent(TestCase):

    # создаём контент для проверок
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(title='Заголовок',
                                       text='Текст',
                                       slug='note-slug',
                                       author=cls.author)
        cls.notauthor = User.objects.create(username='Неавтор')

    # заметка автора на странице со списком заметок в списке object_list
    # неавтор её не увидит
    def test_notes_list(self):
        url_name = 'notes:list'
        users = (self.author, self.notauthor)
        expected_results = (True, False)
        for user, expected_result in zip(users, expected_results):
            with self.subTest(name=url_name):
                url = reverse(url_name)
                # Выполняем запрос
                self.client.force_login(user)
                response = self.client.get(url)
                object_list = response.context['object_list']
                # Проверяем истинность утверждения "заметка есть в списке":
                self.assertEqual(self.note in object_list, expected_result)

    def test_pages_contains_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', {'slug': self.note.slug})
        )
        for url_name, kwargs in urls:
            url = reverse(url_name, kwargs=kwargs)
            # Запрашиваем нужную страницу:
            self.client.force_login(self.author)
            response = self.client.get(url)
            # Проверяем, есть ли объект формы в словаре контекста:
            assert 'form' in response.context
            # Проверяем, что объект формы относится к нужному классу.
            assert isinstance(response.context['form'], NoteForm)
