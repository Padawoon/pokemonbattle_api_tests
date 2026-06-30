import pytest
from http import HTTPStatus
from jsonschema.validators import validate
from config.api_config import BASE_URL
from data.api_endpoints import BATTLE_ENDPOINT
from helpers.file_helpers import load_schema


class TestBattle:
    @pytest.mark.smoke
    def test_get_battles_success(self, api_session):
        response = api_session.get(
            BASE_URL + BATTLE_ENDPOINT
        )
        assert response.status_code == HTTPStatus.OK
        response_body = response.json()
        template = load_schema("battles.yml")
        validate(response_body, template)