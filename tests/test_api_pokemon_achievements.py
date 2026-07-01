import pytest
from http import HTTPStatus
from jsonschema.validators import validate
from config.api_config import BASE_URL
from data.api_endpoints import ACHIEVEMENTS
from helpers.file_helpers import load_schema
from deepdiff import DeepDiff
from pytest_check import check

class TestAchievements:
    @pytest.mark.smoke
    def test_get_achievements_success(self, api_session):
        response = api_session.get(
            BASE_URL + ACHIEVEMENTS
        )
        assert response.status_code == HTTPStatus.OK
        response_body = response.json()
        template = load_schema("achievements.yml")
        validate(response_body, template)
        body_template = {
            "data": [
                {"slug": "beginning", "is_reached": False},
                {"slug": "out_of_battles", "is_reached": False},
                {"slug": "self_knockout", "is_reached": False},
                {"slug": "max_level"},
                {"slug": "one_vs_seven", "is_reached": False},
                {"slug": "five_battles", "is_reached": False},
                {"slug": "three_defends", "is_reached": False}
            ]
        }
        compare = DeepDiff(
            body_template,
            response_body,
            exclude_regex_paths=[
                r"root\['data'\]\[\d+\]\['is_reached'\]"
            ])
        assert not compare, compare

    @pytest.mark.negative
    def test_get_achievements_negative(self, api_session):
        payload = {'is_reached': 'ololo'}
        response = api_session.get(
            BASE_URL + ACHIEVEMENTS,
            params=payload
        )
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        body = response.json()

        check.equal(body.get('status'), 'error')
        expected_message = 'Input should be a valid boolean, unable to interpret input'

        with check:
            assert expected_message in body.get('message')
