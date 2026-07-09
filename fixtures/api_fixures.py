import pytest
import requests
import os
from helpers.api_helpers import ApiSession

@pytest.fixture(scope='session')
def api_session():
    with requests.Session() as poke_session:
        poke_session.headers.update({'trainer_token': os.getenv('USER_TRAINER_TOKEN')})
        yield ApiSession(poke_session)