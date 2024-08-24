import json
import os
import time
import requests


class FILM:
    def __init__(self, data: dict):
        self.kp_id = data['kinopoiskId']
        self.name = data['nameRu'] if not data['nameEn'] else data['nameEn']
        self.ru_name = data['nameRu']
        self.year = str(data['year']).split(
            '-')[0] if data['type'] != 'FILM' else data['year']
        self.duration = data['filmLength']
        self.tagline = data['slogan'] if data['slogan'] is not None else '-'
        self.description = data['description']
        self.genres = [genre['genre'] for genre in data['genres']]
        self.countries = [country['country'] for country in data['countries']]
        self.age_rating = data['ratingAgeLimits']
        self.kp_rate = data['ratingKinopoisk']
        self.kp_rate_cnt = data['ratingKinopoiskVoteCount']
        self.imdb_rate = data['ratingImdb']
        self.imdb_rate_cnt = data['ratingImdbVoteCount']
        self.kp_url = data['webUrl']
        self.poster = data['posterUrl']
        self.poster_preview = data['posterUrlPreview']
        self.ratingMpaa = data['ratingMpaa']
        self.directors = []
        self.actors = []
        for person in data['staff']:
            if person['professionKey'] == 'DIRECTOR':
                self.directors.append(person['nameRu'])
            elif person['professionKey'] == 'ACTOR' and len(self.actors) < 11:
                self.actors.append(person['nameRu'])


class KP:
    def __init__(self, token, secret=None):
        self.token = token
        self.secret = secret
        self.headers = {"X-API-KEY": self.token}
        self.api_version = 'v2.2'
        self.API = 'https://kinopoiskapiunofficial.tech/api/' + self.api_version + '/'
        self.version = self.api_version + '.2-release'
        self.about = 'KinoPoiskAPI'
        self.api_version_staff = 'v1'
        self.API_staff = 'https://kinopoiskapiunofficial.tech/api/' + \
            self.api_version_staff + '/'

    def get_film(self, film_id):
        cache = CACHE().load()

        if str(film_id) in cache:
            data = {}
            for a in cache[str(film_id)]:
                data[a] = cache[str(film_id)][a]
            return FILM(data)

        for _ in range(10):
            try:
                request = requests.get(
                    self.API + 'films/' + str(film_id), headers=self.headers)
                request_json = json.loads(request.text)
                cache[str(film_id)] = request_json
                request_staff = requests.get(
                    self.API_staff + 'staff?filmId=' + str(film_id), headers=self.headers)
                request_staff_json = json.loads(request_staff.text)
                cache[str(film_id)].update({'staff': request_staff_json})
                CACHE().write(cache)
                return FILM(cache[str(film_id)])
            except json.decoder.JSONDecodeError:
                time.sleep(0.5)
                continue


class CACHE:
    def __init__(self):
        self.PATH = os.path.dirname(os.path.abspath(__file__))

    def load(self) -> dict:
        try:
            with open(self.PATH + '/cache.json', 'r') as f:
                return json.loads(f.read())
        except FileNotFoundError:
            with open(self.PATH + '/cache.json', 'w') as f:
                f.write('{}')
                return {}

    def write(self, cache: dict, indent: int = 4):
        with open(self.PATH + '/cache.json', 'w') as f:
            return json.dump(cache, f, indent=indent)
