# DAYS — за сколько последних дней загружать цифровые релизы. По умолчанию 60.
# SOCKS_IP и SOCKS_PORT — IP-адрес и порт SOCKS Proxy. Если они указаны, то будет импортирована библиотека (PySocks), а в функции rutorLinks запросы будет обрабатываться через указанный прокси-сервер. В digitalReleases и filmDetail запросы всегда идут без прокси.
# SORT_TYPE — тип финальной сортировки. rating — сортировка по рейтингу, releaseDate — сортировка по дате цифрового релиза, torrentsDate — сортировка по дате появления торрента, comboDate — сортировка по комбинированное дате (наибольшая из releaseDate и torrentsDate).
# USE_MAGNET — использование Magnet-ссылок вместо ссылок на торрент-файлы.

LOAD_DAYS = 1
USE_MAGNET = False
SORT_TYPE = 'rating'  # "torrentsDate" #torrentsDate
MIN_VOTES_KP = 50
MIN_VOTES_IMDB = 150
# HTML_SAVE_PATH = "/opt/share/www/releases.html"
HTML_SAVE_PATH = ".\\releases.html"
SOCKS5_IP = ""
SOCKS5_PORT = 9050
CONNECTION_ATTEMPTS = 3

GENRES = ['ужасы', 'фантастика', 'троллер']
GROUPS = [1, 5, 7, 9]
RELEASE_YEAR = 2024

RUTOR_BASE_URL = "http://rutor.info"
# RUTOR_BASE_URL = "http://www.rutorc6mqdinc4cz.onion"
RUTOR_MONTHS = {"Янв": 1, "Фев": 2, "Мар": 3, "Апр": 4, "Май": 5,
                "Июн": 6, "Июл": 7, "Авг": 8, "Сен": 9, "Окт": 10, "Ноя": 11, "Дек": 12}
RUTOR_SEARCH_MAIN = "http://rutor.info/search/{}/{}/300/0/BDRip|(WEB%20DL)%201080p|1080%D1%80%7C2160%D1%80%7C1080i%20{}"
# RUTOR_SEARCH_MAIN = "http://www.rutorc6mqdinc4cz.onion/search/{}/{}/300/0/BDRemux|BDRip|(WEB%20DL)%201080p|2160p|1080%D1%80%7C2160%D1%80%7C1080i%20{}"

KINOZAL_SEARCH_BDREMUX = "http://kinozal-me.appspot.com/browse.php?s=%5E{}&g=3&c=0&v=4&d=0&w=0&t=0&f=0"
KINOZAL_SEARCH_BDRIP = "http://kinozal-me.appspot.com/browse.php?s=%5E{}&g=3&c=0&v=3&d=0&w=0&t=0&f=0"
KINOZAL_USERNAME = "your_KINOZAL_USERNAME"
KINOZAL_PASSWORD = "your_KINOZAL_PASSWORD"
KP_TOKEN = 'токен с сайта https://kinopoiskapiunofficial.tech'
