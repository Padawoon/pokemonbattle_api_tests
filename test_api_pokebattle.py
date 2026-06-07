import requests
import pytest

from http import HTTPStatus

AUTH_HEADER = {'trainer_token': 'c421d26024bc1b8de5875815f62b72ae'}
BASE_URL = 'https://api.pokemonbattle.ru/v2'
TRAINERS_ENDPOINT = '/trainers'
POKEMONS_ENDPOINT = '/pokemons'

@pytest.fixture(scope="session")
def api_session():
    with requests.Session() as poke_session:
        yield poke_session

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