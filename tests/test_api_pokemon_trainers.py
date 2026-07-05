import pytest
import allure
from http import HTTPStatus
from config.api_config import BASE_URL
from data.api_endpoints import POKEMONS_ENDPOINT, TRAINERS_ENDPOINT


@allure.suite("API Покемонов: Тренеры")
class TestGetTrainers:
    @allure.title("Получение списка тренеров по городу")
    @pytest.mark.smoke
    def test_get_trainers_by_city_success(self, api_session):
        payload = {'city': 'Subotica'}
        with allure.step("Отправка GET-запроса на получение списка тренеров по городу Subotica"):
            response = api_session.get(
                BASE_URL + TRAINERS_ENDPOINT,
                params=payload
            )
            
        with allure.step("Проверка статус-кода ответа (должен быть 200 OK)"):
            assert response.status_code == HTTPStatus.OK
            response_body = response.json()
            
        with allure.step("Проверка, что город первого тренера в результатах — Subotica"):
            assert response_body['data'][0]['city'] == payload['city']

    @allure.title("Получение информации о тренере по его ID")
    @pytest.mark.smoke
    def test_get_trainer_by_id_success(self, api_session):
        payload = {'trainer_id': 64411}
        with allure.step("Отправка GET-запроса на получение тренера по ID 64411"):
            response = api_session.get(
                BASE_URL + TRAINERS_ENDPOINT,
                params=payload
            )
            
        with allure.step("Проверка статус-кода ответа (должен быть 200 OK)"):
            assert response.status_code == HTTPStatus.OK
            response_body = response.json()
            
        with allure.step("Проверка соответствия ID тренера в полученных данных"):
            assert int(response_body['data'][0]['id']) == payload['trainer_id']

    @allure.title("Сортировка тренеров по убыванию уровня")
    @pytest.mark.regress
    def test_get_trainers_by_id_sorted_level_desc_success(self, api_session):
        payload = {'city': 'Moscow', 'sort': 'desc_level'}
        with allure.step("Отправка GET-запроса на получение тренеров в Москве с сортировкой по убыванию уровня"):
            response = api_session.get(
                BASE_URL + TRAINERS_ENDPOINT,
                params=payload
            )
            
        with allure.step("Проверка статус-кода ответа (должен быть 200 OK)"):
            assert response.status_code == HTTPStatus.OK
            response_body = response.json()
            
        with allure.step("Сбор городов и уровней тренеров из ответа"):
            cities = {trainer['city'].lower() for trainer in response_body['data']}
            levels = [int(trainer['level']) for trainer in response_body['data']]
            
        with allure.step("Проверка корректности фильтрации по городу и сортировки по убыванию уровня"):
            assert len(response_body['data']) > 0
            assert cities == {payload['city'].lower()}
            assert levels == sorted(levels, reverse=True)

