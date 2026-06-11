import pytest
from config.api_config import BASE_URL
from data.api_endpoints import POKEMONS_ENDPOINT


@pytest.fixture(scope='session')
def knockout_trainer_pokemons(api_session):
    payload = {'trainer_id': 64411}
    response = api_session.get(
        BASE_URL + POKEMONS_ENDPOINT,
        params=payload
    )
    response_body = response.json()
    pokemons = [pokemon['id'] for pokemon in response_body['data'] if pokemon.get('status') == 1]
    for pok_id in pokemons:
        api_session.post(
            BASE_URL + POKEMONS_ENDPOINT + '/knockout',
            json={'pokemon_id': str(pok_id)}
        )
    response = api_session.get(
        BASE_URL + POKEMONS_ENDPOINT,
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
        json={'name': 'generate',
              'photo_id': -1}
    )
    response_body = response.json()
    return response_body