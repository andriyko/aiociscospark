import itertools
import logging

from collections import namedtuple

from ..constants import API_BASE_URL, API_V1
from ..pagination import ResponsePaginator

logger = logging.getLogger(__name__)


ApiResource = namedtuple('ApiResource', ['name', 'cursor'])


class ApiService(object):
    """
    Base REST API client that provides high-level methods to perform CRUD operations.
    Delegates HTTP communication, authentication etc to the HTTP client.
    """
    _base_url = API_BASE_URL
    _version = API_V1
    _resource = ApiResource(None, 'cursor')
    _paginator = ResponsePaginator

    def __init__(self, http_client):
        self._resource_url = f'{self._base_url}/{self._version}/{self._resource.name}'
        self.http_client = http_client

    def get_resource_url(self, id_or_path=None):
        """
        Builds a resource URL for the given id or path (which may embed an id).
        :param id_or_path: An id or path that embeds and id.
        """
        if id_or_path is not None:
            return f'{self._resource_url}/{id_or_path}'
        return self._resource_url

    async def request(self, method, id_or_path, params=None, data=None, json_response=True,
                      **kwargs):
        """
        Performs HTTP request and returns HTTP response.

        :param method: HTTP method (verb)
        :param id_or_path: id or path (with embedded id) of the resource entity
        :param data: POST data as dict
        :param params: URL parameters as dict
        :param json_response: Return `aiohttp.ClientResponse` object or JSON
        :param kwargs: named arguments passed to underlying HTTP client
        :return: dict (if json_response == True) or
        HTTP Response object (eg. `aiohttp.ClientResponse`)
        """
        resource_url = self.get_resource_url(id_or_path=id_or_path)
        normalized_params = self._normalize_params(params)
        resp = await self.http_client.request(method,
                                              resource_url,
                                              params=normalized_params,
                                              json=data,
                                              **kwargs)
        return await resp.json() if json_response else resp

    @staticmethod
    def _normalize_params(d):
        if d is None or len(d) == 0:
            return {}
        params = {k: str(v).lower() if isinstance(v, bool) else str(v)
                  for (k, v) in d.items() if v is not None}
        return params

    async def paginate_response(self, response, paginate=True, **kwargs):
        """
        Iterates through a list of pages in a response and yields pairs of (item, cursor).

        Read more: https://developer.ciscospark.com/pagination.html

        :param response: `aiohttp.ClientResponse`
        """
        has_more = True
        c = 0
        while has_more:
            c += 1
            logger.debug(f'Page #{c}')
            paginator = self._paginator(response)
            data = await response.json()
            items = data['items']
            if self._resource.cursor:
                cursor = paginator.get_cursor(cursor=self._resource.cursor)
                # Instead of yielding item, yield pairs (item, cursor)
                # ({<item_dict>}, 'bGltaXQ9MTAmc3RhcnRJbmRleD0yMQ==')
                items = itertools.product(items, [cursor, ])
            for item in items:
                yield item
            has_more = not paginator.is_last_page and paginate
            if has_more:
                response = await self.http_client.get(paginator.next_url, **kwargs)

    async def get_items(self, params, paginate=True, **kwargs):
        response = await self.list(params=params, json_response=False, **kwargs)
        items = self.paginate_response(response, paginate=paginate, **kwargs)
        async for item in items:
            yield item

    # A set of aliases to simplify usage of API client.
    def head(self, id_or_path, params=None, **kwargs):
        return self.request('HEAD', id_or_path, data=None, params=params,
                            json_response=False, **kwargs)

    def get(self, id_or_path, params=None, json_response=True, **kwargs):
        return self.request('GET', id_or_path, data=None, params=params,
                            json_response=json_response, **kwargs)

    def list(self, params=None, json_response=True, **kwargs):
        return self.get(None, params=params, json_response=json_response, **kwargs)

    def put(self, id_or_path, data=None, params=None, json_response=True, **kwargs):
        return self.request('PUT', id_or_path, data=data, params=params,
                            json_response=json_response, **kwargs)

    def post(self, id_or_path=None, data=None, params=None, json_response=True, **kwargs):
        return self.request('POST', id_or_path, data=data, params=params,
                            json_response=json_response, **kwargs)

    def delete(self, id_or_path, params=None, **kwargs):
        return self.request('DELETE', id_or_path, data=None, params=params,
                            json_response=False, **kwargs)
