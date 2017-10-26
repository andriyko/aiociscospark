"""
Third-party fixtures:
    event_loop - provided by https://pypi.python.org/pypi/pytest-asyncio
"""
import mock
import pytest

from aiohttp.client_exceptions import ServerConnectionError, ServerTimeoutError
from aioresponses import aioresponses

from .context import aiociscospark


class TestHTTPClient:
    @pytest.fixture(scope='function', autouse=True)
    def setup(self, credentials, event_loop):
        self.client = aiociscospark.HTTPClient(credentials, loop=event_loop)

    def test_initialization(self, event_loop, credentials):
        assert self.client._loop == event_loop
        assert self.client._registered_response_handlers == {}
        assert self.client._creds is credentials
        assert self.client._conn_timeout is None
        assert self.client._read_timeout == 300

    def test_default_headers(self, access_token):
        assert self.client.default_headers == {
            'Accept': 'application/json',
            'Content-Type': 'application/json;charset=utf-8',
            'Authorization': f'Bearer {access_token}'
        }

    def test_session_is_lazy_loaded(self):
        assert getattr(self.client, '_lazy_session', None) is None
        session1 = self.client.session
        session2 = self.client.session
        assert session1 is session2 is getattr(self.client, '_lazy_session')

    def test_session_initialization(self, access_token):
        _ = self.client.session  # noqa
        assert self.client.session._default_headers == {
            'Accept': 'application/json',
            'Content-Type': 'application/json;charset=utf-8',
            'Authorization': f'Bearer {access_token}'
        }
        assert self.client.session._loop == self.client._loop
        assert self.client.session._conn_timeout == self.client._conn_timeout
        assert self.client.session._read_timeout == self.client._read_timeout

    def test_request(self, event_loop, test_url, people_list, response_headers):
        with aioresponses() as m:
            m.get(test_url, payload=people_list, headers=response_headers)
            resp = event_loop.run_until_complete(self.client.request('GET', test_url))
            data = event_loop.run_until_complete(resp.json())
        assert data == people_list

    def test_request_reuses_session_object(self, event_loop, test_url, response_headers,
                                           people_list):
        with aioresponses() as m:
            m.get(test_url, payload=people_list, headers=response_headers)
            event_loop.run_until_complete(self.client.request('GET', test_url))

        session1 = self.client._lazy_session

        with aioresponses() as m:
            m.get(test_url, payload=people_list, headers=response_headers)
            event_loop.run_until_complete(self.client.request('GET', test_url))

        session2 = self.client._lazy_session

        assert self.client._lazy_session == session1 == session2
        assert not self.client._lazy_session.closed

    def test_request_with_params(self, event_loop, test_url, user_info, response_headers):
        person_id = user_info['id']
        url = f'{test_url}/{person_id}'
        with aioresponses() as m:
            m.get(url, payload=user_info, headers=response_headers)
            resp = event_loop.run_until_complete(self.client.request('GET', url))
            data = event_loop.run_until_complete(resp.json())
        assert data == user_info

    def test_request_invokes_correct_error_handlers(self, event_loop, test_url, people_list,
                                                    response_headers, fake_error_handler):
        self.client.register_response_handler(401, fake_error_handler.handler)

        with aioresponses() as m:
            # First attempt - we got "[401] Unauthorized" response.
            # There is appropriate response handler that we assume should refresh the access token.
            m.get(test_url, status=401)
            # After the response handler worked out, we perform second attempt.
            m.get(test_url, payload=people_list, headers=response_headers)
            resp = event_loop.run_until_complete(self.client.request('GET', test_url))
            data = event_loop.run_until_complete(resp.json())
        assert data == people_list
        assert fake_error_handler.done, 'Error was not handled'

    def test_request_raises_response_error(self, event_loop, test_url, response_headers):
        with aioresponses() as m:
            # "[401] Unauthorized" response. There is no error handler registered.
            m.get(test_url, status=401, headers=response_headers)
            with pytest.raises(aiociscospark.exceptions.SparkResponseError):
                event_loop.run_until_complete(self.client.request('GET', test_url))

    def test_request_succeeds_after_connection_error(self, event_loop, test_url, people_list,
                                                     fake_resp):
        side_effects = [ServerConnectionError, ServerTimeoutError, fake_resp]
        with mock.patch.object(self.client.session, 'request',
                               side_effect=side_effects) as session_request_mock:
            resp = event_loop.run_until_complete(self.client.request('GET', test_url))
            data = event_loop.run_until_complete(resp.json())
        assert data == people_list
        assert session_request_mock.call_count == len(side_effects)

    def test_request_closes_session_on_error(self, event_loop, test_url, user_info, response_headers,
                                             response_not_found_error):
        person_id = user_info['id']
        url = f'{test_url}/{person_id}'
        with aioresponses() as m:
            m.get(url, status=404, payload=response_not_found_error, headers=response_headers)
            with pytest.raises(aiociscospark.exceptions.SparkResponseError):
                event_loop.run_until_complete(self.client.request('GET', url))
        assert self.client._lazy_session.closed

    @pytest.mark.parametrize('side_effect', [ServerTimeoutError, Exception])
    def test_request_closes_session_on_exception(self, event_loop, test_url, user_info, side_effect):
        person_id = user_info['id']
        url = f'{test_url}/{person_id}'
        with mock.patch.object(self.client.session, 'request',
                               side_effect=side_effect), \
             mock.patch.object(self.client, 'close_session',
                               side_effect=self.client.close_session) as close_session_mock:  # noqa
            with pytest.raises(side_effect):
                event_loop.run_until_complete(self.client.request('GET', url))
        close_session_mock.assert_called_once_with()
        assert self.client._lazy_session.closed

    def test__handle_error_raises_error(self, event_loop, fake_resp_error):
        with pytest.raises(aiociscospark.exceptions.SparkResponseError) as excinfo:
            resp = event_loop.run_until_complete(fake_resp_error)
            event_loop.run_until_complete(self.client._handle_error(resp, 1))
        assert excinfo.value.message == 'Person not found'

    def test__handle_error_raises_error_if_no_more_attempts(self, event_loop, fake_resp_error):
        with pytest.raises(aiociscospark.exceptions.SparkResponseError) as excinfo:
            resp = event_loop.run_until_complete(fake_resp_error)
            event_loop.run_until_complete(
                self.client._handle_error(resp, self.client.max_retries + 1)
            )
        assert excinfo.value.message == 'Person not found'

    def test__handle_error_raises_rate_limit_error(self, event_loop, fake_resp_error_rate_limit):
        with pytest.raises(aiociscospark.exceptions.SparkRateLimitExceeded) as excinfo:
            resp = event_loop.run_until_complete(fake_resp_error_rate_limit)
            event_loop.run_until_complete(self.client._handle_error(resp, 1))
        assert excinfo.value.text == ''
        assert excinfo.value.retry_after == 60

    def test__handle_error_invokes_registered_handlers(self, event_loop, fake_resp_error,
                                                       fake_error_handler):
        self.client.register_response_handler(404, fake_error_handler.handler)
        resp = event_loop.run_until_complete(fake_resp_error)
        event_loop.run_until_complete(self.client._handle_error(resp, 1))
        assert fake_error_handler.done, 'Error was not handled'

    def test__handle_error_invokes_registered_coro_handlers(self, event_loop, fake_resp_error,
                                                            async_fake_error_handler):
        self.client.register_response_handler(404, async_fake_error_handler.handler)
        resp = event_loop.run_until_complete(fake_resp_error)
        event_loop.run_until_complete(self.client._handle_error(resp, 1))
        assert async_fake_error_handler.done, 'Error was not handled'

    def test__is_valid_response_if_response_not_received(self, event_loop):
        with pytest.raises(aiociscospark.exceptions.SparkResponseNotReceived), \
             mock.patch.object(self.client, '_handle_error') as _handle_error_mock:  # noqa
            is_valid_resp = event_loop.run_until_complete(self.client._is_valid_response(None))
            assert not is_valid_resp
        assert not _handle_error_mock.called

    def test__is_valid_response_if_response_is_valid(self, event_loop, fake_resp):
        resp = event_loop.run_until_complete(fake_resp)
        result = event_loop.run_until_complete(self.client._is_valid_response(resp))
        assert result

    def test__is_valid_response_if_response_is_invalid(self, event_loop, fake_resp_error):
        resp = event_loop.run_until_complete(fake_resp_error)
        with pytest.raises(aiociscospark.exceptions.SparkResponseError) as excinfo:
            is_valid_resp = event_loop.run_until_complete(self.client._is_valid_response(resp))
            assert not is_valid_resp
        assert excinfo.value.status == resp.status

    def test_get_response_handler(self):
        def handle_not_found_error(resp):
            pass

        async def handle_permission_denied_error(resp):
            pass

        self.client.register_response_handler(403, handle_permission_denied_error)
        self.client.register_response_handler(404, handle_not_found_error)
        assert self.client.get_response_handler(403) is handle_permission_denied_error
        assert self.client.get_response_handler(404) is handle_not_found_error
        assert self.client.get_response_handler(401) is None

    def test_register_response_handler(self):
        # function
        def handle_not_found_error(resp):
            pass

        # coro function
        async def handle_permission_denied_error(resp):
            pass

        # method
        def handle_unauthorized_error(self, resp):
            pass
        setattr(self.client, 'handle_unauthorized_error', handle_unauthorized_error)

        self.client.register_response_handler(401, 'handle_unauthorized_error')
        self.client.register_response_handler(403, handle_permission_denied_error)
        self.client.register_response_handler(404, handle_not_found_error)

        assert self.client._registered_response_handlers == {
            401: handle_unauthorized_error,
            403: handle_permission_denied_error,
            404: handle_not_found_error,
        }

    def test_register_response_handlers(self):
        # function
        def handle_not_found_error(resp):
            pass

        # coro function
        async def handle_permission_denied_error(resp):
            pass

        # method
        def handle_unauthorized_error(self, resp):
            pass
        setattr(self.client, 'handle_unauthorized_error', handle_unauthorized_error)
        self.client._response_handlers[401] = 'handle_unauthorized_error'
        self.client._response_handlers[403] = handle_permission_denied_error
        self.client._response_handlers[404] = handle_not_found_error
        self.client.register_response_handlers()
        assert self.client._registered_response_handlers == {
            401: handle_unauthorized_error,
            403: handle_permission_denied_error,
            404: handle_not_found_error,
        }

    @pytest.mark.parametrize('num_attempts, expected_result', [
        (1, False),
        (4, True)
    ])
    def test_has_no_more_attempts(self, num_attempts, expected_result):
        assert self.client.has_no_more_attempts(num_attempts) is expected_result

    def test_get(self, test_url):
        kwargs = {
            'a': 1,
            'b': 2,
        }
        with mock.patch.object(self.client, 'request') as request_mock:
            self.client.get(test_url, **kwargs)
        request_mock.assert_called_once_with('GET', test_url, **kwargs)

    def test_head(self, test_url):
        kwargs = {
            'a': 1,
            'b': 2,
        }
        with mock.patch.object(self.client, 'request') as request_mock:
            self.client.head(test_url, **kwargs)
        request_mock.assert_called_once_with('HEAD', test_url, **kwargs)

    def test_post(self, test_url):
        kwargs = {
            'a': 1,
            'b': 2,
        }
        with mock.patch.object(self.client, 'request') as request_mock:
            self.client.post(test_url, **kwargs)
        request_mock.assert_called_once_with('POST', test_url, **kwargs)

    def test_put(self, test_url):
        kwargs = {
            'a': 1,
            'b': 2,
        }
        with mock.patch.object(self.client, 'request') as request_mock:
            self.client.put(test_url, **kwargs)
        request_mock.assert_called_once_with('PUT', test_url, **kwargs)

    def test_patch(self, test_url):
        kwargs = {
            'a': 1,
            'b': 2,
        }
        with mock.patch.object(self.client, 'request') as request_mock:
            self.client.patch(test_url, **kwargs)
        request_mock.assert_called_once_with('PATCH', test_url, **kwargs)

    def test_delete(self, test_url):
        kwargs = {
            'a': 1,
            'b': 2,
        }
        with mock.patch.object(self.client, 'request') as request_mock:
            self.client.delete(test_url, **kwargs)
        request_mock.assert_called_once_with('DELETE', test_url, **kwargs)

    def test_handle_unauthorized_response_with_response_handler(self, event_loop, response_headers,
                                                                test_url, people_list):
        self.client.register_response_handlers()
        with aioresponses() as m,\
             mock.patch('aiociscospark.http_client.refresh_access_token') as refresh_token_mock:  # noqa
            m.get(test_url, status=401, headers=response_headers)
            m.get(test_url, payload=people_list, headers=response_headers)
            event_loop.run_until_complete(self.client.get(test_url))
        refresh_token_mock.assert_called_once_with(self.client._creds['client_id'],
                                                   self.client._creds['client_secret'],
                                                   self.client._creds['refresh_token'])

    def test_handle_unauthorized_response_without_response_handler(self, event_loop,
                                                                   response_headers, test_url):
        with aioresponses() as m, \
             pytest.raises(aiociscospark.exceptions.SparkResponseError):  # noqa
            m.get(test_url, status=401, headers=response_headers)
            event_loop.run_until_complete(self.client.get(test_url))
