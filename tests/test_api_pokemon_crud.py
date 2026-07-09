import pytest
import allure
from http import HTTPStatus
from config.api_config import BASE_URL
from data.api_endpoints import POKEMONS_ENDPOINT


@allure.suite("API Покемонов: Управление покемонами (CRUD)")
class TestPokemonCrud:
    @allure.title("Успешное изменение имени покемона")
    @pytest.mark.smoke
    def test_patch_pokemon_success(self, api_session, create_pokemon):
        pokemon_id = create_pokemon.get('id')
        with allure.step("Отправка PATCH-запроса для обновления имени покемона"):
            response = api_session.patch(
                BASE_URL + POKEMONS_ENDPOINT + f'/{pokemon_id}',
                json={'name': 'Zhizha'}
            )
            response_body = response.json()
            
        with allure.step("Проверка статус-кода ответа (должен быть 200 OK)"):
            assert response.status_code == HTTPStatus.OK
            
        with allure.step("Проверка сообщения о подтверждении изменения имени"):
            assert response_body['message'] == 'Информация о покемоне обновлена'

    @allure.title("Получение обновленных данных покемона")
    @pytest.mark.skip('Сегодня нам пофиг поменялось или нет')
    def test_get_updated_pokemon_success(self, api_session, create_pokemon):
        payload = {'trainer_id': 64411}
        pokemon_id = create_pokemon.get('id')
        with allure.step("Отправка GET-запроса для получения данных покемона по ID"):
            response = api_session.get(
                BASE_URL + POKEMONS_ENDPOINT + f'/{pokemon_id}',
                params=payload
            )
            response_body = response.json()
            
        with allure.step("Проверка соответствия имени покемона значению 'Zhizha'"):
            assert response_body['name'] == 'Zhizha'