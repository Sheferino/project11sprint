from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestNotesLogic(TestCase):

    # создаём контент для проверок
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        # отдельно словарь для сохранения исходных параметров
        cls.note_data = {
            'title': 'Заголовок',
            'text': 'Текст',
            'slug': 'note-slug',
            'author': cls.author
        }
        cls.note = Note.objects.create(**cls.note_data)
        cls.form_data = {
            'title': 'Заголовок из формы',
            'text': 'Текст из формы',
            'slug': 'slug-from-form'
        }
        # просто пользователь и его клиент
        cls.user = User.objects.create(username='Пользователь')
        cls.simple_auth_client = Client()
        cls.simple_auth_client.force_login(cls.user)

    # пользователь может создать заметку
    def test_user_creation_note(self):
        # определяем начальное количество заметок
        notes_count = Note.objects.count()
        url = reverse('notes:add')
        # запрос от пользователя
        response = self.simple_auth_client.post(url, data=self.form_data)
        # Проверяем, что был выполнен редирект
        self.assertRedirects(response, reverse('notes:success'))
        # проверяем, что количество заметок увеличилось
        assert Note.objects.count() == notes_count + 1
        # Чтобы проверить значения полей заметки -
        # получаем её из базы при помощи метода get():
        new_note = Note.objects.get(slug=self.form_data['slug'])
        # Сверяем атрибуты объекта с ожидаемыми.
        assert new_note.title == self.form_data['title']
        assert new_note.text == self.form_data['text']
        assert new_note.slug == self.form_data['slug']
        assert new_note.author == self.user

    # аноним не может создать заметку
    def test_anonymous_creation_note(self):
        # определяем начальное количество заметок
        notes_count = Note.objects.count()
        url = reverse('notes:add')
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={url}'
        # запрос от анонима
        response = self.client.post(url, data=self.form_data)
        # Проверяем, что был выполнен редирект на логин
        self.assertRedirects(response, redirect_url)
        # проверяем, что количество заметок не увеличилось
        assert Note.objects.count() == notes_count

    # невозможно создать две заметки с одинаковым slug
    def test_not_unique_slug(self):
        # определяем начальное количество заметок
        notes_count = Note.objects.count()
        url = reverse('notes:add')
        # Подменяем slug новой заметки на slug уже существующей записи:
        self.form_data['slug'] = self.note.slug
        # Пытаемся создать новую заметку:
        response = self.simple_auth_client.post(url, data=self.form_data)
        # Проверяем, что в ответе содержится ошибка формы для поля slug:
        self.assertFormError(response, 'form', 'slug',
                             errors=(self.form_data['slug'] + WARNING))
        # Убеждаемся, что количество заметок в базе не увеличилось
        assert Note.objects.count() == notes_count

    # slug формируется автоматически
    def test_slugify_empty_slug(self):
        # определяем начальное количество заметок
        notes_count = Note.objects.count()
        url = reverse('notes:add')
        # Убираем поле slug из словаря формы
        self.form_data.pop('slug')
        response = self.simple_auth_client.post(url, data=self.form_data)
        # Проверяем, что даже без slug заметка была создана
        self.assertRedirects(response, reverse('notes:success'))
        # проверяем, что количество заметок увеличилось
        assert Note.objects.count() == notes_count + 1
        # Формируем ожидаемый slug:
        expected_slug = slugify(self.form_data['title'])
        # убеждаемся, что заметка с таким slug создана
        self.assertIsInstance(Note.objects.get(slug=expected_slug), Note)

    # автор может редактировать заметку
    def test_author_can_edit_note(self):
        # Получаем адрес страницы редактирования заметки:
        url = reverse('notes:edit', args=(self.note.slug,))
        # В POST-запросе на адрес редактирования заметки
        # отправляем form_data - новые значения для полей заметки:
        self.client.force_login(self.author)
        response = self.client.post(url, data=self.form_data)
        # Проверяем редирект:
        self.assertRedirects(response, reverse('notes:success'))
        # Обновляем объект заметки note: получаем обновлённые данные из БД:
        self.note.refresh_from_db()
        # Проверяем, что атрибуты заметки соответствуют обновлённым:
        for attr_name in ['title', 'text', 'slug']:
            self.assertEqual(getattr(self.note, attr_name),
                             self.form_data.get(attr_name))

    # автор может удалить заметку
    def test_author_can_delete_note(self):
        # Получаем адрес страницы редактирования заметки:
        url = reverse('notes:delete', args=(self.note.slug,))
        self.client.force_login(self.author)
        response = self.client.post(url)
        # Проверяем редирект:
        self.assertRedirects(response, reverse('notes:success'))
        # убеждаемся, что такой заметки больше нет
        with self.assertRaises(ObjectDoesNotExist, msg='Заметки больше нет'):
            Note.objects.get(pk=self.note.pk)

    # посторонний не может редактировать заметку, она остаётся прежней
    def test_notauthor_cant_edit_note(self):
        # Получаем адрес страницы редактирования заметки:
        url = reverse('notes:edit', args=(self.note.slug,))
        # В POST-запросе на адрес редактирования заметки
        # отправляем form_data - новые значения для полей заметки:
        self.simple_auth_client.post(url, data=self.form_data)
        # Обновляем объект заметки note: получаем обновлённые данные из БД:
        self.note.refresh_from_db()
        # Проверяем, что атрибуты заметки остались прежние
        for attr_name in ['title', 'text', 'slug']:
            self.assertEqual(getattr(self.note, attr_name),
                             self.note_data.get(attr_name))

    # посторонний не может удалить заметку
    def test_notauthor_cant_delete_note(self):
        # Получаем адрес страницы редактирования заметки:
        url = reverse('notes:delete', args=(self.note.slug,))
        self.client.post(url)
        # Обновляем объект заметки note. Заодно убеждаемся, что она не удалена
        self.note.refresh_from_db()
        # Проверяем, что атрибуты заметки остались прежние
        for attr_name in ['title', 'text', 'slug']:
            self.assertEqual(getattr(self.note, attr_name),
                             self.note_data.get(attr_name))
