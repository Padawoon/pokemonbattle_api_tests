import json
import os
from http import HTTPStatus

import allure
import pytest
from allure_commons.types import AttachmentType
from pytest_check import check

from config.api_config import LAVKA_BASE_URL, BASE_URL
from data.api_endpoints import PAYMENTS_ENDPOINT

@allure.suite("Проверки покупки премиума")
class TestPremium:
    @pytest.mark.positive
    @allure.title("Успешная покупка премиума")
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

    @pytest.mark.negative
    @pytest.mark.parametrize(
        "field_name, field_value",
        [
            ("secure_code", "123456"),
            ("card_cvv", os.getenv("FAIL_CVV"))
        ], ids=[
            "Невалидный код подтверждения из SMS",
            f"Недостаточно средств, CVV-код {os.getenv("FAIL_CVV")}"
        ]
    )

    def test_buy_premium_fail(self, api_session, check_and_cancel_premium, field_name, field_value):
        case_titles = {
            "secure_code": "Неуспешная покупка премиума: Невалидный код подтверждения из SMS",
            "card_cvv": f"Неуспешная покупка премиума: Недостаточно средств, CVV-код {field_value}"
        }
        allure.dynamic.title(case_titles.get(field_name, "Неуспешная покупка премиума"))

        test_premium_days = 15
        request_body = {
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

        request_body["details"][field_name] = field_value

        with allure.step("Отправка POST-запроса на покупку премиума для тренера"):
            response = api_session.post(
                LAVKA_BASE_URL + PAYMENTS_ENDPOINT,
                json=request_body
            )
            # вообще по-хорошему на недостаток средств должен приходить 402 Payment Required,
            # но в тренажёре на всё один ответ 400, так что имеем то, что имеем
            assert response.status_code == HTTPStatus.BAD_REQUEST
