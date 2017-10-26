import aiohttp
import asyncio
import logging

from aiohttp.client import DEFAULT_TIMEOUT

from .exceptions import (SparkResponseError, SparkResponseNotReceived, SparkRateLimitExceeded,
                         SparkClientConfigurationError)
from .utils import refresh_access_token

logger = logging.getLogger(__name__)


__all__ = (
    'HTTPClient',
)


def lazysession(func):
    name = '_lazy_{}'.format(func.__name__)

    @property
    def lazy(self):
        session = getattr(self, name, None)
        if session and not session.closed:
            return session
        else:
            value = func(self)
            setattr(self, name, value)
            return value
    return lazy


class HTTPClient(object):
    max_retries = 4
    _response_handlers = {
        401: 'handle_unauthorized_error',
    }

    def __init__(self, creds, loop=None, conn_timeout=None, read_timeout=DEFAULT_TIMEOUT):
        """
        A thin wrapper around `aiohttp.ClientSession` module that allows registering of response
        handlers and has built-in support for retrying failed requests.

        :param creds: a dictionary with at least one key: "access_token".
        Other allowed keys are: "refresh_token", "client_id", "client_secret".
        :param loop: an event loop
        :param conn_timeout: the connection timeout
        :param read_timeout: the read timeout
        """
        if not creds.get('access_token', None):
            raise SparkClientConfigurationError('"access_token" is required')
        self._creds = creds
        self._loop = loop
        self._conn_timeout = conn_timeout
        self._read_timeout = read_timeout

        self._registered_response_handlers = {}

    @property
    def default_headers(self):
        return {
            'Accept': 'application/json',
            'Content-Type': 'application/json;charset=utf-8',
            'Authorization': f'Bearer {self._creds["access_token"]}'
        }

    @lazysession
    def session(self):
        """
        Lazy property that allows to instantiate `HTTPClient` outside of event loop.

        :return: instance of `aiohttp.ClientSession`.
        """
        logger.debug('Creating new client session')
        return aiohttp.ClientSession(
            loop=self._loop,
            headers=self.default_headers,
            conn_timeout=self._conn_timeout,
            read_timeout=self._read_timeout
        )

    def close_session(self):
        session = getattr(self, '_lazy_session', None)
        return session and session.close()

    async def _handle_error(self, resp, attempts):
        if self.has_no_more_attempts(attempts):
            logger.debug('Giving up after %s attempts', attempts)
            raise await SparkResponseError.get(resp, session=self.session)

        handler_func = self.get_response_handler(resp.status)
        if handler_func:
            if asyncio.iscoroutinefunction(handler_func):
                await handler_func(resp)
            else:
                handler_func(resp)
            return

        if resp.status == 429:
            raise await SparkRateLimitExceeded.get(resp, session=self.session)
        raise await SparkResponseError.get(resp, session=self.session)

    async def _is_valid_response(self, resp, attempts=1):
        if resp is None:
            raise SparkResponseNotReceived('A response was not received')

        if 200 <= resp.status < 300:
            return True

        await self._handle_error(resp, attempts)

        if attempts:
            logger.warning('Attempt %s, retrying...', attempts)
            await asyncio.sleep(2 ** (attempts - 1))

        return False

    def get_response_handler(self, status):
        return self._registered_response_handlers.get(status)

    def register_response_handler(self, status, handler_func):
        if not callable(handler_func):
            handler_func = getattr(self, handler_func)
        self._registered_response_handlers[status] = handler_func

    def register_response_handlers(self):
        for status, handler in self._response_handlers.items():
            self.register_response_handler(status, handler)

    def has_no_more_attempts(self, attempts):
        return attempts >= self.max_retries

    async def request(self, method, url, **kwargs):
        attempts_counter = 0
        for attempts_counter in range(1, self.max_retries + 1):
            logger.debug('%s %s (attempt #%s)', method, url, attempts_counter)
            try:
                response = await self.session.request(method, url, **kwargs)
            except (aiohttp.client_exceptions.ServerTimeoutError,
                    aiohttp.client_exceptions.ServerConnectionError,
                    asyncio.TimeoutError) as exc:
                # await self.close_session()
                if self.has_no_more_attempts(attempts_counter):
                    await self.close_session()
                    raise exc
                logger.warning('Retying due to connection or timeout error')
            except Exception:
                await self.close_session()
                raise
            else:
                if await self._is_valid_response(response, attempts_counter):
                    return response

        raise SparkResponseNotReceived(
            f'A response was not received after {attempts_counter} attempts'
        )

    # A set of aliases to simplify usage of HTTP client.
    def get(self, url, **kwargs):
        return self.request(aiohttp.hdrs.METH_GET, url, **kwargs)

    def head(self, url, **kwargs):
        return self.request(aiohttp.hdrs.METH_HEAD, url, **kwargs)

    def post(self, url, **kwargs):
        return self.request(aiohttp.hdrs.METH_POST, url, **kwargs)

    def put(self, url, **kwargs):
        return self.request(aiohttp.hdrs.METH_PUT, url, **kwargs)

    def patch(self, url, **kwargs):
        return self.request(aiohttp.hdrs.METH_PATCH, url, **kwargs)

    def delete(self, url, **kwargs):
        return self.request(aiohttp.hdrs.METH_DELETE, url, **kwargs)

    # response handlers
    async def handle_unauthorized_error(self, resp):
        logger.info('Trying to refresh access token')
        client_id = self._creds['client_id']
        client_secret = self._creds['client_secret']
        refresh_token = self._creds['refresh_token']
        data = refresh_access_token(client_id, client_secret, refresh_token)
        self._creds['access_token'] = data['access_token']
        logger.info('Refreshed access token')
        return await self.close_session()
