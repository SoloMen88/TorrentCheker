<div align="center">
  <h1>TorrentCheker</h1>
  <p>Чекер, который проверяет торрент-трекеры <a href="https://rutor.info/">rutor.info</a> и <a href="https://megapeer.vip/">megapeer.vip</a> на предмет появления новых раздач с фильмами в выбранных жанрах и генерирует страницу с прямыми ссылками на скачивание.</p>

  <img align="center" src="https://img.shields.io/github/repo-size/SoloMen88/TorrentCheker" alt="GitHub repo size">
  <img align="center" src="https://img.shields.io/github/stars/SoloMen88/TorrentCheker.svg?style=social&label=Stars&style=plastic" alt="GitHub Repo stars">
  <img align="center" src="https://img.shields.io/github/watchers/SoloMen88/TorrentCheker.svg?style=social&label=Watch&style=plastic" alt="GitHub watchers">
  <img align="center" src="https://img.shields.io/github/last-commit/SoloMen88/TorrentCheker.svg?style=social&label=Last commit&style=plastic" alt="GitHub last commit">
  <img align="center" src="https://img.shields.io/github/languages/top/SoloMen88/TorrentCheker" alt="GitHub top language">
  <img align="center" src="https://img.shields.io/badge/BS4-4179E0?style=social&label=Parsing&style=plastic" alt="Parsing">
  <img align="center" src="https://img.shields.io/badge/openapi-4179E0?style=social&label=API&style=plastic" alt="API">
</div>

## Навигация
* [ВНИМАНИЕ](#ВНИМАНИЕ)
* [Описание](#описание)
* [Начало работы](#начало-работы)
  * [Получение токена KinopoiskAPI](#получение-токена-kinopoiskapi)
  * [Регистрация на Кинозал](#регистрация-на-кинозал)
  * [Клонирование репозитория](#клонирование-репозитория)
  * [Указание настроек в файле settings.ini](#указание-настроек-в-файле-settings.ini)
  * [Создание виртуального окружения](#создание-виртуального-окружения)
  * [Запуск виртуального окружения](#запуск-виртуального-окружения)
  * [Установка зависимостей](#установка-зависимостей)
  * [Запуск файла приложения](#запуск-файла-приложения)
* [To Do](#to-do)
* [Автор](#автор)


## ВНИМАНИЕ
Приложение не скачивает и не хранит никакой контент. Оно лишь предоставляет ссылки на скачивание .torrent файлов. Решение скачивать или нет контент принимает сам пользователь! Автор ответственности не несет!

## Описание 

Приложение сканирует и парсит новые раздачи на популярных торрент трекерах <a href="https://rutor.info/">rutor.info</a> и <a href="https://megapeer.vip/">megapeer.vip</a>, согласно заданным настройкам отбирает нужные раздачи для которых запрашивает полные данные через API на кинопоиске, так же при указании логина/пароля ищет эти фильмы в лучшем качестве на <a href="https://kinozal.tv/">Кинозал</a> и генерирует страницу с удобным интерфейсом, где можно одной кнопкой скачать нужный фильм в максимально доступном качестве. Можно указать за сколько дней сканировать раздачи, до какого года выхода брать фильмы.

<img align="center" src="https://i.imgur.com/nqywd99.png" width="600" height="700" alt="Сгенерированная страница.">

## Начало работы
Для работы приложения нужно проделать следующие шаги:

### Получение токена KinopoiskAPI
Для получения токена необходима регистрация на сайте
<a href="https://kinopoiskapiunofficial.tech/signup">kinopoiskapiunofficial.tech</a>.
После регистрации перейдите в настройки своего <a href="https://kinopoiskapiunofficial.tech/profile">профиля</a> и сохраните токен.

### Регистрация на <a href="https://kinozal.tv/">Кинозал</a> (опционально).
Для получения ссылок на торренты с Кинозала необходима регистрация на сайте
<a href="https://kinozal.tv/signup.php">kinozal.tv</a>.
В разделе настроек [PRIVATE] необходимо указать логин/пароль.

### Использование сетевого протокола SOCKS.
Если у вас заблокированны трекеры можно в разделе настроек [PRIVATE] указать ip:port прокси сервера.

### Клонирование репозитория:
```
$ git clone https://github.com/SoloMen88/TorrentCheker
```
### Переименовать файл settings — exemple.ini в settings.ini.
Либо запустить приложение без файла настроек, он будет создан автоматически с дефолтными параметрами.

### Указание настроек в файле settings.ini:
```
[PRIVATE]
kp_token = токен с сайта https://kinopoiskapiunofficial.tech
kinozal_username = логин с кинозала (не обязательно)
kinozal_password = пароль с кинозала (не обязательно)
socks5_ip = ip адрес прокси сервера (не обязательно)
socks5_port = порт прокси сервера (не обязательно)

[BASE]
connection_attempts = количество попыток подключения (кинозал довольно не стабильный поэтому рекомендуется не менее 3х попыток)
load_days = количество дней за которые проверяются новые зраздачи
sort_type = сортитровка результатов (rating либо torrentsDate)
use_magnet = возвращать в результате магнет ссылку вместо торрент файла (True)
min_votes_kp = минимальное количество голосов на Кинопоиске для зачета рейтинга
min_votes_imdb = минимальное количество голосов на IMDB для зачета рейтинга
html_save_path = путь куда сохранить сгенерированный файл с результатом(папка должна существовать .\torrents_list.html)
genres = какие жанры включить в результаты поиска (ужасы, фантастика, триллер, етк..)
release_year_after = до какого года выхода включать фильмы

Остальные настройки скорее служебные, лучше их не менять.
```
### Создание виртуального окружения
```
python -m venv venv
```
### Запуск виртуального окружения
```
source venv/Scripts/activate
```
### Установка зависимостей
```
$ pip install -r requirements.txt
```
### Запуск файла приложения
```
TorrentCheker.py
```

### To Do
* Добавить поиск новых раздач на <a href="https://kinozal.tv/">Кинозал</a>, пока там ищутся фильмы только в более высоком качестве.
* Добавить поиск новых раздач на <a href="https://rutracker.org/">RuTracker.org</a>.
* Улучшить верстку генерируемой страницы (~~добавить выбор качества видео~~, ~~показывать сидов/личеров~~ и т.д.).
* 

### Автор
Станислав Кучеренко @SoloMen88