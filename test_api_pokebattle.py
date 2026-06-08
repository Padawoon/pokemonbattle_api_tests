import requests
import pytest

from http import HTTPStatus

AUTH_HEADER = {'trainer_token': 'c421d26024bc1b8de5875815f62b72ae'}
BASE_URL = 'https://api.pokemonbattle.ru/v2'
TRAINERS_ENDPOINT = '/trainers'
POKEMONS_ENDPOINT = '/pokemons'

@pytest.fixture(scope='session')
def api_session():
    with requests.Session() as poke_session:
        yield poke_session

@pytest.fixture(scope='session')
def knockout_trainer_pokemons(api_session):
    payload = {'trainer_id': 64411}
    response = api_session.get(
        BASE_URL + POKEMONS_ENDPOINT,
        headers=AUTH_HEADER,
        params=payload
    )
    response_body = response.json()
    pokemons = [pokemon['id'] for pokemon in response_body['data'] if pokemon.get('status') == 1]
    for pok_id in pokemons:
        api_session.post(
            BASE_URL + POKEMONS_ENDPOINT + '/knockout',
            headers=AUTH_HEADER,
            json={'pokemon_id': str(pok_id)}
        )
    response = api_session.get(
        BASE_URL + POKEMONS_ENDPOINT,
        headers=AUTH_HEADER,
        params=payload
    )
    response_body = response.json()
    updated_pokemons = [pokemon for pokemon in response_body['data'] if pokemon['id'] in pokemons]
    for pokemon in updated_pokemons:
        assert pokemon.get('status') == 0

@pytest.fixture(scope='session')
def create_pokemon(api_session, knockout_trainer_pokemons):
    response = api_session.post(
        BASE_URL + POKEMONS_ENDPOINT,
        headers=AUTH_HEADER,
        json={'name': 'generate',
              'photo_id': -1}
    )
    response_body = response.json()
    return response_body

class TestGetTrainers:
    def test_get_trainers_by_city_success(self, api_session):
        payload = {'city': 'Subotica'}
        response = api_session.get(
            BASE_URL + TRAINERS_ENDPOINT,
            headers=AUTH_HEADER, params=payload
        )
        assert response.status_code == HTTPStatus.OK
        response_body = response.json()
        assert response_body['data'][0]['city'] == payload['city']

    def test_get_trainer_by_id_success(self, api_session):
        payload = {'trainer_id': 64411}
        response = api_session.get(
            BASE_URL + TRAINERS_ENDPOINT,
            headers=AUTH_HEADER, params=payload
        )
        assert response.status_code == HTTPStatus.OK
        response_body = response.json()
        assert int(response_body['data'][0]['id']) == payload['trainer_id']

    def test_get_trainers_by_id_sorted_level_desc_success(self, api_session):
        payload = {'city': 'Moscow', 'sort': 'desc_level'}
        response = api_session.get(
            BASE_URL + TRAINERS_ENDPOINT,
            headers=AUTH_HEADER, params=payload
        )
        assert response.status_code == HTTPStatus.OK
        response_body = response.json()
        cities = {trainer['city'].lower() for trainer in response_body['data']}
        levels = [int(trainer['level']) for trainer in response_body['data']]
        assert len(response_body['data']) > 0
        assert cities == {payload['city'].lower()}
        assert levels == sorted(levels, reverse=True)

class TestPokemonCrud:
    def test_patch_pokemon_success(self, api_session, create_pokemon):
        pokemon_id = create_pokemon.get('id')
        response = api_session.patch(
            BASE_URL + POKEMONS_ENDPOINT + f'/{pokemon_id}',
            headers=AUTH_HEADER,
            json={'name': 'Zhizha'}
        )
        response_body = response.json()
        assert response.status_code == HTTPStatus.OK
        assert response_body['message'] == 'Информация о покемоне обновлена'

    def test_get_updated_pokemon_success(self, api_session, create_pokemon):
        payload = {'trainer_id': 64411}
        pokemon_id = create_pokemon.get('id')
        response = api_session.get(
            BASE_URL + POKEMONS_ENDPOINT + f'/{pokemon_id}',
            headers=AUTH_HEADER,
            params=payload
        )
        response_body = response.json()
        assert response_body['name'] == 'Zhizha'