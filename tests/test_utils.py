import json
import mock
import pytest

from .context import aiociscospark


class FakeCredentials(aiociscospark.Credentials):
    def __init__(self, d=None):
        self.storage = dict()
        self.update(d or {})

    def _transform_key(self, key):
        return key


class TestCredentials:
    @pytest.fixture(scope='function', autouse=True)
    def setup(self, credentials):
        self.creds = FakeCredentials(credentials)

    def test_get_client_id(self, client_id):
        assert self.creds['client_id'] == client_id

    def test_set_client_id(self):
        value = 'value'
        self.creds['client_id'] = value
        assert self.creds['client_id'] == value

    def test_get_client_secret(self, client_secret):
        assert self.creds['client_secret'] == client_secret

    def test_set_client_secret(self):
        value = 'value'
        self.creds['client_secret'] = value
        assert self.creds['client_secret'] == value

    def test_get_access_token(self, access_token):
        assert self.creds['access_token'] == access_token

    def test_set_access_token(self):
        value = 'value'
        self.creds['access_token'] = value
        assert self.creds['access_token'] == value

    def test_get_refresh_token(self, refresh_token):
        assert self.creds['refresh_token'] == refresh_token

    def test_set_refresh_token(self):
        value = 'value'
        self.creds['refresh_token'] = value
        assert self.creds['refresh_token'] == value


def test_refresh_access_token(client_id, client_secret, refresh_token):
    payload = {
        'access_token': 'new_access_token',
        'expires_in': 1209599,
        'refresh_token': 'refresh_token',
        'refresh_token_expires_in': 7775553
    }

    class FakeConn:
        def __init__(self, *args, **kwargs):
            self._args = args
            self._kwargs = kwargs

            self._request_call_args = None
            self._request_call_kwargs = None

        def request(self, *args, **kwargs):
            self._request_call_args = args
            self._request_call_kwargs = kwargs

        def getresponse(self):
            class FakeResp:
                def read(self):
                    return json.dumps(payload).encode()

            return FakeResp()

    with mock.patch('aiociscospark.utils.HTTPSConnection', side_effect=FakeConn):
        data = aiociscospark.utils.refresh_access_token(client_id, client_secret, refresh_token)
    assert data == payload


def test_refresh_access_token_raises_config_error(client_secret, refresh_token):
    with pytest.raises(ValueError):
        aiociscospark.utils.refresh_access_token(None, client_secret, refresh_token)
