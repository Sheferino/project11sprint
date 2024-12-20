# План тестирования (одинаковый для pytest и unittest)
## Будем тестировать:
### Пути:
* Главная страница доступна анонимному пользователю.
* Аутентифицированному пользователю доступна страница со списком заметок notes/,  страница успешного добавления заметки done/, страница добавления новой заметки add/.
* Страницы отдельной заметки, удаления и редактирования заметки доступны только автору заметки. Если на эти страницы попытается зайти другой пользователь — вернётся ошибка 404.
* При попытке перейти на страницу списка заметок, страницу успешного добавления записи, страницу добавления заметки, отдельной заметки, редактирования или удаления заметки анонимный пользователь перенаправляется на страницу логина.
* Страницы регистрации пользователей, входа в учётную запись и выхода из неё доступны всем пользователям.
### Контент:
* отдельная заметка передаётся на страницу со списком заметок в списке object_list, в словаре context;
* в список заметок одного пользователя не попадают заметки другого пользователя;
* на страницы создания и редактирования заметки передаются  формы.
### Логику:
* Залогиненный пользователь может создать заметку, а анонимный — не может. Анонима перенаправит на логин, а заметка не появится
* Невозможно создать две заметки с одинаковым slug.
* Если при создании заметки не заполнен slug, то он формируется автоматически, с помощью функции pytils.translit.slugify.
* Пользователь может редактировать и удалять свои заметки, но не может редактировать или удалять чужие.
## Не будем тестировать:
* Регистрацию пользователей, процесс входа в учетную запись и выхода из неё (делается средствами django)
* Админку.
* Абсолютные url-адреса; обращаться к адресам будем при помощи функции reverse('name').
* Шаблоны
* Всё то, что не попало в список «будем тестировать».