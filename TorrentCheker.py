"""TorrentCheker
Чекер, который проверяет торрент-трекеры на предмет появления новых раздач с 
фильмами в выбранных жанрах и генерит страницу с прямыми ссылками на скачивание.
Версия 0.0.3c
Автор @SoloMen88"""

import datetime
import operator
import re
from urllib.parse import quote, urljoin
import requests
from bs4 import BeautifulSoup
# import configparser
from ConfigParserList import ConfigParser
import os
from generateHTML import generateHTML
from kinopoisk_api import KP


settings = ConfigParser()
if os.path.isfile('settings.ini'):
    settings.read('settings.ini', encoding='utf-8')
else:
    settings['PRIVATE'] = {
        'KP_TOKEN': 'токен с сайта https://kinopoiskapiunofficial.tech',
        'KINOZAL_USERNAME': 'KINOZAL_USERNAME',
        'KINOZAL_PASSWORD': 'KINOZAL_PASSWORD',
        'SOCKS5_IP': '',
        'SOCKS5_PORT': ''
    }
    settings['BASE'] = {
        'CONNECTION_ATTEMPTS': 3,
        'LOAD_DAYS': 3,
        'SORT_TYPE': 'rating',
        'USE_MAGNET': False,
        'MIN_VOTES_KP': 50,
        'MIN_VOTES_IMDB': 100,
        'HTML_SAVE_PATH': '.\\torrents_list.html',
        'GENRES': ['ужасы', 'фантастика', 'триллер'],

        'RELEASE_YEAR_AFTER': 2024
    }
    settings['RUTOR'] = {
        'USE_RUTOR': True,
        'RUTOR_BASE_URL': 'http://rutor.info',
        'RUTOR_SEARCH_MAIN': "http://rutor.info/search/{}/{}/300/0/BDRip|(WEB%20DL)%201080p|1080%D1%80%7C2160%D1%80%7C1080i%20{}".replace('%', '%%'),
        'CATEGORIES_RUTOR': ['зарубежные фильмы', 'наши фильмы', 'аниме', 'мультики']
    }
    settings['MEGAPEER'] = {
        'USE_MEGAPEER': True,
        'MP_BASE_URL': 'https://megapeer.vip/',
        'MP_SEARCH_1080': "https://megapeer.vip/browse.php?search=1080+{}&stype=0&sort=0&ascdesc=0&r=0&cat={}&page={}",
        'MP_SEARCH_2160': "https://megapeer.vip/browse.php?search=2160+{}&stype=0&sort=0&ascdesc=0&r=0&cat={}&page={}",
        'CATEGORIES_MP': ['зарубежные фильмы', 'наши фильмы', 'аниме', 'мультики']
    }
    settings['KINOZAL'] = {
        'USE_KINOZAL': True,
        'KINOZAL_SEARCH_BDREMUX': 'https://kinozal.tv/browse.php?s=%5E{}&g=3&c=0&v=4&d=0&w=0&t=0&f=0'.replace('%', '%%'),
        'KINOZAL_SEARCH_BDRIP':   'https://kinozal.tv/browse.php?s=%5E{}&g=3&c=0&v=3&d=0&w=0&t=0&f=0'.replace('%', '%%')
    }
    with open('settings.ini', 'w') as settingsfile:
        settings.write(settingsfile)
        settings.read('settings.ini', encoding='utf-8')

VERSION = '0.0.3c'
KP_TOKEN = settings.get('PRIVATE', 'KP_TOKEN')
KINOZAL_USERNAME = settings.get('PRIVATE', 'KINOZAL_USERNAME')
KINOZAL_PASSWORD = settings.get('PRIVATE', 'KINOZAL_PASSWORD')
SOCKS5_IP = settings.get('PRIVATE', 'SOCKS5_IP')
SOCKS5_PORT = settings.get('PRIVATE', 'SOCKS5_PORT')

CONNECTION_ATTEMPTS = settings.getint('BASE', 'CONNECTION_ATTEMPTS')
LOAD_DAYS = settings.getint('BASE', 'LOAD_DAYS')
SORT_TYPE = settings.get('BASE', 'SORT_TYPE')
USE_MAGNET = settings.getboolean('BASE', 'USE_MAGNET')
MIN_VOTES_KP = settings.getint('BASE', 'MIN_VOTES_KP')
MIN_VOTES_IMDB = settings.getint('BASE', 'MIN_VOTES_IMDB')
HTML_SAVE_PATH = settings.get('BASE', 'HTML_SAVE_PATH')
GENRES = settings.getlist('BASE', 'GENRES')
RELEASE_YEAR_AFTER = settings.getint('BASE', 'RELEASE_YEAR_AFTER')

USE_RUTOR = settings.getboolean('RUTOR', 'USE_RUTOR')
RUTOR_BASE_URL = settings.get('RUTOR', 'RUTOR_BASE_URL')
RUTOR_SEARCH_MAIN = settings.get(
    'RUTOR', 'RUTOR_SEARCH_MAIN').replace('%%', '%')
CATEGORIES_RUTOR = settings.getlist('RUTOR', 'CATEGORIES_RUTOR')

USE_MEGAPEER = settings.getboolean('MEGAPEER', 'USE_MEGAPEER')
MP_BASE_URL = settings.get('MEGAPEER', 'MP_BASE_URL')
MP_SEARCH_1080 = settings.get(
    'MEGAPEER', 'MP_SEARCH_1080').replace('%%', '%')
MP_SEARCH_2160 = settings.get(
    'MEGAPEER', 'MP_SEARCH_2160').replace('%%', '%')
CATEGORIES_MP = settings.getlist('MEGAPEER', 'CATEGORIES_MP')

USE_KINOZAL = settings.getboolean('KINOZAL', 'USE_KINOZAL')
KINOZAL_SEARCH_BDREMUX = settings.get(
    'KINOZAL', 'KINOZAL_SEARCH_BDREMUX').replace('%%', '%')
KINOZAL_SEARCH_BDRIP = settings.get(
    'KINOZAL', 'KINOZAL_SEARCH_BDRIP').replace('%%', '%')

RUTOR_MONTHS = {"Янв": 1, "Фев": 2, "Мар": 3, "Апр": 4, "Май": 5,
                "Июн": 6, "Июл": 7, "Авг": 8, "Сен": 9, "Окт": 10, "Ноя": 11, "Дек": 12}

MP_MONTHS = {"Янв": 1, "Фев": 2, "Мар": 3, "Апр": 4, "Мая": 5,
             "Июн": 6, "Июл": 7, "Авг": 8, "Сен": 9, "Окт": 10, "Ноя": 11, "Дек": 12}

CATEGORIES = {
    'зарубежные фильмы': [1, 174],
    'наши фильмы': [5, 79],
    'аниме': [10, 76],
    'мультики': [7, 76]
}

kinopoisk = KP(token=KP_TOKEN)


def main():
    print('Версия: ' + VERSION)
    print("Дата и время запуска программы: " +
          str(datetime.datetime.now()) + ".")
    print("Количество попыток при ошибках соединения: " +
          str(CONNECTION_ATTEMPTS) + ".")

    if SOCKS5_IP:
        print("Для загрузки будет использоваться прокси-сервер SOCKS5: " +
              SOCKS5_IP + ":" + str(SOCKS5_PORT) + ".")

    print("Проверка доступности rutor.info...")
    try:
        content = loadURLContent(
            RUTOR_SEARCH_MAIN.format(0, 0, ""), useProxy=True)
        count = rutorPagesCountForResults(content)
        rutor = True
    except:
        print("Сайт rutor.info недоступен, или изменился его формат данных.")
        print("В поиске не будет результатов с rutor.info")
        rutor = False
    else:
        print("Сайт rutor.info доступен.")

    print("Проверка доступности megapeer.vip...")
    try:
        content = loadURLContent(
            MP_SEARCH_1080.format("", 0, 0), useProxy=True)
        count = mpPagesCountForResults(content)
        mp = True
    except:
        print("Сайт megapeer.vip недоступен, или изменился его формат данных.")
        print("В поиске не будет результатов с megapeer.vip")
        mp = False
    else:
        print("Сайт megapeer.vip доступен.")

    if not (rutor or mp):
        print("Ни один трекер не доступен, работа программы завершена (проверте включен ли VPN).")
        return 1

    print("Анализ раздач...")
    movies = []
    results = {}
    if rutor and USE_RUTOR:
        results.update(rutorResultsForDays(LOAD_DAYS))
    if mp and USE_MEGAPEER:
        resultsmp = mpResultsForDays(LOAD_DAYS)
        results = updateResults(results, resultsmp)
    movies = convertResults(results)
    movies.sort(key=operator.itemgetter(SORT_TYPE), reverse=True)
    print("Генерируем файл с результатами.")
    generateHTML(movies, HTML_SAVE_PATH, SORT_TYPE,
                 MIN_VOTES_KP, MIN_VOTES_IMDB, USE_MAGNET)

    print("Работа программы завершена успешно.")

    return 0


def categoriesDifferent(trType, cat):
    tracker = {
        'RT': 0,
        'MP': 1
    }
    return CATEGORIES[cat][tracker[trType]]


def updateResults(results0, results1):
    results = results0
    for result in results1:
        if result in results0:
            results[result].extend(results1[result])
        else:
            results[result] = results1[result]
    return results


def rutorResultsForDays(days):
    targetDate = datetime.date.today() - datetime.timedelta(days=days)

    tmpSet = set()
    tmpResults = {}

    for category in CATEGORIES_RUTOR:
        try:
            print("Загрузка списка предварительно подходящих раздач c RT...")
            content = loadURLContent(
                RUTOR_SEARCH_MAIN.format(0, categoriesDifferent('RT', category), ""), useProxy=True)
            count = rutorPagesCountForResults(content)
        except:
            raise ConnectionError(
                "Ошибка. Не удалось загрузить страницу с результатами поиска или формат данных rutor.info изменился.")

        i = 0
        needMore = True
        nextPage = True

        while needMore and nextPage:
            pageResults, nextPage = rutorResultsOnPage(content, False)
            for result in pageResults:
                if result["date"] >= targetDate:
                    element = parseRutorElement(result)
                    if not element:
                        continue
                    if (element["compareName"] in tmpSet):
                        continue
                    print("Обработка раздачи: {} ({})...".format(
                        element["nameRU"], element["year"]))
                    try:
                        elements = rutorSearchSimilarElements(
                            element, categoriesDifferent('RT', category))
                        elements = rutorFilmIDForElements(elements)
                        if USE_MEGAPEER:
                            elementsMP = mpSearchSimilarElements(
                                element, categoriesDifferent('MP', category), 2160)
                            elementsMP.extend(
                                mpSearchSimilarElements(element, categoriesDifferent('MP', category)))
                            elements.extend(mpFilmIDForElements(elementsMP))
                    except:
                        raise ConnectionError(
                            "Ошибка. Не удалось загрузить данные похожих раздач или загрузить страницу с описанием.")
                    tmpSet.add(element["compareName"])
                    if len(elements) > 0:
                        if (tmpResults.get(elements[0]["filmID"])):
                            tmpResults[elements[0]["filmID"]].extend(elements)
                        else:
                            tmpResults[elements[0]["filmID"]] = elements
                else:
                    needMore = False
                    break
            i = i + 1
            if (i >= count):
                needMore = False
            if needMore:
                print("Загрузка списка предварительно подходящих раздач c RT...")
                try:
                    content = loadURLContent(
                        RUTOR_SEARCH_MAIN.format(i, categoriesDifferent('RT', category), ""), useProxy=True)
                except:
                    raise ConnectionError(
                        "Ошибка. Не удалось загрузить страницу с результатами поиска или формат данных rutor.info изменился.")

    return tmpResults


def convertResults(rutorResults):
    targetDate = datetime.date.today() - datetime.timedelta(days=LOAD_DAYS)

    movies = []

    try:
        if KINOZAL_USERNAME and USE_KINOZAL:
            print("Логинимся на kinozal.tv")
            opener = kinozalAuth(KINOZAL_USERNAME, KINOZAL_PASSWORD)
        else:
            opener = None
    except:
        print("Не удалось залогиниться на kinozal.tv")
        opener = None

    for key, values in rutorResults.items():
        BDDate = None
        BDDateLicense = None
        WBDate = None
        for value in values:
            if "BD" in value["type"]:
                if value["license"]:
                    if not BDDateLicense:
                        BDDateLicense = value["date"]
                    else:
                        BDDateLicense = min(BDDateLicense, value["date"])
                else:
                    if not BDDate:
                        BDDate = value["date"]
                    else:
                        BDDate = min(BDDate, value["date"])
            else:
                if not WBDate:
                    WBDate = value["date"]
                else:
                    WBDate = min(WBDate, value["date"])
        # if BDDateLicense:
        #     if BDDateLicense < targetDate:
        #         continue
        # elif BDDate:
        #     if BDDate < targetDate:
        #         continue
        # else:
        #     if WBDate < targetDate:
        #         continue

        tr = {}

        for value in values:
            if value["type"] == "UHD BDRemux":
                if value["hdr"]:
                    if tr.get("UHD BDRemux HDR") != None:
                        if ((not tr["UHD BDRemux HDR"]["license"]) and value["license"]):
                            tr["UHD BDRemux HDR"] = value
                        elif (tr["UHD BDRemux HDR"]["license"] == False and value["license"] == False) or (tr["UHD BDRemux HDR"]["license"] == True and value["license"] == True):
                            if value["seeders"] > tr["UHD BDRemux HDR"]["seeders"]:
                                tr["UHD BDRemux HDR"] = value
                    else:
                        tr["UHD BDRemux HDR"] = value
                else:
                    if tr.get("UHD BDRemux SDR") != None:
                        if ((not tr["UHD BDRemux SDR"]["license"]) and value["license"]):
                            tr["UHD BDRemux SDR"] = value
                        elif (tr["UHD BDRemux SDR"]["license"] == False and value["license"] == False) or (tr["UHD BDRemux SDR"]["license"] == True and value["license"] == True):
                            if value["seeders"] > tr["UHD BDRemux SDR"]["seeders"]:
                                tr["UHD BDRemux SDR"] = value
                    else:
                        tr["UHD BDRemux SDR"] = value
            elif value["type"] == "BDRemux":
                if tr.get("BDRemux") != None:
                    if ((not tr["BDRemux"]["license"]) and value["license"]):
                        tr["BDRemux"] = value
                    elif (tr["BDRemux"]["license"] == False and value["license"] == False) or (tr["BDRemux"]["license"] == True and value["license"] == True):
                        if value["seeders"] > tr["BDRemux"]["seeders"]:
                            tr["BDRemux"] = value
                else:
                    tr["BDRemux"] = value
            elif value["type"] == "BDRip-HEVC":
                if tr.get("BDRip-HEVC 1080p") != None:
                    if ((not tr["BDRip-HEVC 1080p"]["license"]) and value["license"]):
                        tr["BDRip-HEVC 1080p"] = value
                    elif (tr["BDRip-HEVC 1080p"]["license"] == False and value["license"] == False) or (tr["BDRip-HEVC 1080p"]["license"] == True and value["license"] == True):
                        if value["seeders"] > tr["BDRip-HEVC 1080p"]["seeders"]:
                            tr["BDRip-HEVC 1080p"] = value
                else:
                    tr["BDRip-HEVC 1080p"] = value
            elif value["type"] == "BDRip":
                if tr.get("BDRip 1080p") != None:
                    if ((not tr["BDRip 1080p"]["license"]) and value["license"]):
                        tr["BDRip 1080p"] = value
                    elif (tr["BDRip 1080p"]["license"] == False and value["license"] == False) or (tr["BDRip 1080p"]["license"] == True and value["license"] == True):
                        if value["seeders"] > tr["BDRip 1080p"]["seeders"]:
                            tr["BDRip 1080p"] = value
                else:
                    tr["BDRip 1080p"] = value
            elif value["type"] == "WEB-DL":
                if value["resolution"] == "2160p":
                    if value["hdr"]:
                        if tr.get("WEB-DL 2160p HDR") != None:
                            if ((not tr["WEB-DL 2160p HDR"]["license"]) and value["license"]):
                                tr["WEB-DL 2160p HDR"] = value
                            elif (tr["WEB-DL 2160p HDR"]["license"] == False and value["license"] == False) or (tr["WEB-DL 2160p HDR"]["license"] == True and value["license"] == True):
                                if value["seeders"] > tr["WEB-DL 2160p HDR"]["seeders"]:
                                    tr["WEB-DL 2160p HDR"] = value
                        else:
                            tr["WEB-DL 2160p HDR"] = value
                    else:
                        if tr.get("WEB-DL 2160p SDR") != None:
                            if ((not tr["WEB-DL 2160p SDR"]["license"]) and value["license"]):
                                tr["WEB-DL 2160p SDR"] = value
                            elif (tr["WEB-DL 2160p SDR"]["license"] == False and value["license"] == False) or (tr["WEB-DL 2160p SDR"]["license"] == True and value["license"] == True):
                                if value["seeders"] > tr["WEB-DL 2160p SDR"]["seeders"]:
                                    tr["WEB-DL 2160p SDR"] = value
                        else:
                            tr["WEB-DL 2160p SDR"] = value
                else:
                    if tr.get("WEB-DL 1080p") != None:
                        if ((not tr["WEB-DL 1080p"]["license"]) and value["license"]):
                            tr["WEB-DL 1080p"] = value
                        elif (tr["WEB-DL 1080p"]["license"] == False and value["license"] == False) or (tr["WEB-DL 1080p"]["license"] == True and value["license"] == True):
                            if value["seeders"] > tr["WEB-DL 1080p"]["seeders"]:
                                tr["WEB-DL 1080p"] = value
                    else:
                        tr["WEB-DL 1080p"] = value

        # if tr.get("UHD BDRemux HDR") or tr.get("UHD BDRemux SDR") or tr.get("BDRip-HEVC 1080p") or tr.get("BDRip 1080p") or tr.get("BDRemux"):
        #     tr.pop("WEB-DL 2160p HDR", None)
        #     tr.pop("WEB-DL 2160p SDR", None)
        #     tr.pop("WEB-DL 1080p", None)

        # if tr.get("UHD BDRemux HDR"):
        #     tr.pop("UHD BDRemux SDR", None)

        print("Загрузка данных для фильма с ID " + values[0]["filmID"] + "...")
        flag = False
        detailse = filmDetail(values[0]["filmID"])
        if len(detailse) == 0:
            detailse = filmDetail(values[0]["filmID"])
        for genre in GENRES:
            try:
                if genre in detailse['genre']:
                    detail = detailse.copy()
                    flag = True
                    break
            except:
                print(f"Функция filmDetail для фильма " +
                      values[0]["filmID"] + " вернула пустой список")
        if not flag:
            continue
        print("Загружены данные для фильма: " + detail["nameRU"] + ".")

        if not detail.get("year"):
            print("У фильма \"" + detail["nameRU"] +
                  "\" нет даты премьеры. Пропуск фильма.")
            continue
        if detail["year"] < RELEASE_YEAR_AFTER:
            print("Фильм \"" + detail["nameRU"] +
                  "\" слишком старый. Пропуск фильма.")
            continue

        finalResult = []

        if (tr.get("WEB-DL 1080p") or tr.get("WEB-DL 2160p HDR") or tr.get("WEB-DL 2160p SDR")) and opener:
            print("Пробуем найти отсутствующий BDRip 1080p на kinozal.tv...")
            kName = detail["nameRU"]
            kNameOriginal = detail["nameOriginal"]
            if not kNameOriginal:
                kNameOriginal = kName
            try:
                kRes = kinozalSearch(
                    {"nameRU": kName, "nameOriginal": kNameOriginal, "year": detail["year"]}, opener, "BDRip 1080p")
                if kRes:
                    print("Отсутствующий BDRip 1080p найден на kinozal.tv.")
                    finalResult.append(kRes)
                    tr.pop("WEB-DL 2160p HDR", None)
                    tr.pop("WEB-DL 2160p SDR", None)
                    tr.pop("WEB-DL 1080p", None)
                    if kRes["license"]:
                        BDDateLicense = kRes["date"]
                    else:
                        BDDate = kRes["date"]
            except:
                print(
                    "Какая-то ошибка при работе с kinozal.tv. Подробная информация о проблемах ещё не добавлена в функцию.")
        if tr.get("WEB-DL 1080p"):
            finalResult.append({"link": tr["WEB-DL 1080p"]["fileLink"], "magnet": tr["WEB-DL 1080p"]["magnetLink"], "date": tr["WEB-DL 1080p"]
                               ["date"], "type": "WEB-DL 1080p", "license": tr["WEB-DL 1080p"]["license"], "page": tr['WEB-DL 1080p']['descriptionLink'], "seeders": tr['WEB-DL 1080p']['seeders'], "leechers": tr['WEB-DL 1080p']['leechers']})
        if tr.get("WEB-DL 2160p HDR"):
            finalResult.append({"link": tr["WEB-DL 2160p HDR"]["fileLink"], "magnet": tr["WEB-DL 2160p HDR"]["magnetLink"], "date": tr["WEB-DL 2160p HDR"]
                               ["date"], "type": "WEB-DL 2160p HDR", "license": tr["WEB-DL 2160p HDR"]["license"], "page": tr['WEB-DL 2160p HDR']['descriptionLink'], "seeders": tr['WEB-DL 2160p HDR']['seeders'], "leechers": tr['WEB-DL 2160p HDR']['leechers']})
        elif tr.get("WEB-DL 2160p SDR"):
            finalResult.append({"link": tr["WEB-DL 2160p SDR"]["fileLink"], "magnet": tr["WEB-DL 2160p SDR"]["magnetLink"], "date": tr["WEB-DL 2160p SDR"]
                               ["date"], "type": "WEB-DL 2160p SDR", "license": tr["WEB-DL 2160p SDR"]["license"], "page": tr['WEB-DL 2160p SDR']['descriptionLink'], "seeders": tr['WEB-DL 2160p SDR']['seeders'], "leechers": tr['WEB-DL 2160p SDR']['leechers']})
        if tr.get("BDRip 1080p"):
            finalResult.append({"link": tr["BDRip 1080p"]["fileLink"], "magnet": tr["BDRip 1080p"]["magnetLink"], "date": tr["BDRip 1080p"]
                               ["date"], "type": "BDRip 1080p", "license": tr["BDRip 1080p"]["license"], "page": tr['BDRip 1080p']['descriptionLink'], "seeders": tr['BDRip 1080p']['seeders'], "leechers": tr['BDRip 1080p']['leechers']})
        elif (tr.get("BDRip-HEVC 1080p") or tr.get("BDRemux")) and opener:
            print("Пробуем найти отсутствующий BDRip 1080p на kinozal.tv...")
            kName = detail["nameRU"]
            kNameOriginal = detail["nameOriginal"]
            if not kNameOriginal:
                kNameOriginal = kName
            try:
                kRes = kinozalSearch(
                    {"nameRU": kName, "nameOriginal": kNameOriginal, "year": detail["year"]}, opener, "BDRip 1080p")
                if kRes:
                    print("Отсутствующий BDRip 1080p найден на kinozal.tv.")
                    finalResult.append(kRes)
            except:
                print(
                    "Какая-то ошибка при работе с kinozal.tv. Подробная информация о проблемах ещё не добавлена в функцию.")
        if tr.get("BDRip-HEVC 1080p"):

            found = False

            try:
                if (not tr["BDRip-HEVC 1080p"]["license"]) and tr["BDRip 1080p"]["license"]:
                    kName = detail["nameRU"]
                    kNameOriginal = detail["nameOriginal"]
                    if not kNameOriginal:
                        kNameOriginal = kName
                    kRes = kinozalSearch({"nameRU": kName, "nameOriginal": kNameOriginal,
                                         "year": detail["year"]}, opener, "BDRip-HEVC 1080p", licenseOnly=True)
                    if kRes:
                        found = True
                        finalResult.append(kRes)
            except:
                pass

            if not found:
                finalResult.append({"link": tr["BDRip-HEVC 1080p"]["fileLink"], "magnet": tr["BDRip-HEVC 1080p"]["magnetLink"], "date": tr["BDRip-HEVC 1080p"]
                                   ["date"], "type": "BDRip-HEVC 1080p", "license": tr["BDRip-HEVC 1080p"]["license"], "page": tr['BDRip-HEVC 1080p']['descriptionLink'], "seeders": tr['BDRip-HEVC 1080p']['seeders'], "leechers": tr['BDRip-HEVC 1080p']['leechers']})
        elif (tr.get("BDRip 1080p") or tr.get("BDRemux")) and opener:
            print("Пробуем найти отсутствующий BDRip-HEVC 1080p на kinozal.tv...")
            kName = detail["nameRU"]
            kNameOriginal = detail["nameOriginal"]
            if not kNameOriginal:
                kNameOriginal = kName
            try:
                kRes = kinozalSearch({"nameRU": kName, "nameOriginal": kNameOriginal,
                                     "year": detail["year"]}, opener, "BDRip-HEVC 1080p")
                if kRes:
                    print("Отсутствующий BDRip-HEVC 1080p найден на kinozal.tv.")
                    finalResult.append(kRes)
            except:
                print(
                    "Какая-то ошибка при работе с kinozal.tv. Подробная информация о проблемах ещё не добавлена в функцию.")
        if tr.get("BDRemux"):
            found = False

            try:
                if (not tr["BDRemux"]["license"]) and tr["BDRip 1080p"]["license"]:
                    kName = detail["nameRU"]
                    kNameOriginal = detail["nameOriginal"]
                    if not kNameOriginal:
                        kNameOriginal = kName
                    kRes = kinozalSearch({"nameRU": kName, "nameOriginal": kNameOriginal,
                                         "year": detail["year"]}, opener, "BDRemux", licenseOnly=True)
                    if kRes:
                        found = True
                        finalResult.append(kRes)
            except:
                pass

            if not found:
                finalResult.append({"link": tr["BDRemux"]["fileLink"], "magnet": tr["BDRemux"]["magnetLink"], "date": tr["BDRemux"]
                                   ["date"], "type": "BDRemux", "license": tr["BDRemux"]["license"], "page": tr['BDRemux']['descriptionLink'], "seeders": tr['BDRemux']['seeders'], "leechers": tr['BDRemux']['leechers']})
        elif (tr.get("BDRip-HEVC 1080p") or tr.get("BDRip 1080p")) and opener:
            print("Пробуем найти отсутствующий BDRemux на kinozal.tv...")
            kName = detail["nameRU"]
            kNameOriginal = detail["nameOriginal"]
            if not kNameOriginal:
                kNameOriginal = kName
            try:
                kRes = kinozalSearch(
                    {"nameRU": kName, "nameOriginal": kNameOriginal, "year": detail["year"]}, opener, "BDRemux")
                if kRes:
                    print("Отсутствующий BDRemux найден на kinozal.tv.")
                    finalResult.append(kRes)
            except:
                print(
                    "Какая-то ошибка при работе с kinozal.tv. Подробная информация о проблемах ещё не добавлена в функцию.")
        if tr.get("UHD BDRemux HDR"):
            finalResult.append({"link": tr["UHD BDRemux HDR"]["fileLink"], "magnet": tr["UHD BDRemux HDR"]["magnetLink"], "date": tr["UHD BDRemux HDR"]
                               ["date"], "type": "UHD BDRemux HDR", "license": tr["UHD BDRemux HDR"]["license"], "page": tr['UHD BDRemux HDR']['descriptionLink'], "seeders": tr['UHD BDRemux HDR']['seeders'], "leechers": tr['UHD BDRemux HDR']['leechers']})
        elif tr.get("UHD BDRemux SDR"):
            finalResult.append({"link": tr["UHD BDRemux SDR"]["fileLink"], "magnet": tr["UHD BDRemux SDR"]["magnetLink"], "date": tr["UHD BDRemux SDR"]
                               ["date"], "type": "UHD BDRemux SDR", "license": tr["UHD BDRemux SDR"]["license"], "page": tr['UHD BDRemux SDR']['descriptionLink'], "seeders": tr['UHD BDRemux SDR']['seeders'], "leechers": tr['UHD BDRemux SDR']['leechers']})

        dates = []
        for torrent in finalResult:
            dates.append(torrent["date"])
        dates.sort()

        detail["torrents"] = finalResult
        detail["torrentsDate"] = dates[0]
        if BDDateLicense:
            detail["torrentsDate"] = BDDateLicense
            detail["torrentsDateType"] = "Blu-ray с официальным русским озвучиванием ★"
        elif BDDate:
            detail["torrentsDate"] = BDDate
            detail["torrentsDateType"] = "Blu-ray с официальным русским озвучиванием из VoD"
        else:
            detail["torrentsDate"] = WBDate
            detail["torrentsDateType"] = "VoD с официальным русским озвучиванием"
        movies.append(detail)

    return movies


def loadURLContent(url, attempts=CONNECTION_ATTEMPTS, useProxy=False):
    headers = {}
    headers["Accept-encoding"] = "gzip"
    headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0"

    if useProxy and SOCKS5_IP:
        proxies = {'http': "socks5://{}:{}".format(SOCKS5_IP, SOCKS5_PORT)}
        session = requests.Session(proxies=proxies)
    else:
        session = requests.Session()

    response = None
    n = attempts
    while n > 0:
        try:
            response = session.get(url, headers=headers)
            break
        except:
            n -= 1
            if (n <= 0):
                raise ConnectionError(
                    "Ошибка соединения. Все попытки соединения израсходованы.")

    return response.text


def rutorPagesCountForResults(content):
    soup = BeautifulSoup(content, 'html.parser')

    if (soup == None):
        raise ValueError(
            "Ошибка. Невозможно инициализировать HTML-парсер, что-то не так с контентом.")

    try:
        resultsGroup = soup.find("div", id="index")
    except:
        raise ValueError("Ошибка. Нет блока с торрентами.")
    if resultsGroup == None:
        raise ValueError("Ошибка. Нет блока с торрентами.")

    try:
        indexes = [text for text in resultsGroup.b.stripped_strings]
    except:
        raise ValueError("Ошибка. Нет блока со страницами результатов.")
    if len(indexes) == 0:
        raise ValueError("Ошибка. Нет блока со страницами результатов.")

    lastIndexStr = indexes[-1]
    if lastIndexStr.startswith("Страницы"):
        return 1

    lastIndex = int(lastIndexStr)

    if lastIndex <= 0:
        raise ValueError("Ошибка. Неверное значение индекса страницы.")

    return lastIndex


def filmDetail(filmID):
    result = {}
    content = None

    try:
        content = kinopoisk.get_film(int(filmID))
    except:
        pass

    if content:
        if content.kp_rate_cnt < MIN_VOTES_KP:
            content.kp_rate = None
        if content.imdb_rate_cnt < MIN_VOTES_IMDB:
            content.imdb_rate = None

        if content.imdb_rate and content.kp_rate:
            rating = (content.imdb_rate + content.kp_rate) / 2.0 + 0.001
        elif content.kp_rate:
            rating = content.kp_rate
        elif content.imdb_rate:
            rating = content.imdb_rate
        else:
            rating = 0

        directorsResult = ""
        if len(content.directors) > 0:
            for director in content.directors:
                directorsResult += director
                directorsResult += ", "
        if directorsResult.endswith(", "):
            directorsResult = directorsResult[:-2]

        actorsResult = ""
        if len(content.actors) > 0:
            for actor in content.actors:
                actorsResult += actor
                actorsResult += ", "
        if actorsResult.endswith(", "):
            actorsResult = actorsResult[:-2]

        result["filmID"] = filmID
        result["nameRU"] = content.ru_name
        if content.name:
            result["nameOriginal"] = content.name
        else:
            result["nameOriginal"] = content.ru_name
        result["description"] = content.description
        result["year"] = content.year
        result["country"] = ", ".join(content.countries)
        result["genre"] = ''
        result["genre"] = ", ".join(content.genres)
        result["ratingAgeLimits"] = str(
            content.age_rating)
        result["ratingMPAA"] = content.ratingMpaa
        result["posterURL"] = content.poster
        result["filmLength"] = content.duration
        result["ratingKP"] = content.kp_rate
        result["ratingKPCount"] = content.kp_rate_cnt
        result["ratingIMDb"] = content.imdb_rate
        result["ratingIMDbCount"] = content.imdb_rate_cnt
        result["rating"] = rating
        result["ratingFloat"] = float(rating)
        result["directors"] = directorsResult
        result["actors"] = actorsResult
        result["webURL"] = content.kp_url
        result["trailerURL"] = ''

    return result


def convertToAlfaNum(str):
    tmpStr = str.upper()
    tmpList = []
    for c in tmpStr:
        if c.isalnum():
            tmpList.append(c)
        else:
            tmpList.append(" ")

    return " ".join("".join(tmpList).split())


def replaceSimilarChars(str):
    tmpStr = str.upper()
    tmpStr = tmpStr.replace("A", "А")
    tmpStr = tmpStr.replace("B", "В")
    tmpStr = tmpStr.replace("C", "С")
    tmpStr = tmpStr.replace("E", "Е")
    tmpStr = tmpStr.replace("H", "Н")
    tmpStr = tmpStr.replace("K", "К")
    tmpStr = tmpStr.replace("M", "М")
    tmpStr = tmpStr.replace("O", "О")
    tmpStr = tmpStr.replace("P", "Р")
    tmpStr = tmpStr.replace("T", "Т")
    tmpStr = tmpStr.replace("X", "Х")
    tmpStr = tmpStr.replace("Y", "У")
    tmpStr = tmpStr.replace("Ё", "Е")

    return tmpStr


def parseRutorElement(dict):
    tmpParts = dict["name"].split("|")

    fullName = tmpParts[0].strip().upper()
    tags = set()
    tagsStr = ""

    if len(tmpParts) > 1:
        for i in range(1, len(tmpParts)):
            moreParts = tmpParts[i].split(",")
            for tmpPart in moreParts:
                tags.add(tmpPart.strip().upper())
                tagsStr = tagsStr + tmpPart.strip().upper() + " "

    if ("LINE" in tags) or ("UKR" in tags) or ("3D-VIDEO" in tags) or ("60 FPS" in tags) or (("1080" in fullName) and ("HDR" in tags)) or ("UHD BDRIP" in fullName) or ("[" in fullName) or ("]" in fullName):
        return None

    patternYear = re.compile("\((\d{4})\)")
    match = re.search(patternYear, tmpParts[0])

    if not match:
        return None

    year = match[1]
    targetYear = RELEASE_YEAR_AFTER
    # targetYear = (datetime.date.today() - datetime.timedelta(days=365)).year
    if int(year) < targetYear:
        return None

    namesPart = (tmpParts[0][:match.start()]).strip()
    typePart = (tmpParts[0][match.end():]).strip().upper()
    names = namesPart.split("/")
    RU = True if len(names) == 1 else False
    nameRU = names[0].strip()
    names.pop(0)
    if len(names) > 0:
        nameOriginal = names[-1]
    else:
        nameOriginal = nameRU

    if not RU:
        if not (("ЛИЦЕНЗИЯ" in tags) or ("ITUNES" in tags) or ("D" in tags) or ("D1" in tags) or ("D2" in tags) or ("НЕВАФИЛЬМ" in tags) or ("ПИФАГОР" in tags) or ("AMEDIA" in tags) or ("МОСФИЛЬМ-МАСТЕР" in tags) or ("СВ-ДУБЛЬ" in tags) or ("КИРИЛЛИЦА" in tags) or ("АРК-ТВ" in tagsStr) or ("APK-ТВ" in tagsStr) or ("APK-TB" in tagsStr) or ("MovieDalen" in tagsStr) or ("Red Head" in tagsStr) or ("LostFilm" in tagsStr) or ("Jaskier" in tagsStr) or ("HDRezka" in tagsStr)):
            return None

    license = True if ("ЛИЦЕНЗИЯ" in tags) else False

    if "UHD BDREMUX" in typePart:
        type = "UHD BDRemux"
    elif "BDREMUX" in typePart:
        type = "BDRemux"
    elif "BDRIP-HEVC" in typePart:
        type = "BDRip-HEVC"
    elif "BDRIP" in typePart:
        type = "BDRip"
    elif "WEB-DL " in typePart:
        type = "WEB-DL"
    elif "WEB-DL-HEVC" in typePart:
        # type = "WEB-DL-HEVC"
        type = "WEB-DL"
    else:
        return None

    hdr = False

    if "2160" in typePart:
        resolution = "2160p"
        hdr = True if ("HDR" in tags) else False
    elif "1080I" in typePart:
        resolution = "1080i"
    elif ("1080P" in typePart) or ("1080Р" in typePart):
        resolution = "1080p"
    else:
        return None

    IMAX = True if (("IMAX" in tags) or ("IMAX EDITION" in tags)) else False
    OpenMatte = True if ("OPEN MATTE" in tags) else False

    if RU:
        compareName = replaceSimilarChars(
            convertToAlfaNum(nameRU)) + " " + year
        searchPattern = "(^" + convertToAlfaNum(nameRU) + \
            " " + year + ")|(^" + compareName + ")"
    else:
        compareName = replaceSimilarChars(convertToAlfaNum(
            nameRU)) + " " + convertToAlfaNum(nameOriginal) + " " + year
        searchPattern = "(^" + convertToAlfaNum(nameRU) + " " + \
            convertToAlfaNum(nameOriginal) + " " + year + \
            ")"  # |(^" + compareName + ")"
        if len(searchPattern) > 130:
            searchPattern = "(^" + convertToAlfaNum(nameRU) + " " + \
                convertToAlfaNum(nameOriginal) + " " + year + ")"
    searchPattern = searchPattern.replace("AND", "and")
    searchPattern = searchPattern.replace("OR", "or")

    result = {"date": dict["date"], "torrentName": dict["name"], "fileLink": dict["fileLink"], "magnetLink": dict["magnetLink"], "descriptionLink": dict["descriptionLink"], "size": dict["size"], "seeders": dict["seeders"], "leechers": dict["leechers"],
              "nameOriginal": nameOriginal, "nameRU": nameRU, "compareName": compareName, "searchPattern": searchPattern, "year": year, "type": type, "resolution": resolution, "hdr": hdr, "IMAX": IMAX, "OpenMatte": OpenMatte, "license": license}

    return result


def rutorSearchSimilarElements(element, category):
    results = []
    content = loadURLContent(RUTOR_SEARCH_MAIN.format(
        0, category, quote(element["searchPattern"])), useProxy=True)
    try:
        pageResults, t = rutorResultsOnPage(content)
    except:
        return results

    for result in pageResults:
        tmpElement = parseRutorElement(result)
        if not tmpElement:
            continue
        if tmpElement["compareName"] == element["compareName"]:
            results.append(tmpElement)

    return results


def rutorResultsOnPage(content, similar=True):
    targetDate = datetime.date.today() - datetime.timedelta(days=LOAD_DAYS)
    soup = BeautifulSoup(content, 'html.parser')

    if (soup == None):
        raise ValueError("{} {}".format(datetime.datetime.now(
        ), "Невозможно инициализировать HTML-парсер, что-то не так с контентом."))

    result = []

    try:
        resultsGroup = soup.find("div", id="index")
    except Exception as e:
        raise ValueError("{} {}".format(
            datetime.datetime.now(), "Нет блока с торрентами."))
    if resultsGroup == None:
        raise ValueError("{} {}".format(
            datetime.datetime.now(), "Нет блока с торрентами."))

    elements = resultsGroup.find_all("tr", class_=["gai", "tum"])

    if len(elements) == 0:
        return result, True

    for element in elements:
        allTDinElement = element.find_all("td", recursive=False)

        if len(allTDinElement) == 4:
            dateElement = allTDinElement[0]
            mainElement = allTDinElement[1]
            sizeElement = allTDinElement[2]
            peersElement = allTDinElement[3]
        elif len(allTDinElement) == 5:
            dateElement = allTDinElement[0]
            mainElement = allTDinElement[1]
            sizeElement = allTDinElement[3]
            peersElement = allTDinElement[4]
        else:
            raise ValueError("{} {}".format(
                datetime.datetime.now(), "Неверный формат блока торрента."))

        try:
            components = dateElement.string.split(u"\xa0")
            torrentDate = datetime.date((int(components[2]) + 2000) if int(components[2]) < 2000 else int(
                components[2]), RUTOR_MONTHS[components[1]], int(components[0]))
        except Exception as e:
            raise ValueError("{} {}".format(
                datetime.datetime.now(), "Неверный формат блока даты."))

        if (not similar) and torrentDate < targetDate:
            return result, False
        try:
            seeders = int(peersElement.find(
                "span", class_="green").get_text(strip=True))
            leechers = int(peersElement.find(
                "span", class_="red").get_text(strip=True))
        except Exception as e:
            raise ValueError("{} {}".format(
                datetime.datetime.now(), "Неверный формат блока пиров."))

        try:
            sizeStr = sizeElement.get_text(strip=True)

            if sizeStr.endswith("GB"):
                multiplier = 1024 * 1024 * 1024
            elif sizeStr.endswith("MB"):
                multiplier = 1024 * 1024
            elif sizeStr.endswith("KB"):
                multiplier = 1024
            else:
                multiplier = 1

            components = sizeStr.split(u"\xa0")
            torrentSize = int(float(components[0]) * multiplier)
        except Exception as e:
            raise ValueError("{} {}".format(
                datetime.datetime.now(), "Неверный формат блока размера."))

        try:
            mainElements = mainElement.find_all("a")
            torrentFileLink = mainElements[0].get("href").strip()
            if not torrentFileLink.startswith("http"):
                torrentFileLink = urljoin(
                    "http://d.rutor.info", torrentFileLink)
            magnetLink = mainElements[1].get("href").strip()

            if not magnetLink.startswith("magnet"):
                raise ValueError("Magnet")

            torrentLink = quote(mainElements[2].get("href").strip())
            if not torrentLink.startswith("http"):
                torrentLink = urljoin(RUTOR_BASE_URL, torrentLink)

            torrentName = mainElements[2].get_text(strip=True)
        except Exception as e:
            raise ValueError("{} {}".format(datetime.datetime.now(
            ), "Неверный формат основного блока в блоке торрента."))

        result.append({"date": torrentDate, "name": torrentName, "fileLink": torrentFileLink, "magnetLink": magnetLink,
                      "descriptionLink": torrentLink, "size": torrentSize, "seeders": seeders, "leechers": leechers})

    return result, True


def rutorFilmIDForElements(elements, deep=True):
    kID = None
    for element in elements:
        content = loadURLContent(element["descriptionLink"], useProxy=True)

        patternLink = re.compile("\"http://www.kinopoisk.ru/film/(.*?)/\"")
        matches = re.findall(patternLink, content)
        if len(matches) == 1:
            kID = matches[0]
            break
        elif len(matches) > 1:
            return []

        if not kID:
            patternLink = re.compile(
                "\"http://www.kinopoisk.ru/level/1/film/(.*?)/\"")
            matches = re.findall(patternLink, content)
            if len(matches) == 1:
                kID = matches[0]
                break
            elif len(matches) > 1:
                return []

    if kID:
        for element in elements:
            element["filmID"] = kID
        return elements
    else:
        if not deep:
            return []

        try:
            for element in elements:
                content = loadURLContent(
                    element["descriptionLink"], useProxy=True)
                pageResults = rutorResultsOnPage(content, True)
                newElements = rutorFilmIDForElements(pageResults, deep=False)
                if len(newElements) > 0:
                    kID = newElements[0]["filmID"]
                    break
        except:
            return []

    if kID:
        for element in elements:
            element["filmID"] = kID
        return elements
    else:
        return []


def kinozalAuth(username, password, useProxy=True):
    headers = {}
    headers["Accept-encoding"] = "gzip"
    headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0"

    session = requests.Session()
    try:
        auth = session.post("https://kinozal.tv/takelogin.php",
                            data={'login': KINOZAL_USERNAME,
                                  'password': KINOZAL_PASSWORD},
                            headers=headers)
        return session
    except:
        return None


def kinozalSearch(filmDetail, session, type, licenseOnly=False):
    headers = {}
    headers["Accept-encoding"] = "gzip"
    headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0"

    targetDate = datetime.date.today() - datetime.timedelta(days=LOAD_DAYS)
    DBResults = []
    PMResults = []

    if type == "BDRip 1080p" or type == "BDRip-HEVC 1080p":
        try:
            response = session.get(KINOZAL_SEARCH_BDRIP.format(
                quote(filmDetail["nameRU"])), headers=headers)
        except:
            response = session.get(KINOZAL_SEARCH_BDRIP.format(
                quote(filmDetail["nameRU"])), headers=headers)
    elif type == "BDRemux":
        try:
            response = session.get(KINOZAL_SEARCH_BDREMUX.format(
                quote(filmDetail["nameRU"])), headers=headers)
        except:
            response = session.get(KINOZAL_SEARCH_BDREMUX.format(
                quote(filmDetail["nameRU"])), headers=headers)
    else:
        return None

    content = response.text.replace("\n", "")
    soup = BeautifulSoup(content, 'html.parser')
    elements = soup.find_all("td", class_=["nam"])

    if len(elements) == 0:
        return None

    for element in elements:
        contents = element.contents
        if len(contents) != 7:
            continue

        fullName = contents[0].get_text(strip=True)
        torrentLink = contents[0].get("href").strip()
        seeders = int(contents[3].get_text(strip=True))
        leechers = int(contents[4].get_text(strip=True))
        dateStr = contents[5].get_text(strip=True)

        if "сегодня" in dateStr:
            torrentDate = datetime.date.today()
        elif "вчера" in dateStr:
            torrentDate = datetime.date.today() - datetime.timedelta(days=1)
        else:
            patternDate = re.compile("\d{2}.\d{2}.\d{4}")
            matches = re.findall(patternDate, dateStr)
            if len(matches) != 1:
                continue
            torrentDate = datetime.datetime.strptime(
                matches[0], "%d.%m.%Y").date()

        if torrentDate <= targetDate:
            continue

        patternID = re.compile("id=(\d+)")
        matches = re.findall(patternID, torrentLink)
        if len(matches) != 1:
            continue
        kinozalID = matches[0]

        patternYear = re.compile("/ \d{4} /")
        match = re.search(patternYear, fullName)

        if not match:
            continue

        namesPart = (fullName[:match.end()]).strip().upper().replace("Ё", "Е")
        typePart = (fullName[match.end():]).strip().upper()

        year = int(filmDetail["year"])
        nameRU = filmDetail["nameRU"].upper().replace("Ё", "Е")
        nameOriginal = filmDetail["nameOriginal"].upper().replace("Ё", "Е")

        if type == "BDRip 1080p":
            if not ((nameRU in namesPart) and (nameOriginal in namesPart) and ((str(year) in namesPart) or (str(year - 1) in namesPart) or (str(year + 1) in namesPart)) and ("BDRIP" in typePart) and ("1080P" in typePart)):
                continue
            if ("HEVC" in typePart):
                continue
        elif type == "BDRemux":
            if not ((nameRU in namesPart) and (nameOriginal in namesPart) and ((str(year) in namesPart) or (str(year - 1) in namesPart) or (str(year + 1) in namesPart)) and ("REMUX" in typePart) and (("1080P" in typePart) or ("1080I" in typePart))):
                continue
        elif type == "BDRip-HEVC 1080p":
            if not ((nameRU in namesPart) and (nameOriginal in namesPart) and ((str(year) in namesPart) or (str(year - 1) in namesPart) or (str(year + 1) in namesPart)) and ("BDRIP" in typePart) and ("HEVC" in typePart) and ("1080P" in typePart)):
                continue
        else:
            return None

        if ("3D" in typePart) or ("TS" in typePart) or ("LINE" in typePart):
            continue

        try:
            response = session.get(
                "http://kinozal.tv/details.php?id={}".format(kinozalID), headers=headers)
        except:
            response = session.get(
                "http://kinozal.tv/details.php?id={}".format(kinozalID), headers=headers)

        content = response.text.replace("\n", "")
        patternTabID = re.compile(
            "<a onclick=\"showtab\({},(\d)\); return false;\" href=\"#\">Релиз</a>".format(kinozalID))
        matches = re.findall(patternTabID, content)
        if len(matches) != 1:
            continue
        try:
            response = session.get(
                "http://kinozal.tv/get_srv_details.php?id={}&pagesd={}".format(kinozalID, matches[0]), headers=headers)
        except:
            response = session.get(
                "http://kinozal.tv/get_srv_details.php?id={}&pagesd={}".format(kinozalID, matches[0]), headers=headers)
        content = response.text.replace("\n", "")
        content = content.upper()
        pmAudioOK = False

        if ("ЛИЦЕНЗИЯ" in content) or ("ITUNES" in content) or ("НЕВАФИЛЬМ" in content) or ("ПИФАГОР" in content) or ("AMEDIA" in content) or ("МОСФИЛЬМ-МАСТЕР" in content) or ("СВ-ДУБЛЬ" in content) or ("АРК-ТВ" in content) or ("APK-ТВ" in content) or ("APK-TB" in content) or ("КИРИЛЛИЦА" in content):
            pmAudioOK = True

        license = False
        if ("ЛИЦЕНЗИЯ" in content):
            license = True

        if ("RUS TRANSFER" in typePart) or ("РУ" in typePart):
            license = True

        if ("ДБ" in typePart) or ("РУ" in typePart):
            if licenseOnly:
                if license:
                    DBResults.append({"fullName": fullName, "kinozalID": kinozalID, "torrentDate": torrentDate,
                                     "seeders": seeders, "leechers": leechers, "license": license})
            else:
                DBResults.append({"fullName": fullName, "kinozalID": kinozalID, "torrentDate": torrentDate,
                                 "seeders": seeders, "leechers": leechers, "license": license})

        if ("ПМ" in typePart) and pmAudioOK and not (("ДБ" in typePart) or ("РУ" in typePart)):
            if licenseOnly:
                if license:
                    PMResults.append({"fullName": fullName, "kinozalID": kinozalID, "torrentDate": torrentDate,
                                     "seeders": seeders, "leechers": leechers, "license": license})
            else:
                PMResults.append({"fullName": fullName, "kinozalID": kinozalID, "torrentDate": torrentDate,
                                 "seeders": seeders, "leechers": leechers, "license": license})

    if len(DBResults) > 0:
        DBResults.sort(key=operator.itemgetter(
            "license", "seeders"), reverse=True)
        if DBResults[0]["seeders"] == 0:
            DBResults.sort(key=operator.itemgetter(
                "license", "torrentDate"), reverse=True)
        try:
            response = session.get(
                "http://kinozal.tv/get_srv_details.php?id={}&action=2".format(DBResults[0]["kinozalID"]), headers=headers)
        except:
            response = session.get(
                "http://kinozal.tv/get_srv_details.php?id={}&action=2".format(DBResults[0]["kinozalID"]), headers=headers)
        content = response.text.replace("\n", "")
        patternHash = re.compile("[A-F0-9]{40}")
        match = re.search(patternHash, content)

        if not match:
            return None

        return {"link": "http://dl.kinozal.tv/download.php?id={}".format(DBResults[0]["kinozalID"]), "magnet": "magnet:?xt=urn:btih:{}&dn=kinozal.tv".format(match[0]), "date": DBResults[0]["torrentDate"], "type": type, "license": DBResults[0]["license"], "seeders": DBResults[0]['seeders'], "leechers": DBResults[0]['leechers']}
    elif len(PMResults) > 0:
        PMResults.sort(key=operator.itemgetter(
            "license", "seeders"), reverse=True)
        if PMResults[0]["seeders"] == 0:
            # return None
            PMResults.sort(key=operator.itemgetter(
                "license", "torrentDate"), reverse=True)
        try:
            response = session.get(
                "http://kinozal.tv/get_srv_details.php?id={}&action=2".format(PMResults[0]["kinozalID"]), headers=headers)
        except:
            response = session.get(
                "http://kinozal.tv/get_srv_details.php?id={}&action=2".format(PMResults[0]["kinozalID"]), headers=headers)

        content = response.text.replace("\n", "")
        patternHash = re.compile("[A-F0-9]{40}")
        match = re.search(patternHash, content)

        if not match:
            return None

        return {"link": "http://dl.kinozal.tv/download.php?id={}".format(PMResults[0]["kinozalID"]), "magnet": "magnet:?xt=urn:btih:{}&dn=kinozal.tv".format(match[0]), "date": PMResults[0]["torrentDate"], "type": type, "license": PMResults[0]["license"]}
    return None


def mpResultsForDays(days):
    targetDate = datetime.date.today() - datetime.timedelta(days=days)

    tmpSet = set()
    tmpResults = {}

    for category in CATEGORIES_MP:
        try:
            print("Загрузка списка предварительно подходящих раздач 1080p c MP...")
            content = loadURLContent(
                MP_SEARCH_1080.format('', categoriesDifferent('MP', category), 0), useProxy=True)
            count = mpPagesCountForResults(content)
        except:
            raise ConnectionError(
                "Ошибка. Не удалось загрузить страницу с результатами поиска или формат данных megapeer.vip изменился.")

        i = 0
        needMore = True

        while needMore:
            pageResults = mpResultsOnPage(content)
            for result in pageResults:
                if result["date"] >= targetDate:
                    element = parseMPElement(result)
                    if not element:
                        continue
                    if (element["compareName"] in tmpSet):
                        continue
                    print("Обработка раздачи: {} ({})...".format(
                        element["nameRU"], element["year"]))
                    try:
                        elements = mpSearchSimilarElements(
                            element, categoriesDifferent('MP', category))
                        elements = mpFilmIDForElements(elements)
                    except:
                        raise ConnectionError(
                            "Ошибка. Не удалось загрузить данные похожих раздач или загрузить страницу с описанием.")
                    tmpSet.add(element["compareName"])
                    if len(elements) > 0:
                        if (tmpResults.get(elements[0]["filmID"])):
                            tmpResults[elements[0]["filmID"]].extend(elements)
                        else:
                            tmpResults[elements[0]["filmID"]] = elements
                else:
                    needMore = False
                    break
            i = i + 1
            if (i >= count):
                needMore = False
            if needMore:
                print("Загрузка списка предварительно подходящих раздач 1080p c MP...")
                try:
                    content = loadURLContent(
                        MP_SEARCH_1080.format(i, categoriesDifferent('RT', category), ""), useProxy=True)
                except:
                    raise ConnectionError(
                        "Ошибка. Не удалось загрузить страницу с результатами поиска или формат данных megapeer.vip изменился.")

    for category in CATEGORIES_MP:
        try:
            print("Загрузка списка предварительно подходящих раздач 2160p c MP...")
            content = loadURLContent(
                MP_SEARCH_2160.format('', categoriesDifferent('MP', category), 0), useProxy=True)
            count = mpPagesCountForResults(content)
        except:
            raise ConnectionError(
                "Ошибка. Не удалось загрузить страницу с результатами поиска или формат данных megapeer.vip изменился.")

        i = 0
        needMore = True

        while needMore:
            pageResults = mpResultsOnPage(content)
            for result in pageResults:
                if result["date"] >= targetDate:
                    element = parseMPElement(result)
                    if not element:
                        continue
                    if (element["compareName"] in tmpSet):
                        continue
                    print("Обработка раздачи: {} ({})...".format(
                        element["nameRU"], element["year"]))
                    try:
                        elements = mpSearchSimilarElements(
                            element, categoriesDifferent('RT', category), 2160)
                        elements = mpFilmIDForElements(elements)
                    except:
                        raise ConnectionError(
                            "Ошибка. Не удалось загрузить данные похожих раздач или загрузить страницу с описанием.")
                    tmpSet.add(element["compareName"])
                    if len(elements) > 0:
                        if (tmpResults.get(elements[0]["filmID"])):
                            tmpResults[elements[0]["filmID"]].extend(elements)
                        else:
                            tmpResults[elements[0]["filmID"]] = elements
                else:
                    needMore = False
                    break
            i = i + 1
            if (i >= count):
                needMore = False
            if needMore:
                print("Загрузка списка предварительно подходящих раздач 2160p c MP...")
                try:
                    content = loadURLContent(
                        MP_SEARCH_2160.format(i, categoriesDifferent('RT', category), ""), useProxy=True)
                except:
                    raise ConnectionError(
                        "Ошибка. Не удалось загрузить страницу с результатами поиска или формат данных megapeer.vip изменился.")

    return tmpResults


def convertMPResults(mpResults):
    targetDate = datetime.date.today() - datetime.timedelta(days=LOAD_DAYS)

    movies = []

    try:
        if KINOZAL_USERNAME:
            print("Логинимся на kinozal.tv")
            opener = kinozalAuth(KINOZAL_USERNAME, KINOZAL_PASSWORD)
        else:
            opener = None
    except:
        print("Не удалось залогиниться на kinozal.tv")
    opener = None

    for key, values in mpResults.items():
        BDDate = None
        BDDateLicense = None
        WBDate = None
        for value in values:
            if "BD" in value["type"]:
                if value["license"]:
                    if not BDDateLicense:
                        BDDateLicense = value["date"]
                    else:
                        BDDateLicense = min(BDDateLicense, value["date"])
                else:
                    if not BDDate:
                        BDDate = value["date"]
                    else:
                        BDDate = min(BDDate, value["date"])
            else:
                if not WBDate:
                    WBDate = value["date"]
                else:
                    WBDate = min(WBDate, value["date"])
        if BDDateLicense:
            if BDDateLicense < targetDate:
                continue
        elif BDDate:
            if BDDate < targetDate:
                continue
        else:
            if WBDate < targetDate:
                continue

        tr = {}

        for value in values:
            if value["type"] == "UHD BDRemux":
                if value["hdr"]:
                    if tr.get("UHD BDRemux HDR") != None:
                        if ((not tr["UHD BDRemux HDR"]["license"]) and value["license"]):
                            tr["UHD BDRemux HDR"] = value
                        elif (tr["UHD BDRemux HDR"]["license"] == False and value["license"] == False) or (tr["UHD BDRemux HDR"]["license"] == True and value["license"] == True):
                            if value["seeders"] > tr["UHD BDRemux HDR"]["seeders"]:
                                tr["UHD BDRemux HDR"] = value
                    else:
                        tr["UHD BDRemux HDR"] = value
                else:
                    if tr.get("UHD BDRemux SDR") != None:
                        if ((not tr["UHD BDRemux SDR"]["license"]) and value["license"]):
                            tr["UHD BDRemux SDR"] = value
                        elif (tr["UHD BDRemux SDR"]["license"] == False and value["license"] == False) or (tr["UHD BDRemux SDR"]["license"] == True and value["license"] == True):
                            if value["seeders"] > tr["UHD BDRemux SDR"]["seeders"]:
                                tr["UHD BDRemux SDR"] = value
                    else:
                        tr["UHD BDRemux SDR"] = value
            elif value["type"] == "BDRemux":
                if tr.get("BDRemux") != None:
                    if ((not tr["BDRemux"]["license"]) and value["license"]):
                        tr["BDRemux"] = value
                    elif (tr["BDRemux"]["license"] == False and value["license"] == False) or (tr["BDRemux"]["license"] == True and value["license"] == True):
                        if value["seeders"] > tr["BDRemux"]["seeders"]:
                            tr["BDRemux"] = value
                else:
                    tr["BDRemux"] = value
            elif value["type"] == "BDRip-HEVC":
                if tr.get("BDRip-HEVC 1080p") != None:
                    if ((not tr["BDRip-HEVC 1080p"]["license"]) and value["license"]):
                        tr["BDRip-HEVC 1080p"] = value
                    elif (tr["BDRip-HEVC 1080p"]["license"] == False and value["license"] == False) or (tr["BDRip-HEVC 1080p"]["license"] == True and value["license"] == True):
                        if value["seeders"] > tr["BDRip-HEVC 1080p"]["seeders"]:
                            tr["BDRip-HEVC 1080p"] = value
                else:
                    tr["BDRip-HEVC 1080p"] = value
            elif value["type"] == "BDRip":
                if tr.get("BDRip 1080p") != None:
                    if ((not tr["BDRip 1080p"]["license"]) and value["license"]):
                        tr["BDRip 1080p"] = value
                    elif (tr["BDRip 1080p"]["license"] == False and value["license"] == False) or (tr["BDRip 1080p"]["license"] == True and value["license"] == True):
                        if value["seeders"] > tr["BDRip 1080p"]["seeders"]:
                            tr["BDRip 1080p"] = value
                else:
                    tr["BDRip 1080p"] = value
            elif value["type"] == "WEB-DL":
                if value["resolution"] == "2160p":
                    if value["hdr"]:
                        if tr.get("WEB-DL 2160p HDR") != None:
                            if ((not tr["WEB-DL 2160p HDR"]["license"]) and value["license"]):
                                tr["WEB-DL 2160p HDR"] = value
                            elif (tr["WEB-DL 2160p HDR"]["license"] == False and value["license"] == False) or (tr["WEB-DL 2160p HDR"]["license"] == True and value["license"] == True):
                                if value["seeders"] > tr["WEB-DL 2160p HDR"]["seeders"]:
                                    tr["WEB-DL 2160p HDR"] = value
                        else:
                            tr["WEB-DL 2160p HDR"] = value
                    else:
                        if tr.get("WEB-DL 2160p SDR") != None:
                            if ((not tr["WEB-DL 2160p SDR"]["license"]) and value["license"]):
                                tr["WEB-DL 2160p SDR"] = value
                            elif (tr["WEB-DL 2160p SDR"]["license"] == False and value["license"] == False) or (tr["WEB-DL 2160p SDR"]["license"] == True and value["license"] == True):
                                if value["seeders"] > tr["WEB-DL 2160p SDR"]["seeders"]:
                                    tr["WEB-DL 2160p SDR"] = value
                        else:
                            tr["WEB-DL 2160p SDR"] = value
                else:
                    if tr.get("WEB-DL 1080p") != None:
                        if ((not tr["WEB-DL 1080p"]["license"]) and value["license"]):
                            tr["WEB-DL 1080p"] = value
                        elif (tr["WEB-DL 1080p"]["license"] == False and value["license"] == False) or (tr["WEB-DL 1080p"]["license"] == True and value["license"] == True):
                            if value["seeders"] > tr["WEB-DL 1080p"]["seeders"]:
                                tr["WEB-DL 1080p"] = value
                    else:
                        tr["WEB-DL 1080p"] = value

        if tr.get("UHD BDRemux HDR") or tr.get("UHD BDRemux SDR") or tr.get("BDRip-HEVC 1080p") or tr.get("BDRip 1080p") or tr.get("BDRemux"):
            tr.pop("WEB-DL 2160p HDR", None)
            tr.pop("WEB-DL 2160p SDR", None)
            tr.pop("WEB-DL 1080p", None)

        if tr.get("UHD BDRemux HDR"):
            tr.pop("UHD BDRemux SDR", None)

        print("Загрузка данных для фильма с ID " + values[0]["filmID"] + "...")
        flag = False
        detailse = filmDetail(values[0]["filmID"])
        if len(detailse) == 0:
            detailse = filmDetail(values[0]["filmID"])
        for genre in GENRES:
            try:
                if genre in detailse['genre']:
                    detail = detailse.copy()
                    flag = True
                    break
            except:
                print(f"Функция filmDetail для фильма " +
                      values[0]["filmID"] + " вернула пустой список")
        if not flag:
            continue
        print("Загружены данные для фильма: " + detail["nameRU"] + ".")

        if not detail.get("year"):
            print("У фильма \"" + detail["nameRU"] +
                  "\" нет даты премьеры. Пропуск фильма.")
            continue
        if detail["year"] < RELEASE_YEAR_AFTER:
            print("Фильм \"" + detail["nameRU"] +
                  "\" слишком старый. Пропуск фильма.")
            continue

        finalResult = []

        if (tr.get("WEB-DL 1080p") or tr.get("WEB-DL 2160p HDR") or tr.get("WEB-DL 2160p SDR")) and opener:
            print("Пробуем найти отсутствующий BDRip 1080p на kinozal.tv...")
            kName = detail["nameRU"]
            kNameOriginal = detail["nameOriginal"]
            if not kNameOriginal:
                kNameOriginal = kName
            try:
                kRes = kinozalSearch(
                    {"nameRU": kName, "nameOriginal": kNameOriginal, "year": detail["year"]}, opener, "BDRip 1080p")
                if kRes:
                    print("Отсутствующий BDRip 1080p найден на kinozal.tv.")
                    finalResult.append(kRes)
                    tr.pop("WEB-DL 2160p HDR", None)
                    tr.pop("WEB-DL 2160p SDR", None)
                    tr.pop("WEB-DL 1080p", None)
                    if kRes["license"]:
                        BDDateLicense = kRes["date"]
                    else:
                        BDDate = kRes["date"]
            except:
                print(
                    "Какая-то ошибка при работе с kinozal.tv. Подробная информация о проблемах ещё не добавлена в функцию.")
        if tr.get("WEB-DL 1080p"):
            finalResult.append({"link": tr["WEB-DL 1080p"]["fileLink"], "magnet": tr["WEB-DL 1080p"]["magnetLink"], "date": tr["WEB-DL 1080p"]
                               ["date"], "type": "WEB-DL 1080p", "license": tr["WEB-DL 1080p"]["license"], "page": tr['WEB-DL 1080p']['descriptionLink']})
        if tr.get("WEB-DL 2160p HDR"):
            finalResult.append({"link": tr["WEB-DL 2160p HDR"]["fileLink"], "magnet": tr["WEB-DL 2160p HDR"]["magnetLink"], "date": tr["WEB-DL 2160p HDR"]
                               ["date"], "type": "WEB-DL 2160p HDR", "license": tr["WEB-DL 2160p HDR"]["license"], "page": tr['WEB-DL 2160p HDR']['descriptionLink']})
        elif tr.get("WEB-DL 2160p SDR"):
            finalResult.append({"link": tr["WEB-DL 2160p SDR"]["fileLink"], "magnet": tr["WEB-DL 2160p SDR"]["magnetLink"], "date": tr["WEB-DL 2160p SDR"]
                               ["date"], "type": "WEB-DL 2160p SDR", "license": tr["WEB-DL 2160p SDR"]["license"], "page": tr['WEB-DL 2160p SDR']['descriptionLink']})
        if tr.get("BDRip 1080p"):
            finalResult.append({"link": tr["BDRip 1080p"]["fileLink"], "magnet": tr["BDRip 1080p"]["magnetLink"], "date": tr["BDRip 1080p"]
                               ["date"], "type": "BDRip 1080p", "license": tr["BDRip 1080p"]["license"], "page": tr['BDRip 1080p']['descriptionLink']})
        elif (tr.get("BDRip-HEVC 1080p") or tr.get("BDRemux")) and opener:
            print("Пробуем найти отсутствующий BDRip 1080p на kinozal.tv...")
            kName = detail["nameRU"]
            kNameOriginal = detail["nameOriginal"]
            if not kNameOriginal:
                kNameOriginal = kName
            try:
                kRes = kinozalSearch(
                    {"nameRU": kName, "nameOriginal": kNameOriginal, "year": detail["year"]}, opener, "BDRip 1080p")
                if kRes:
                    print("Отсутствующий BDRip 1080p найден на kinozal.tv.")
                    finalResult.append(kRes)
            except:
                print(
                    "Какая-то ошибка при работе с kinozal.tv. Подробная информация о проблемах ещё не добавлена в функцию.")
        if tr.get("BDRip-HEVC 1080p"):

            found = False

            try:
                if (not tr["BDRip-HEVC 1080p"]["license"]) and tr["BDRip 1080p"]["license"]:
                    kName = detail["nameRU"]
                    kNameOriginal = detail["nameOriginal"]
                    if not kNameOriginal:
                        kNameOriginal = kName
                    kRes = kinozalSearch({"nameRU": kName, "nameOriginal": kNameOriginal,
                                         "year": detail["year"]}, opener, "BDRip-HEVC 1080p", licenseOnly=True)
                    if kRes:
                        found = True
                        finalResult.append(kRes)
            except:
                pass

            if not found:
                finalResult.append({"link": tr["BDRip-HEVC 1080p"]["fileLink"], "magnet": tr["BDRip-HEVC 1080p"]["magnetLink"], "date": tr["BDRip-HEVC 1080p"]
                                   ["date"], "type": "BDRip-HEVC 1080p", "license": tr["BDRip-HEVC 1080p"]["license"], "page": tr['BDRip-HEVC 1080p']['descriptionLink']})
        elif (tr.get("BDRip 1080p") or tr.get("BDRemux")) and opener:
            print("Пробуем найти отсутствующий BDRip-HEVC 1080p на kinozal.tv...")
            kName = detail["nameRU"]
            kNameOriginal = detail["nameOriginal"]
            if not kNameOriginal:
                kNameOriginal = kName
            try:
                kRes = kinozalSearch({"nameRU": kName, "nameOriginal": kNameOriginal,
                                     "year": detail["year"]}, opener, "BDRip-HEVC 1080p")
                if kRes:
                    print("Отсутствующий BDRip-HEVC 1080p найден на kinozal.tv.")
                    finalResult.append(kRes)
            except:
                print(
                    "Какая-то ошибка при работе с kinozal.tv. Подробная информация о проблемах ещё не добавлена в функцию.")
        if tr.get("BDRemux"):
            found = False

            try:
                if (not tr["BDRemux"]["license"]) and tr["BDRip 1080p"]["license"]:
                    kName = detail["nameRU"]
                    kNameOriginal = detail["nameOriginal"]
                    if not kNameOriginal:
                        kNameOriginal = kName
                    kRes = kinozalSearch({"nameRU": kName, "nameOriginal": kNameOriginal,
                                         "year": detail["year"]}, opener, "BDRemux", licenseOnly=True)
                    if kRes:
                        found = True
                        finalResult.append(kRes)
            except:
                pass

            if not found:
                finalResult.append({"link": tr["BDRemux"]["fileLink"], "magnet": tr["BDRemux"]["magnetLink"], "date": tr["BDRemux"]
                                   ["date"], "type": "BDRemux", "license": tr["BDRemux"]["license"], "page": tr['BDRemux']['descriptionLink']})
        elif (tr.get("BDRip-HEVC 1080p") or tr.get("BDRip 1080p")) and opener:
            print("Пробуем найти отсутствующий BDRemux на kinozal.tv...")
            kName = detail["nameRU"]
            kNameOriginal = detail["nameOriginal"]
            if not kNameOriginal:
                kNameOriginal = kName
            try:
                kRes = kinozalSearch(
                    {"nameRU": kName, "nameOriginal": kNameOriginal, "year": detail["year"]}, opener, "BDRemux")
                if kRes:
                    print("Отсутствующий BDRemux найден на kinozal.tv.")
                    finalResult.append(kRes)
            except:
                print(
                    "Какая-то ошибка при работе с kinozal.tv. Подробная информация о проблемах ещё не добавлена в функцию.")
        if tr.get("UHD BDRemux HDR"):
            finalResult.append({"link": tr["UHD BDRemux HDR"]["fileLink"], "magnet": tr["UHD BDRemux HDR"]["magnetLink"], "date": tr["UHD BDRemux HDR"]
                               ["date"], "type": "UHD BDRemux HDR", "license": tr["UHD BDRemux HDR"]["license"], "page": tr['UHD BDRemux HDR']['descriptionLink']})
        elif tr.get("UHD BDRemux SDR"):
            finalResult.append({"link": tr["UHD BDRemux SDR"]["fileLink"], "magnet": tr["UHD BDRemux SDR"]["magnetLink"], "date": tr["UHD BDRemux SDR"]
                               ["date"], "type": "UHD BDRemux SDR", "license": tr["UHD BDRemux SDR"]["license"], "page": tr['UHD BDRemux SDR']['descriptionLink']})

        dates = []
        for torrent in finalResult:
            dates.append(torrent["date"])
        dates.sort()

        detail["torrents"] = finalResult
        detail["torrentsDate"] = dates[0]
        if BDDateLicense:
            detail["torrentsDate"] = BDDateLicense
            detail["torrentsDateType"] = "Blu-ray с официальным русским озвучиванием ★"
        elif BDDate:
            detail["torrentsDate"] = BDDate
            detail["torrentsDateType"] = "Blu-ray с официальным русским озвучиванием из VoD"
        else:
            detail["torrentsDate"] = WBDate
            detail["torrentsDateType"] = "VoD с официальным русским озвучиванием"
        movies.append(detail)

    return movies


def mpPagesCountForResults(content):
    soup = BeautifulSoup(content, 'html.parser')

    if (soup == None):
        raise ValueError(
            "Ошибка. Невозможно инициализировать HTML-парсер, что-то не так с контентом.")

    try:
        resultsGroup = soup.find("div", id="index")
    except:
        raise ValueError("Ошибка. Нет блока с торрентами.")
    if resultsGroup == None:
        raise ValueError("Ошибка. Нет блока с торрентами.")

    try:
        indexes = resultsGroup.find_all("td", class_="pager")
    except:
        raise ValueError("Ошибка. Нет блока со страницами результатов.")
    if len(indexes) == 0:
        indexes = resultsGroup.find_all("td", class_="highlight")
        if len(indexes) == 0:
            raise ValueError("Ошибка. Нет блока со страницами результатов.")
    if len(indexes) > 2:
        lastIndexStr = indexes[-2].text
    if len(indexes) == 2:
        return 1

    lastIndex = int(lastIndexStr)

    if lastIndex <= 0:
        raise ValueError("Ошибка. Неверное значение индекса страницы.")

    return lastIndex


def parseMPElement(dict):
    tmpParts = dict["name"].split("|")

    fullName = tmpParts[0].strip().upper()
    tags = set()
    tagsStr = ""

    if len(tmpParts) > 1:
        for i in range(1, len(tmpParts)):
            moreParts = tmpParts[i].split(",")
            for tmpPart in moreParts:
                tags.add(tmpPart.strip().upper())
                tagsStr = tagsStr + tmpPart.strip().upper() + " "

    if ("LINE" in tags) or ("UKR" in tags) or ("3D-VIDEO" in tags) or ("60 FPS" in tags) or (("1080" in fullName) and ("HDR" in tags)) or ("UHD BDRIP" in fullName) or ("[" in fullName) or ("]" in fullName):
        return None

    patternYear = re.compile("\((\d{4})\)")
    match = re.search(patternYear, tmpParts[0])

    if not match:
        return None

    year = match[1]
    targetYear = RELEASE_YEAR_AFTER
    if int(year) < targetYear:
        return None

    namesPart = (tmpParts[0][:match.start()]).strip()
    typePart = (tmpParts[0][match.end():]).strip().upper()
    names = namesPart.split("/")
    RU = True if len(names) == 1 else False
    nameRU = names[0].strip()
    names.pop(0)
    if len(names) > 0:
        nameOriginal = names[-1].strip()
    else:
        nameOriginal = nameRU

    if not RU:
        if not (("ЛИЦЕНЗИЯ" in tags) or ("ITUNES" in tags) or ("D" in tags) or ("D1" in tags) or ("D2" in tags) or ("НЕВАФИЛЬМ" in tags) or ("ПИФАГОР" in tags) or ("AMEDIA" in tags) or ("МОСФИЛЬМ-МАСТЕР" in tags) or ("СВ-ДУБЛЬ" in tags) or ("КИРИЛЛИЦА" in tags) or ("АРК-ТВ" in tagsStr) or ("APK-ТВ" in tagsStr) or ("APK-TB" in tagsStr) or ("HDREZKA STUDIO" in tagsStr)):
            return None

    license = True if ("ЛИЦЕНЗИЯ" in tags) else False

    if "UHD BDREMUX" in typePart:
        type = "UHD BDRemux"
    elif "BDREMUX" in typePart:
        type = "BDRemux"
    elif "BDRIP-HEVC" in typePart:
        type = "BDRip-HEVC"
    elif "BDRIP" in typePart:
        type = "BDRip"
    elif "WEB-DL " or "WEB-DLRIP" in typePart:
        type = "WEB-DL"
    elif "WEB-DL-HEVC" in typePart:
        # type = "WEB-DL-HEVC"
        type = "WEB-DL"
    else:
        return None

    hdr = False

    if "2160" in typePart:
        resolution = "2160p"
        hdr = True if ("HDR" in tags) else False
    elif "1080I" in typePart:
        resolution = "1080i"
    elif ("1080P" in typePart) or ("1080Р" in typePart):
        resolution = "1080p"
    else:
        return None

    IMAX = True if (("IMAX" in tags) or ("IMAX EDITION" in tags)) else False
    OpenMatte = True if ("OPEN MATTE" in tags) else False

    if RU:
        compareName = replaceSimilarChars(
            convertToAlfaNum(nameRU)) + " " + year
        searchPattern = "(^" + convertToAlfaNum(nameRU) + \
            " " + year + ")|(^" + compareName + ")"
    else:
        compareName = replaceSimilarChars(convertToAlfaNum(
            nameRU)) + " " + convertToAlfaNum(nameOriginal) + " " + year
        searchPattern = "(^" + convertToAlfaNum(nameRU) + " " + \
            convertToAlfaNum(nameOriginal) + " " + year + \
            ")"  # |(^" + compareName + ")"
        if len(searchPattern) > 130:
            searchPattern = "(^" + convertToAlfaNum(nameRU) + " " + \
                convertToAlfaNum(nameOriginal) + " " + year + ")"
    searchPattern = searchPattern.replace("AND", "and")
    searchPattern = searchPattern.replace("OR", "or")

    result = {"date": dict["date"], "torrentName": dict["name"], "fileLink": dict["fileLink"], "magnetLink": dict["magnetLink"], "descriptionLink": dict["descriptionLink"], "size": dict["size"], "seeders": dict["seeders"], "leechers": dict["leechers"],
              "nameOriginal": nameOriginal, "nameRU": nameRU, "compareName": compareName, "searchPattern": searchPattern, "year": year, "type": type, "resolution": resolution, "hdr": hdr, "IMAX": IMAX, "OpenMatte": OpenMatte, "license": license}

    return result


def mpSearchSimilarElements(element, category, resolution=1080):
    results = []
    searchPattern = f'''{quote(element['nameRU'], encoding='cp1251').replace("%20", "+")}+{element['nameOriginal'].strip().replace(" ", "+")}+{element['year']}'''
    if resolution == 1080:
        content = loadURLContent(MP_SEARCH_1080.format(
            searchPattern, category, 0), useProxy=True)
    else:
        content = loadURLContent(MP_SEARCH_2160.format(
            searchPattern, category, 0), useProxy=True)
    try:
        pageResults = mpResultsOnPage(content)
    except:
        return results

    for result in pageResults:
        tmpElement = parseMPElement(result)
        if not tmpElement:
            continue
        if tmpElement["compareName"] == element["compareName"]:
            results.append(tmpElement)

    return results


def mpResultsOnPage(content):
    soup = BeautifulSoup(content, 'lxml')

    if (soup == None):
        raise ValueError("{} {}".format(datetime.datetime.now(
        ), "Невозможно инициализировать HTML-парсер, что-то не так с контентом."))

    result = []

    try:
        resultsGroup = soup.find("div", id="index")
    except Exception as e:
        raise ValueError("{} {}".format(
            datetime.datetime.now(), "Нет блока с торрентами."))
    if resultsGroup == None:
        raise ValueError("{} {}".format(
            datetime.datetime.now(), "Нет блока с торрентами."))

    elements = resultsGroup.find_all('tr', class_='table_fon')

    if len(elements) == 0:
        return result

    for element in elements:
        allTDinElement = element.find_all("td", recursive=False)

        if len(allTDinElement) == 5:
            dateElement = allTDinElement[0]
            mainElement = allTDinElement[1]
            sizeElement = allTDinElement[3]
            peersElement = allTDinElement[4]
        else:
            raise ValueError("{} {}".format(
                datetime.datetime.now(), "Неверный формат блока торрента."))

        try:
            components = dateElement.text.split()
            torrentDate = datetime.date((int(components[2]) + 2000) if int(components[2]) < 2000 else int(
                components[2]), MP_MONTHS[components[1]], int(components[0]))
        except Exception as e:
            raise ValueError("{} {}".format(
                datetime.datetime.now(), "Неверный формат блока даты."))

        try:
            seeders = int(peersElement.find(
                "font", color="#008000").get_text(strip=True))
            leechers = int(peersElement.find(
                "font", color="#8b0000").get_text(strip=True))
        except Exception as e:
            raise ValueError("{} {}".format(
                datetime.datetime.now(), "Неверный формат блока пиров."))

        try:
            sizeStr = sizeElement.get_text(strip=True)

            if sizeStr.endswith("GB"):
                multiplier = 1024 * 1024 * 1024
            elif sizeStr.endswith("MB"):
                multiplier = 1024 * 1024
            elif sizeStr.endswith("KB"):
                multiplier = 1024
            else:
                multiplier = 1

            components = sizeStr.split()
            torrentSize = int(float(components[0]) * multiplier)
        except Exception as e:
            raise ValueError("{} {}".format(
                datetime.datetime.now(), "Неверный формат блока размера."))
            continue

        try:
            mainElements = mainElement.find_all("a")
            torrentFileLink = mainElements[0].get("href").strip()
            if not torrentFileLink.startswith("http"):
                torrentFileLink = urljoin(
                    MP_BASE_URL, torrentFileLink)
            torrentLink = quote(mainElements[1].get("href").strip())
            if not torrentLink.startswith("http"):
                torrentLink = urljoin(MP_BASE_URL, torrentLink)

            torrentName = mainElements[1].get_text(strip=True)
        except Exception as e:
            raise ValueError("{} {}".format(datetime.datetime.now(
            ), "Неверный формат основного блока в блоке торрента."))
        if USE_MAGNET:
            magnetLink = getMPmagnetLink(torrentLink)
        else:
            magnetLink = None

        result.append({"date": torrentDate, "name": torrentName, "fileLink": torrentFileLink, "magnetLink": magnetLink,
                      "descriptionLink": torrentLink, "size": torrentSize, "seeders": seeders, "leechers": leechers})

    return result


def getMPmagnetLink(torrentLink):
    content = loadURLContent(torrentLink, useProxy=True)
    soup = BeautifulSoup(content, 'lxml')
    try:
        resultsDownload = soup.find("div", id="download")
    except Exception as e:
        raise ValueError("{} {}".format(
            datetime.datetime.now(), "Нет блока с ссылками на загрузку."))
    if resultsDownload == None:
        raise ValueError("{} {}".format(
            datetime.datetime.now(), "Нет блока с ссылками на загрузку."))
    magnetLink = resultsDownload.find("a").get("href").strip()

    return magnetLink


def mpFilmIDForElements(elements, deep=True):
    kID = None
    for element in elements:
        content = loadURLContent(element["descriptionLink"], useProxy=True)

        patternLink = re.compile("\'http://www.kinopoisk.ru/film/(.*?)/\'")
        matches = re.findall(patternLink, content)
        if len(matches) == 1:
            kID = matches[0]
            break
        elif len(matches) > 1:
            return []

        if not kID:
            patternLink = re.compile(
                "\'http://www.kinopoisk.ru/level/1/film/(.*?)/\'")
            matches = re.findall(patternLink, content)
            if len(matches) == 1:
                kID = matches[0]
                break
            elif len(matches) > 1:
                return []

    if kID:
        for element in elements:
            element["filmID"] = kID
        return elements
    else:
        if not deep:
            return []

        try:
            for element in elements:
                content = loadURLContent(
                    element["descriptionLink"], useProxy=True)
                pageResults = mpResultsOnPage(content)
                newElements = mpFilmIDForElements(pageResults, deep=False)
                if len(newElements) > 0:
                    kID = newElements[0]["filmID"]
                    break
        except:
            return []

    if kID:
        for element in elements:
            element["filmID"] = kID
        return elements
    else:
        return []


main()


# try:
# 	exitCode = main()
# except:
# 	exitCode = 1

# sys.exit(exitCode)
