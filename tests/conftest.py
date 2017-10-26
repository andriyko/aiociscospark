import asyncio
import json
import os

import pytest

from aiohttp import ClientResponse
from aiohttp.client_reqrep import RequestInfo
from yarl import URL

from .context import aiociscospark


def _load_json_data_file(fname):
    cur_dir = os.path.dirname(__file__)
    return json.load(open(os.path.join(cur_dir, f'data/{fname}')))


def _find_by_key(lst, key, val):
    return next((i for i in lst if i[key] == val), None)


@pytest.fixture
def api_base_url():
    return f'{aiociscospark.API_BASE_URL}/{aiociscospark.API_V1}'


@pytest.fixture
def test_url(api_base_url):
    return f'{api_base_url}/people'


@pytest.fixture
def access_token():
    return 'ZmQzMDdmNWUtZWVmNi0yM2U3LWExMjMtMTIzMzQ1NjdyZXI3cWZmYjQxYzAtMmU0'


@pytest.fixture
def refresh_token():
    return 'ODdlYzJjOTMtY2I3Zi00Zjg3LTllYTEtM3gxZjQyZXhlZjgxYWExZGM3YjMtYWE2'


@pytest.fixture
def bot_access_token():
    return '531lSZ16SQCOy1I3ZDhaz5MX53yiL6uqQ61614u10r71081838927O2Xp7Jx9K48'


@pytest.fixture
def bot_id():
    return 'Y2lzY29zcGFyazovL3VzL1BFT1BMRS8xYWJjODdiZi00MzMyLTQzMTItOTVnNS12NTRjNWMyYTQxYjg'


@pytest.fixture
def client_id():
    return 'Ca12775ddfar4354qqrty564o90c31q1e1d54trc0a59ee77f4fabe3qazea55ee5'


@pytest.fixture
def client_secret():
    return '21d1776ra5fa065185c6e2e6314c323e160147b14624b3f47c0dc5dkk4b785be'


@pytest.fixture
def credentials(client_id, client_secret, refresh_token, access_token):
    return {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'access_token': access_token,
    }


@pytest.fixture
def response_not_found_error():
    return {
        'message': 'Person not found',
        'errors': [
            {
                'description': 'Person not found'
            }
        ],
        'trackingId': 'NA_54fe2133-6126-4312-a213-c09ee7536d85'
    }


@pytest.fixture
def request_headers(access_token):
    return {
        'Accept': 'application/json',
        'Content-Type': 'application/json;charset=utf-8',
        'Authorization': f'Bearer {access_token}'
    }


@pytest.fixture
def response_headers():
    return {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json;charset=UTF-8',
        'Date': 'Mon, 27 Mar 2017 20:27:36 GMT',
        'Server': 'Redacted',
        'Trackingid': 'NA_a2565414-f59d-4e1a-a215-2c2d58b1aa13',
        'Vary': 'Accept-Encoding',
        'X-Cf-Requestid': '88e02466-842b-4b4d-65f6-fa76021e8566'
    }


@pytest.fixture
def response_headers_retry_after(response_headers):
    response_headers['Retry-After'] = 60
    return response_headers


@pytest.fixture
def file_content_headers():
    return {
        'Cache-Control': 'no-cache',
        'Content-Disposition': 'attachment; filename="file.txt"',
        'Content-Length': '33464',
        'Content-Type': 'text/plain',
        'Server': 'Redacted',
        'Trackingid': 'NA_63a58f57-f7ca-4ea8-aaf4-7122a191c43f',
        'X-Cf-Requestid': '91b28216-1126-4bcf-52f2-f07e826cc5da',
        'Date': 'Fri, 26 May 2017 08:39:25 GMT'
    }


@pytest.fixture
def people_list():
    return _load_json_data_file('people.json')


@pytest.fixture
def messages_list():
    return _load_json_data_file('messages.json')


@pytest.fixture
def licenses_list():
    return _load_json_data_file('licenses.json')


@pytest.fixture
def rooms_list():
    return _load_json_data_file('rooms.json')


@pytest.fixture
def teams_list():
    return _load_json_data_file('teams.json')


@pytest.fixture
def team_memberships_list():
    return _load_json_data_file('team_memberships.json')


@pytest.fixture
def organizations_list():
    return _load_json_data_file('organizations.json')


@pytest.fixture
def room_memberships_list():
    return _load_json_data_file('room_memberships.json')


@pytest.fixture
def roles_list():
    return _load_json_data_file('roles.json')


@pytest.fixture
def webhooks_list():
    return _load_json_data_file('webhooks.json')


@pytest.fixture()
def user_info(people_list):
    # user "fulladmin"
    _id = 'Y2lzY29zcGFyazovL3VzL1BFT1BMRS9mN2VyNjc1Yi0zMzlkLTVzMGQtZWM0NC1jN2IxOGY2MTUxNzc'
    return _find_by_key(people_list['items'], 'id', _id)


@pytest.fixture()
def team_info(teams_list):
    # team "Team1"
    _id = 'Y2lzY29zcGFyazovL3VzL1RFQU0vMzZlZjd0ZTAtMDEyMi0xMnI3LXJlYXEtYnIyMjU2NzZmYTZm'
    return _find_by_key(teams_list['items'], 'id', _id)


@pytest.fixture()
def room_info(rooms_list):
    # room "Room2"
    _id = 'Y2lzY29zcGFyazovL3VzL1JPT00vYzYyMDQyYTUtYWMyMS0zZWQyLWFlMjItOGk4MXJlNjU1NTFk'
    return _find_by_key(rooms_list['items'], 'id', _id)


@pytest.fixture()
def team_membership_info(team_memberships_list):
    # team "Team1" and user "fulladmin"
    _id = 'Y2lzY29zcGFyazovL3VzL1RFQU1fTUVNQkVSU0hJUC8zNmVmN3RlMC0wMTIyLTEycjctcmVhcS1icj' \
          'IyNTY3NmZhNmY6ZjdlcjY3NWItMzM5ZC01czBkLWVjNDQtYzdiMThmNjE1MTc3'
    return _find_by_key(team_memberships_list['items'], 'id', _id)


@pytest.fixture()
def organization_info(organizations_list):
    # organization "Async HTTP Client for Cisco Spark API"
    _id = 'Y2lzY29zcGFyazovL3VzL09SR0FOSVpBVElPTi81Yzc3MWNlMy1lNTAwLTQwMDMtN3Q4Yi01ZTc1YzliYXNzOTA'
    return _find_by_key(organizations_list['items'], 'id', _id)


@pytest.fixture
def bot_info(bot_id, org_id):
    return {
        'id': bot_id,
        'emails': [
            'thebot@sparkbot.io'
        ],
        'displayName': 'The Bot',
        'avatar': 'https://thebot.avatar',
        'orgId': org_id,
        'created': '2017-09-30T11:41:03.543Z',
        'type': 'bot'
    }


@pytest.fixture()
def room_membership_info(room_memberships_list):
    # room "Room2" and user "fulladmin"
    _id = 'Y2lzY29zcGFyazovL3VzL01FTUJFUlNISVAvYzYyMDQyYTUtYWMyMS0zZWQyLWFlMjItOGk4MXJlNjU1NTFk' \
          'OmY3ZXI2NzViLTMzOWQtNXMwZC1lYzQ0LWM3YjE4ZjYxNTE3Nw'
    return _find_by_key(room_memberships_list['items'], 'id', _id)


@pytest.fixture()
def message_info(messages_list):
    # message posted by admin@example.com
    _id = 'Y2lzY29zcGFyazovL3VzL01FU1NBR0UvN2VhNXY3ODEtMTJmZS0xMWU3LTg0ZGItZDk5Mzk1MzEzMTdi'
    return _find_by_key(messages_list['items'], 'id', _id)


@pytest.fixture()
def license_info(licenses_list):
    # Messaging license
    _id = 'Y2lzY29zcGFyazovL3VzL0xJQ0VOU0UvNWM3NzFjZTMtZTUwMC00MDAzLTd0OGItNWU3NWM5YmFzczk' \
          'wOkVFXzE3MmM4M2ExLTFlZDAtNDNiYS1hYmM3LTRlcmY4NzZhYzM4YV9leGFtcGxlLndlYmV4LmNvbQ'
    return _find_by_key(licenses_list['items'], 'id', _id)


@pytest.fixture()
def role_info(roles_list):
    # Full Admin role
    _id = 'Y2lzY29zcGFyazovL3VzL1JPTEUvaWRfZnVsbF9hZG1pbg'
    return _find_by_key(roles_list['items'], 'id', _id)


@pytest.fixture()
def webhook_info(webhooks_list):
    # webhook1
    _id = 'Y2lzY29zcGFyazovL3VzL1dFQkhPT0svMjExNDE2NzEtZDJjOC00NzhjLWEwM2MtNTZlM2NiY2FiNWFj'
    return _find_by_key(webhooks_list['items'], 'id', _id)


async def prepare_fake_response(url, *, method='GET', req_headers=None, resp_headers=None,
                                resp_status=200, resp_reason='OK', resp_content=b''):
    resp = ClientResponse(method, URL(val=url),
                          request_info=RequestInfo(url, method, req_headers or {}))
    resp._content = resp_content
    resp.status = resp_status
    resp.reason = resp_reason
    resp.headers = resp_headers or {}
    future = asyncio.Future()
    future.set_result(resp)
    return future


@pytest.fixture
def create_fake_response():
    return prepare_fake_response


@pytest.fixture
async def fake_resp(test_url, request_headers, response_headers, people_list, create_fake_response):
    resp_content = json.dumps(people_list).encode()
    future_resp = create_fake_response(test_url, req_headers=request_headers,
                                       resp_headers=response_headers, resp_content=resp_content)
    return await future_resp


@pytest.fixture
async def fake_resp_with_next_link(test_url, request_headers, response_headers, people_list,
                                   create_fake_response):
    resp_content = json.dumps(people_list).encode()
    response_headers['link'] = f'<{test_url}?max=1&cursor=bGltaXQ9MiZzdGFydEluZGV4PTM=>; rel="next"'
    future_resp = create_fake_response(test_url, req_headers=request_headers,
                                       resp_headers=response_headers, resp_content=resp_content)
    return await future_resp


@pytest.fixture
async def fake_resp_error(test_url, request_headers, response_headers, response_not_found_error,
                          create_fake_response):
    resp_content = json.dumps(response_not_found_error).encode()
    future_resp = create_fake_response(test_url, req_headers=request_headers,
                                       resp_headers=response_headers, resp_reason='Not found',
                                       resp_status=404, resp_content=resp_content)
    return await future_resp


@pytest.fixture
async def fake_resp_error_rate_limit(test_url, request_headers, response_headers_retry_after,
                                     create_fake_response):
    future_resp = create_fake_response(test_url, req_headers=request_headers,
                                       resp_headers=response_headers_retry_after,
                                       resp_reason='Too many requests', resp_status=429)
    return await future_resp


@pytest.fixture
def fake_error_handler():
    class FakeErrorHandler:
        done = False

        @staticmethod
        def handler(resp):
            FakeErrorHandler.done = True

    return FakeErrorHandler


@pytest.fixture
def async_fake_error_handler():
    class FakeErrorHandler:
        done = False

        @staticmethod
        async def handler(resp):
            # await asyncio.sleep(0.1)
            FakeErrorHandler.done = True

    return FakeErrorHandler
