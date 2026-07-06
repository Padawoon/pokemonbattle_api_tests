from http import HTTPStatus

import pytest
import requests
import os

from config.api_config import BASE_URL
from data.api_endpoints import POKEMONS_ENDPOINT, TRAINERS_ENDPOINT
from helpers.api_helpers import ApiSession


@pytest.fixture(scope='session')
def api_session():
    with requests.Session() as poke_session:
        poke_session.headers.update({'trainer_token': os.getenv('USER_TRAINER_TOKEN')})
        yield ApiSession(poke_session)


@pytest.fixture()
def prepare_and_clear_battle(api_session: ApiSession):
    response = api_session.get(
        BASE_URL + POKEMONS_ENDPOINT,
        params={
            "trainer_id": os.getenv("TRAINER_ID"),
            "in_pokeball": 1
        }
    )
    body = response.json()

    pokemons_in_pokeballs = body.get("data") or []

    if pokemons_in_pokeballs:
        pokemon_id = pokemons_in_pokeballs[0]["id"]
    else:
        response = api_session.get(
            BASE_URL + POKEMONS_ENDPOINT,
            params={
                "trainer_id": os.getenv("TRAINER_ID"),
                "status": 1,
                "in_pokeball": 0
            }
        )
        assert response.status_code == HTTPStatus.OK
        body = response.json()

        alive_pokemons_not_in_pokeballs = body.get("data") or []

        if alive_pokemons_not_in_pokeballs:
            pokemon_id = alive_pokemons_not_in_pokeballs[0]["id"]
            response = api_session.post(
                BASE_URL + TRAINERS_ENDPOINT + "/add_pokeball",
                json={
                    "pokemon_id": pokemon_id
                }
            )
            assert response.status_code == HTTPStatus.OK
        else:
            response = api_session.post(
                BASE_URL + POKEMONS_ENDPOINT,
                json={
                    "name": "generate",
                    "photo_id": -1
                }
            )
            body = response.json()
            pokemon_id = body["id"]
            response = api_session.post(
                BASE_URL + TRAINERS_ENDPOINT + "/add_pokeball",
                json={
                    "pokemon_id": pokemon_id
                }
            )
            assert response.status_code == HTTPStatus.OK

    yield pokemon_id

    api_session.post(
        BASE_URL + POKEMONS_ENDPOINT + "/knockout",
        json={
            "pokemon_id": pokemon_id
        }
    )