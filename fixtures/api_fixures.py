import pytest
import requests
import os

@pytest.fixture(scope='session')
def api_session():
    with requests.Session() as poke_session:
        poke_session.headers.update({'trainer_token': os.getenv('USER_TRAINER_TOKEN')})
        yield poke_session