import pytest
import allure
from http import HTTPStatus
from jsonschema.validators import validate
from config.api_config import BASE_URL
from data.api_endpoints import BATTLE_ENDPOINT
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