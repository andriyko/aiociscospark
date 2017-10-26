import json
import os
import urllib.parse
from http.client import HTTPSConnection

from .constants import API_BASE_URL, API_V1

__all__ = (
    'Credentials',
    'get_access_token',
    'refresh_access_token',
)


class Credentials(dict):
    """
    This class partially implements python's dictionary api.
    Delegates actual data set/get to underlying `storage` object which is `os.environ` in this case.

    Allows to work with the following keys:
    - access_token
    - refresh_token
    - client_id
    - client_secret

    Which are getting transformed to the following env variables:
    - CISCO_SPARK_ACCESS_TOKEN
    - CISCO_SPARK_REFRESH_TOKEN
    - CISCO_SPARK_CLIENT_ID
    - CISCO_SPARK_CLIENT_SECRET
    """
    _keys = (
        'access_token',
        'refresh_token',
        'client_id',
        'client_secret',
    )

    def __init__(self, d=None):
        self.storage = os.environ
        self.update(d or {})

    def _validate_key(self, key):
        if key not in self._keys:
            raise KeyError(key)

    def _transform_key(self, key):
        self._validate_key(key)
        return f'cisco_spark_{key}'.upper()

    def update(self, d):
        for k, v in d.items():
            if k in self._keys:
                self.__setitem__(k, v)

    def items(self):
        return [(k, self.__getitem__(k)) for k in self.keys()]

    def get(self, key, default=None):
        return self.storage.get(self._transform_key(key), default)

    def keys(self):
        return [key for key in self._keys if self.__contains__(key)]

    def values(self):
        return [self.__getitem__(k) for k in self.keys()]

    def pop(self, key, default=None):
        return self.storage.pop(self._transform_key(key), None)

    def popitem(self):
        try:
            key = next(iter(self))
        except StopIteration:
            raise KeyError
        value = self.__getitem__(key)
        self.__delitem__(key)
        return key, value

    def __contains__(self, key):
        try:
            self.storage[self._transform_key(key)]
        except KeyError:
            return False
        return True

    def __getitem__(self, key):
        return self.storage[self._transform_key(key)]

    def __setitem__(self, key, value):
        self.storage[self._transform_key(key)] = value

    def __delitem__(self, key):
        self.storage.pop(self._transform_key(key), None)

    def __iter__(self):
        return iter(self.storage.items())

    def __len__(self):
        return len(self.storage.keys())


def get_access_token(client_id, client_secret, code, redirect_uri):
    post_data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'redirect_uri': redirect_uri
    }
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json;charset=utf-8',
    }
    parsed_url = urllib.parse.urlparse(API_BASE_URL)
    conn = HTTPSConnection(parsed_url.hostname, parsed_url.port)
    url = os.path.join('/', API_V1, 'access_token')
    conn.request('POST', url, body=json.dumps(post_data), headers=headers)
    resp = conn.getresponse()
    data = json.loads(resp.read().decode())
    return data


def refresh_access_token(client_id, client_secret, refresh_token):
    """
    Refreshes access token. Performs synchronous request.

    :return: dict
    {'access_token': '<omitted>',
     'expires_in': 1209599,
     'refresh_token': '<omitted>',
     'refresh_token_expires_in': 7775553}
    """
    post_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }
    not_set = next((k for k in post_data.keys() if post_data[k] is None), None)
    if not_set:
        raise ValueError(f'"{not_set}" not set, it is needed in order to refresh access token')
    parsed_url = urllib.parse.urlparse(API_BASE_URL)
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json;charset=utf-8',
    }
    conn = HTTPSConnection(parsed_url.hostname, parsed_url.port)
    url = os.path.join('/', API_V1, 'access_token')
    conn.request('POST', url, body=json.dumps(post_data), headers=headers)
    resp = conn.getresponse()
    data = json.loads(resp.read().decode())
    return data
