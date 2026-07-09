import os

import pytest
import allure
from http import HTTPStatus
from jsonschema.validators import validate
from config.api_config import BASE_URL
from data.api_endpoints import BATTLE_ENDPOINT, POKEMONS_ENDPOINT, TRAINERS_ENDPOINT
from helpers.api_helpers import ApiSession
from helpers.file_helpers import load_schema


@allure.suite("API Покемонов: Битвы")
class TestBattle:
    @allure.title("Успешное получение списка битв")
    @pytest.mark.smoke
    def test_get_battles_success(self, api_session):
        with allure.step("Отправка GET-запроса на получение истории битв"):
            response = api_session.get(
                BASE_URL + BATTLE_ENDPOINT
            )
            
        with allure.step("Проверка статус-кода ответа (должен быть 200 OK)"):
            assert response.status_code == HTTPStatus.OK
            response_body = response.json()
            
        with allure.step("Валидация ответа по схеме battles.yml"):
            template = load_schema("battles.yml")
            validate(response_body, template)

    @allure.title("Битва покемонов: успешное прохождение")
    def test_run_battle_successfully(self, api_session: ApiSession, prepare_and_clear_battle: str):
        my_pokemon_id = prepare_and_clear_battle

        with allure.step("Поиск покемона-соперника"):
            ready_for_battle_response = api_session.get(
                BASE_URL + POKEMONS_ENDPOINT,
                params={"in_pokeball": 1}
            )
            assert ready_for_battle_response.status_code == HTTPStatus.OK
            body = ready_for_battle_response.json()
            suitable_pokemons = [x for x in body.get("data", []) if x["trainer_id"] != os.getenv("TRAINER_ID")]
            assert suitable_pokemons, "В базе нет чужих покемонов в покеболах для проведения битвы"
            enemy_pokemon_id = suitable_pokemons[0]["id"]

        with allure.step("Проведение битвы"):
            battle_response = api_session.post(
                BASE_URL + BATTLE_ENDPOINT,
                json={
                    "attacking_pokemon": my_pokemon_id,
                    "defending_pokemon": enemy_pokemon_id
                }
            )
            assert battle_response.status_code == HTTPStatus.OK
            battle_body = battle_response.json()
            assert battle_body.get("message") == "Битва проведена"

        with allure.step("Проверка статуса покемона после битвы"):
            check_pokemon_after_battle_response = api_session.get(
                BASE_URL + POKEMONS_ENDPOINT + f"/{my_pokemon_id}"
            )
            assert check_pokemon_after_battle_response.status_code == HTTPStatus.OK
            pokemon_body = check_pokemon_after_battle_response.json()

            if battle_body.get("result") == "Твой покемон проиграл":
                with allure.step("Битва проиграна: проверка нокаута и потери покебола"):
                    assert pokemon_body.get("status") == 0
                    assert pokemon_body.get("in_pokeball") == 0
            else:
                with allure.step("Битва выиграна: проверка активного статуса и нахождения в покеболе"):
                    assert pokemon_body.get("status") == 1
                    assert pokemon_body.get("in_pokeball") == 1