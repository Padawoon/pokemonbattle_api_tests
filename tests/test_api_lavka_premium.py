import json
import os
from http import HTTPStatus

import allure
import pytest
from allure_commons.types import AttachmentType

from config.api_config import LAVKA_BASE_URL, BASE_URL
from data.api_endpoints import PAYMENTS_ENDPOINT

@allure.suite("Проверки покупки премиума")
class TestPremium:
    @pytest.mark.positive
    def test_buy_premium_success(self, api_session, check_and_cancel_premium):
        with allure.step("Отправка POST-запроса на покупку премиума для тренера"):
            test_premium_days = 15
            response = api_session.post(
                LAVKA_BASE_URL + PAYMENTS_ENDPOINT,
                json={
                    "order_type": "premium",
                    "details": {
                        "card_number": os.getenv("VISA"),
                        "secure_code": os.getenv("SECURE_CODE"),
                        "card_name": os.getenv("CARD_NAME"),
                        "card_cvv": os.getenv("SUCCESS_CVV"),
                        "card_actual": os.getenv("DUE_DATE"),
                        "days": test_premium_days
                    }
                }
            )
            with allure.step("Проверка статус-кода ответа на покупку премиума"):
                assert response.status_code == HTTPStatus.OK
            body = response.json()
            expected_message = "Транзакция успешна"
            with allure.step("Проверка ответа об успешной транзакции"):
                assert body.get("message") == expected_message
            with allure.step(f"Проверка купленных дней премиума, должно быть {test_premium_days}"):
                assert body.get("days") == test_premium_days

        with allure.step("Проверка, что статус премиума успешно обновился в профиле тренера"):
            response = api_session.get(BASE_URL + "/me")
            assert response.status_code == HTTPStatus.OK
            body = response.json()
            assert body.get("data")[0].get("is_premium")

            attach = json.dumps(body, indent=4, ensure_ascii=False)

            allure.attach(
                body=attach,
                name="JSON-ответ сервера",
                attachment_type=AttachmentType.JSON
            )