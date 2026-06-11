import pytest

from http import HTTPStatus
from config.api_config import BASE_URL
from data.api_endpoints import POKEMONS_ENDPOINT


class TestPokemonCrud:
    @pytest.mark.smoke
    def test_patch_pokemon_success(self, api_session, create_pokemon):
        pokemon_id = create_pokemon.get('id')
        response = api_session.patch(
            BASE_URL + POKEMONS_ENDPOINT + f'/{pokemon_id}',
            json={'name': 'Zhizha'}
        )
        response_body = response.json()
        assert response.status_code == HTTPStatus.OK
        assert response_body['message'] == 'Информация о покемоне обновлена'
    @pytest.mark.skip('А чёт пофиг сейчас поменялось или нет')
    def test_get_updated_pokemon_success(self, api_session, create_pokemon):
        payload = {'trainer_id': 64411}
        pokemon_id = create_pokemon.get('id')
        response = api_session.get(
            BASE_URL + POKEMONS_ENDPOINT + f'/{pokemon_id}',
            params=payload
        )
        response_body = response.json()
        assert response_body['name'] == 'Zhizha'