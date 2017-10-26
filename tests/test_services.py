import json
import mock
import pytest

import aiohttp

from copy import copy

from aioresponses import aioresponses

from .context import aiociscospark


class TestBaseApiService:
    @pytest.fixture(scope='function', autouse=True)
    def setup(self, credentials, event_loop):
        http_client = aiociscospark.HTTPClient(credentials, loop=event_loop)
        svc = aiociscospark.services.ApiService
        svc._resource = aiociscospark.services.ApiResource('people', 'cursor')
        self.svc = svc(http_client)

    def test_init(self, test_url):
        assert self.svc._resource_url == test_url
        assert isinstance(self.svc.http_client, aiociscospark.HTTPClient)

    def test_get_resource_url(self, test_url):
        assert self.svc.get_resource_url() == test_url
        assert self.svc.get_resource_url('me') == f'{test_url}/me'

    def test__normalize_params(self):
        d = {'none': None, 'bool': True, 'id': 'Id'}
        normalized = self.svc._normalize_params(d)
        assert normalized == {'bool': 'true', 'id': 'Id'}

    def test_request(self, event_loop, test_url, response_headers, user_info):
        with aioresponses() as m:
            m.get(f'{test_url}/me', headers=response_headers, payload=user_info)
            data = event_loop.run_until_complete(self.svc.request('GET', 'me'))
        assert data == user_info

    def test_request_raw_response(self, event_loop, test_url, response_headers,
                                  user_info):
        with aioresponses() as m:
            m.get(f'{test_url}/me', headers=response_headers, body=json.dumps(user_info).encode())
            resp = event_loop.run_until_complete(self.svc.request('GET', 'me', json_response=False))
        assert isinstance(resp, aiohttp.ClientResponse)
        data = event_loop.run_until_complete(resp.json())
        assert data == user_info

    def test_request_passes_correct_signature_to_http_client(self, event_loop, test_url, fake_resp):
        params = {
            'email': 'admin@example.com',
            'max': None
        }
        with mock.patch.object(self.svc.http_client, 'request',
                               return_value=fake_resp) as http_client_request_mock:
            event_loop.run_until_complete(self.svc.request('GET', None, params=params, timeout=10))
        http_client_request_mock.assert_called_once_with('GET', test_url,
                                                         params={'email': 'admin@example.com'},
                                                         json=None, **{'timeout': 10})

    async def test_paginate_response(self, test_url, people_list, response_headers):
        items = people_list['items']
        cursor = 'cursor='
        response_headers['link'] = f'<{test_url}?max=2&cursor={cursor}>; rel="next"'
        data = []
        with aioresponses() as m:
            m.get(f'{test_url}', headers=copy(response_headers), payload={'items': items[:2]})
            response_headers.pop('link')
            m.get(f'{test_url}?max=2&cursor={cursor}', headers=response_headers,
                  payload={'items': items[2:]})
            resp = await self.svc.request('GET', None, json_response=False)
            async for item, cursor in self.svc.paginate_response(resp):
                data.append(item)
        assert data == items

    async def test_paginate_response_without_cursor(self, test_url, people_list, response_headers):
        items = people_list['items']
        response_headers['link'] = f'<{test_url}?max=2>; rel="next"'
        data = []

        self.svc._resource = aiociscospark.services.ApiResource('people', None)

        with aioresponses() as m:
            m.get(f'{test_url}', headers=copy(response_headers), payload={'items': items[:2]})
            response_headers.pop('link')
            m.get(f'{test_url}?max=2', headers=response_headers,
                  payload={'items': items[2:]})
            resp = await self.svc.request('GET', None, json_response=False)
            async for item in self.svc.paginate_response(resp):
                data.append(item)
        assert data == items

    async def test_get_items_with_pagination(self, test_url, people_list, response_headers):
        items = people_list['items']
        cursor = 'cursor='
        response_headers['link'] = f'<{test_url}?max=2&cursor={cursor}>; rel="next"'
        data = []
        with aioresponses() as m:
            m.get(f'{test_url}', headers=copy(response_headers), payload={'items': items[:2]})
            response_headers.pop('link')
            m.get(f'{test_url}?max=2&cursor={cursor}', headers=response_headers,
                  payload={'items': items[2:]})
            async for item, cursor in self.svc.get_items({'max': 2, 'cursor': cursor},
                                                         paginate=True):
                data.append(item)
        assert data == items

    async def test_get_items_without_pagination(self, test_url, people_list, response_headers):
        items = people_list['items']
        cursor = 'cursor='
        response_headers['link'] = f'<{test_url}?max=2&cursor={cursor}>; rel="next"'
        data = []
        with aioresponses() as m:
            m.get(f'{test_url}', headers=response_headers, payload={'items': items[:2]})
            async for item, cursor in self.svc.get_items({'max': 2, 'cursor': cursor},
                                                         paginate=False):
                data.append(item)
        assert data == items[:2]

    # Test that aliases pass correct signature to underlying request function.
    def test_head(self):
        id_or_path = None
        params = {'a': 1}
        kwargs = {'b': 2}
        with mock.patch.object(self.svc, 'request') as svc_request_mock:
            self.svc.head(id_or_path, params=params, **kwargs)
        svc_request_mock.assert_called_once_with('HEAD', id_or_path, data=None, params=params,
                                                 json_response=False, **kwargs)

    @pytest.mark.parametrize('json_response', [True, False])
    def test_get(self, json_response):
        id_or_path = 'id_or_path'
        params = {'a': 1}
        kwargs = {'b': 2}
        with mock.patch.object(self.svc, 'request') as svc_request_mock:
            self.svc.get(id_or_path, json_response=json_response, params=params, **kwargs)
        svc_request_mock.assert_called_once_with('GET', id_or_path, data=None, params=params,
                                                 json_response=json_response, **kwargs)

    @pytest.mark.parametrize('json_response', [True, False])
    def test_list(self, json_response):
        params = {'a': 1}
        kwargs = {'b': 2}
        with mock.patch.object(self.svc, 'request') as svc_request_mock:
            self.svc.list(params=params, json_response=json_response, **kwargs)
        svc_request_mock.assert_called_once_with('GET', None, data=None, params=params,
                                                 json_response=json_response, **kwargs)

    @pytest.mark.parametrize('json_response', [True, False])
    def test_put(self, json_response):
        id_or_path = 'id_or_path'
        params = {'a': 1}
        kwargs = {'b': 2}
        data = {'c': 1}
        with mock.patch.object(self.svc, 'request') as svc_request_mock:
            self.svc.put(id_or_path, data=data, params=params, json_response=json_response, **kwargs)
        svc_request_mock.assert_called_once_with('PUT', id_or_path, data=data, params=params,
                                                 json_response=json_response, **kwargs)

    @pytest.mark.parametrize('json_response', [True, False])
    def test_post(self, json_response):
        id_or_path = 'id_or_path'
        params = {'a': 1}
        kwargs = {'b': 2}
        data = {'c': 1}
        with mock.patch.object(self.svc, 'request') as svc_request_mock:
            self.svc.post(id_or_path, data=data, params=params, json_response=json_response,
                          **kwargs)
        svc_request_mock.assert_called_once_with('POST', id_or_path, data=data, params=params,
                                                 json_response=json_response, **kwargs)

    def test_delete(self):
        id_or_path = 'id_or_path'
        params = {'a': 1}
        kwargs = {'b': 2}
        with mock.patch.object(self.svc, 'request') as svc_request_mock:
            self.svc.delete(id_or_path, params=params, **kwargs)
        svc_request_mock.assert_called_once_with('DELETE', id_or_path, data=None, params=params,
                                                 json_response=False, **kwargs)


class BaseTestApiService:
    svc_class = None

    @pytest.fixture(scope='function', autouse=True)
    def setup(self, credentials, event_loop):
        http_client = aiociscospark.HTTPClient(credentials, loop=event_loop)
        self.svc = self.svc_class(http_client)


class TestApiServiceContents(BaseTestApiService):
    svc_class = aiociscospark.services.ApiServiceContents

    def test__get_content_url(self, api_base_url):
        content_id = 'content_id'
        content_url = f'{api_base_url}/contents/{content_id}'
        url1 = self.svc._get_content_url(content_id=content_id)
        url2 = self.svc._get_content_url(content_url=content_url)
        assert content_url == url1 == url2

    def test__get_content_url_raises_error(self, api_base_url):
        with pytest.raises(ValueError):
            self.svc._get_content_url()

    async def test_get_content_info(self, api_base_url, file_content_headers):
        content_id = 'content_id'
        url = f'{api_base_url}/contents/{content_id}'
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
             mock.patch.object(self.svc.http_client, 'head',
                               side_effect=self.svc.http_client.head) as req_mock:  # noqa
            m.head(url, headers=file_content_headers)
            data = await self.svc.get_content_info(content_id=content_id, **kwargs)
        req_mock.assert_called_once_with(url, **kwargs)
        assert data == {
            'content_name': 'file.txt',
            'content_size': 33464,
            'content_type': 'text/plain'
        }

    async def test_get_content(self, api_base_url, file_content_headers):
        content_id = 'content_id'
        url = f'{api_base_url}/contents/{content_id}'
        content_text = 'content text'
        kwargs = {'timeout': 300}
        with aioresponses() as m,\
             mock.patch.object(self.svc.http_client, 'get',
                               side_effect=self.svc.http_client.get) as req_mock:  # noqa
            m.get(url, headers=file_content_headers, body=content_text)
            data = await self.svc.get_content(content_id=content_id, **kwargs)
        req_mock.assert_called_once_with(url, **kwargs)
        assert data == content_text


class TestApiServiceLicenses(BaseTestApiService):
    svc_class = aiociscospark.services.ApiServiceLicenses

    async def test_list_licenses(self, api_base_url, response_headers, licenses_list):
        data = []
        kwargs = {'timeout': 300}
        org_id = 'org_id'
        paginate = False
        with aioresponses() as m, \
             mock.patch.object(self.svc, 'get_items',
                               side_effect=self.svc.get_items) as get_items_mock:  # noqa
            m.get(f'{api_base_url}/licenses', headers=response_headers, payload=licenses_list)
            async for item, cursor in self.svc.list_licenses(org_id=org_id,
                                                             paginate=paginate, **kwargs):
                data.append(item)
        get_items_mock.assert_called_once_with(
            {'orgId': org_id, 'max': None, 'cursor': None},
            paginate=paginate,
            **kwargs
        )
        assert data == licenses_list['items']

    async def test_get_license(self, api_base_url, response_headers, license_info):
        license_id = license_info['id']
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
             mock.patch.object(self.svc, 'get', side_effect=self.svc.get) as req_mock:  # noqa
            m.get(f'{api_base_url}/licenses/{license_id}', headers=response_headers,
                  payload=license_info)
            data = await self.svc.get_license(license_id, **kwargs)
        req_mock.assert_called_once_with(license_id, **kwargs)
        assert data == license_info


class TestApiServiceMessages(BaseTestApiService):
    svc_class = aiociscospark.services.ApiServiceMessages

    async def test_list_messages(self, api_base_url, response_headers, messages_list, message_info):
        data = []
        kwargs = {'timeout': 300}
        room_id = message_info['roomId']
        with aioresponses() as m, \
             mock.patch.object(self.svc, 'get_items',
                               side_effect=self.svc.get_items) as get_items_mock:  # noqa
            m.get(f'{api_base_url}/messages', headers=response_headers, payload=messages_list)
            async for item, cursor in self.svc.list_messages(room_id=room_id, **kwargs):
                data.append(item)
        get_items_mock.assert_called_once_with(
            {
                'roomId': room_id,
                'mentionedPeople': None,
                'before': None,
                'beforeMessage': None,
                'max': None,
                'cursor': None
            },
            paginate=True,
            **kwargs
        )
        assert data == messages_list['items']

    async def test_get_message(self, api_base_url, message_info, response_headers):
        message_id = message_info['id']
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
             mock.patch.object(self.svc, 'get', side_effect=self.svc.get) as req_mock:  # noqa
            m.get(f'{api_base_url}/messages/{message_id}', headers=response_headers,
                  payload=message_info)
            data = await self.svc.get_message(message_id, **kwargs)
        req_mock.assert_called_once_with(message_id, **kwargs)
        assert data == message_info

    async def test_create_message(self, api_base_url, message_info, response_headers):
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
            mock.patch.object(self.svc, 'post', side_effect=self.svc.post) as req_mock:  # noqa
            m.post(f'{api_base_url}/messages', headers=response_headers, payload=message_info)
            data = await self.svc.create_message(room_id=message_info['roomId'],
                                                 text=message_info['text'], **kwargs)
        req_mock.assert_called_once_with(
            data={
                'roomId': message_info['roomId'],
                'toPersonId': None,
                'toPersonEmail': None,
                'text': message_info['text'],
                'markdown': None,
                'files': None
            },
            **kwargs
        )
        assert data == message_info

    async def test_delete_message(self, api_base_url, message_info, response_headers):
        kwargs = {'timeout': 300}
        message_id = message_info['id']
        with aioresponses() as m, \
            mock.patch.object(self.svc, 'delete', side_effect=self.svc.delete) as req_mock:  # noqa
            m.delete(f'{api_base_url}/messages/{message_id}', status=204, headers=response_headers)
            resp = await self.svc.delete_message(message_id, **kwargs)
        req_mock.assert_called_once_with(message_id, **kwargs)
        assert resp.status == 204


class TestApiServiceOrganizations(BaseTestApiService):
    svc_class = aiociscospark.services.ApiServiceOrganizations

    async def test_list_organizations(self, api_base_url, response_headers, organizations_list):
        data = []
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
            mock.patch.object(self.svc, 'get_items',
                              side_effect=self.svc.get_items) as get_items_mock:  # noqa
            m.get(f'{api_base_url}/organizations', headers=response_headers,
                  payload=organizations_list)
            async for item, cursor in self.svc.list_organizations(limit=10, **kwargs):
                data.append(item)
        get_items_mock.assert_called_once_with(
            {
                'max': 10,
                'cursor': None
            },
            paginate=True,
            **kwargs
        )
        assert data == organizations_list['items']

    async def test_get_organization(self, api_base_url, response_headers, organization_info):
        organization_id = organization_info['id']
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
             mock.patch.object(self.svc, 'get', side_effect=self.svc.get) as req_mock:  # noqa
            m.get(f'{api_base_url}/organizations/{organization_id}', headers=response_headers,
                  payload=organization_info)
            data = await self.svc.get_organization(organization_id, **kwargs)
        req_mock.assert_called_once_with(organization_id, **kwargs)
        assert data == organization_info


class TestApiServicePeople(BaseTestApiService):
    svc_class = aiociscospark.services.ApiServicePeople

    async def test_list_people(self, api_base_url, response_headers, people_list):
        data = []
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
            mock.patch.object(self.svc, 'get_items',
                              side_effect=self.svc.get_items) as get_items_mock:  # noqa
            m.get(f'{api_base_url}/people', headers=response_headers, payload=people_list)
            async for item, cursor in self.svc.list_people(limit=10, **kwargs):
                data.append(item)
        get_items_mock.assert_called_once_with(
            {'email': None, 'displayName': None, 'max': 10, 'cursor': None},
            paginate=True,
            **kwargs
        )
        assert data == people_list['items']

    async def test_get_person(self, api_base_url, response_headers, user_info):
        person_id = user_info['id']
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
             mock.patch.object(self.svc, 'get', side_effect=self.svc.get) as req_mock:  # noqa
            m.get(f'{api_base_url}/people/{person_id}', headers=response_headers,
                  payload=user_info)
            data = await self.svc.get_person(person_id, **kwargs)
        req_mock.assert_called_once_with(person_id, **kwargs)
        assert data == user_info

    async def test_me(self, api_base_url, response_headers, user_info):
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
             mock.patch.object(self.svc, 'get', side_effect=self.svc.get) as req_mock:  # noqa
            m.get(f'{api_base_url}/people/me', headers=response_headers,
                  payload=user_info)
            data = await self.svc.me(**kwargs)
        req_mock.assert_called_once_with('me', **kwargs)
        assert data == user_info

    async def test_create_person(self, api_base_url, response_headers, user_info):
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
             mock.patch.object(self.svc, 'post', side_effect=self.svc.post) as req_mock:  # noqa
            m.post(f'{api_base_url}/people', headers=response_headers, payload=user_info)
            data = await self.svc.create_person(
                emails=user_info['emails'],
                display_name=user_info['displayName'],
                first_name='Full',
                last_name='Admin',
                org_id=user_info['orgId'],
                roles=user_info['roles'],
                licenses=user_info['licenses'],
                **kwargs
            )
        req_mock.assert_called_once_with(
            data={
                'emails': user_info['emails'],
                'displayName': user_info['displayName'],
                'firstName': 'Full',
                'lastName': 'Admin',
                'avatar': None,
                'orgId': user_info['orgId'],
                'roles': user_info['roles'],
                'licenses': user_info['licenses']
            },
            **kwargs
        )
        assert data == user_info

    async def test_update_person(self, api_base_url, response_headers, user_info):
        person_id = user_info['id']
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
             mock.patch.object(self.svc, 'put', side_effect=self.svc.put) as req_mock:  # noqa
            m.put(f'{api_base_url}/people/{person_id}', headers=response_headers, payload=user_info)
            data = await self.svc.update_person(person_id,
                                                emails=user_info['emails'],
                                                display_name=user_info['displayName'],
                                                first_name='Full',
                                                last_name='Admin',
                                                org_id=user_info['orgId'],
                                                roles=user_info['roles'],
                                                licenses=user_info['licenses'],
                                                **kwargs)
        req_mock.assert_called_once_with(
            person_id,
            data={
                'emails': user_info['emails'],
                'displayName': user_info['displayName'],
                'firstName': 'Full',
                'lastName': 'Admin',
                'avatar': None,
                'orgId': user_info['orgId'],
                'roles': user_info['roles'],
                'licenses': user_info['licenses']
            },
            **kwargs
        )
        assert data == user_info

    async def test_delete_person(self, api_base_url, user_info, response_headers):
        person_id = user_info['id']
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
             mock.patch.object(self.svc, 'delete', side_effect=self.svc.delete) as req_mock:  # noqa
            m.delete(f'{api_base_url}/people/{person_id}', status=204, headers=response_headers)
            resp = await self.svc.delete_person(person_id, **kwargs)
        req_mock.assert_called_once_with(person_id, **kwargs)
        assert resp.status == 204


class TestApiServiceRoles(BaseTestApiService):
    svc_class = aiociscospark.services.ApiServiceRoles

    async def test_list_roles(self, api_base_url, response_headers, roles_list):
        data = []
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
            mock.patch.object(self.svc, 'get_items',
                              side_effect=self.svc.get_items) as get_items_mock:  # noqa
            m.get(f'{api_base_url}/roles', headers=response_headers, payload=roles_list)
            async for item, cursor in self.svc.list_roles(limit=10, **kwargs):
                data.append(item)
        get_items_mock.assert_called_once_with(
            {'max': 10, 'cursor': None},
            paginate=True,
            **kwargs
        )
        assert data == roles_list['items']

    async def test_get_role(self, api_base_url, response_headers, role_info):
        role_id = role_info['id']
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
             mock.patch.object(self.svc, 'get', side_effect=self.svc.get) as req_mock:  # noqa
            m.get(f'{api_base_url}/roles/{role_id}', headers=response_headers,
                  payload=role_info)
            data = await self.svc.get_role(role_id, **kwargs)
        req_mock.assert_called_once_with(role_id, **kwargs)
        assert data == role_info


class TestApiServiceRoomMemberships(BaseTestApiService):
    svc_class = aiociscospark.services.ApiServiceRoomMemberships

    async def test_list_memberships(self, api_base_url, response_headers, room_memberships_list):
        data = []
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
             mock.patch.object(self.svc, 'get_items',
                               side_effect=self.svc.get_items) as get_items_mock:  # noqa
            m.get(f'{api_base_url}/memberships', headers=response_headers,
                  payload=room_memberships_list)
            async for item, cursor in self.svc.list_memberships(limit=10, **kwargs):
                data.append(item)
        get_items_mock.assert_called_once_with(
            {'roomId': None, 'personId': None, 'personEmail': None, 'max': 10, 'cursor': None},
            paginate=True,
            **kwargs
        )
        assert data == room_memberships_list['items']

    async def test_get_membership(self, api_base_url, response_headers, room_membership_info):
        membership_id = room_membership_info['id']
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
             mock.patch.object(self.svc, 'get', side_effect=self.svc.get) as req_mock:  # noqa
            m.get(f'{api_base_url}/memberships/{membership_id}', headers=response_headers,
                  payload=room_membership_info)
            data = await self.svc.get_membership(membership_id, **kwargs)
        req_mock.assert_called_once_with(membership_id, **kwargs)
        assert data == room_membership_info

    async def test_create_membership(self, api_base_url, response_headers, room_membership_info):
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
             mock.patch.object(self.svc, 'post', side_effect=self.svc.post) as req_mock:  # noqa
            m.post(f'{api_base_url}/memberships', headers=response_headers,
                   payload=room_membership_info)
            data = await self.svc.create_membership(
                room_id=room_membership_info['id'],
                person_id=room_membership_info['personId'],
                person_email=room_membership_info['personEmail'],
                is_moderator=room_membership_info['isModerator'],
                **kwargs
            )
        req_mock.assert_called_once_with(
            data={
                'roomId': room_membership_info['id'],
                'personId': room_membership_info['personId'],
                'personEmail': room_membership_info['personEmail'],
                'isModerator': room_membership_info['isModerator']
            },
            **kwargs
        )
        assert data == room_membership_info

    async def test_update_membership(self, api_base_url, response_headers, room_membership_info):
        room_membership_id = room_membership_info['id']
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
            mock.patch.object(self.svc, 'put', side_effect=self.svc.put) as req_mock:  # noqa
            m.put(f'{api_base_url}/memberships/{room_membership_id}', headers=response_headers,
                  payload=room_membership_info)
            data = await self.svc.update_membership(room_membership_id, is_moderator=False, **kwargs)
        req_mock.assert_called_once_with(room_membership_id, data={'isModerator': False}, **kwargs)
        assert data == room_membership_info

    async def test_delete_membership(self, api_base_url, room_membership_info, response_headers):
        room_membership_id = room_membership_info['id']
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
             mock.patch.object(self.svc, 'delete', side_effect=self.svc.delete) as req_mock:  # noqa
            m.delete(f'{api_base_url}/memberships/{room_membership_id}', status=204,
                     headers=response_headers)
            resp = await self.svc.delete_membership(room_membership_id, **kwargs)
        req_mock.assert_called_once_with(room_membership_id, **kwargs)
        assert resp.status == 204


class TestApiServiceRooms(BaseTestApiService):
    svc_class = aiociscospark.services.ApiServiceRooms

    async def test_list_rooms(self, api_base_url, response_headers, team_info, rooms_list):
        data = []
        kwargs = {'timeout': 300}
        team_id = team_info['id']
        with aioresponses() as m, \
             mock.patch.object(self.svc, 'get_items',
                               side_effect=self.svc.get_items) as get_items_mock:  # noqa
            m.get(f'{api_base_url}/rooms', headers=response_headers, payload=rooms_list)
            async for item, cursor in self.svc.list_rooms(team_id=team_id, **kwargs):
                data.append(item)
        get_items_mock.assert_called_once_with(
            {'teamId': team_id, 'max': None, 'sortBy': None, 'type': None, 'cursor': None},
            paginate=True,
            **kwargs
        )
        assert data == rooms_list['items']

    async def test_get_room(self, api_base_url, response_headers, room_info):
        room_id = room_info['id']
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
             mock.patch.object(self.svc, 'get', side_effect=self.svc.get) as req_mock:  # noqa
            m.get(f'{api_base_url}/rooms/{room_id}', headers=response_headers, payload=room_info)
            data = await self.svc.get_room(room_id, **kwargs)
        req_mock.assert_called_once_with(room_id, **kwargs)
        assert data == room_info

    async def test_create_room(self, api_base_url, response_headers, room_info):
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
             mock.patch.object(self.svc, 'post', side_effect=self.svc.post) as req_mock:  # noqa
            m.post(f'{api_base_url}/rooms', headers=response_headers, payload=room_info)
            data = await self.svc.create_room(
                title=room_info['title'],
                team_id=room_info['teamId'],
                **kwargs
            )
        req_mock.assert_called_once_with(
            data={
                'title': room_info['title'],
                'teamId': room_info['teamId']
            },
            **kwargs
        )
        assert data == room_info

    async def test_update_rooms(self, api_base_url, response_headers, room_info):
        room_id = room_info['id']
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
            mock.patch.object(self.svc, 'put', side_effect=self.svc.put) as req_mock:  # noqa
            m.put(f'{api_base_url}/rooms/{room_id}', headers=response_headers, payload=room_info)
            data = await self.svc.update_room(room_id, title='New title', **kwargs)
        req_mock.assert_called_once_with(room_id, data={'title': 'New title'}, **kwargs)
        assert data == room_info

    async def test_delete_room(self, api_base_url, room_info, response_headers):
        room_id = room_info['id']
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
             mock.patch.object(self.svc, 'delete', side_effect=self.svc.delete) as req_mock:  # noqa
            m.delete(f'{api_base_url}/rooms/{room_id}', status=204,
                     headers=response_headers)
            resp = await self.svc.delete_room(room_id, **kwargs)
        req_mock.assert_called_once_with(room_id, **kwargs)
        assert resp.status == 204


class TestApiServiceTeamMemberships(BaseTestApiService):
    svc_class = aiociscospark.services.ApiServiceTeamMemberships

    async def test_list_memberships(self, api_base_url, response_headers, team_memberships_list):
        data = []
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
             mock.patch.object(self.svc, 'get_items',
                               side_effect=self.svc.get_items) as get_items_mock:  # noqa
            m.get(f'{api_base_url}/team/memberships', headers=response_headers,
                  payload=team_memberships_list)
            async for item, cursor in self.svc.list_memberships(limit=10, **kwargs):
                data.append(item)
        get_items_mock.assert_called_once_with(
            {'teamId': None, 'max': 10, 'cursor': None},
            paginate=True,
            **kwargs
        )
        assert data == team_memberships_list['items']

    async def test_get_membership(self, api_base_url, response_headers, team_membership_info):
        membership_id = team_membership_info['id']
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
             mock.patch.object(self.svc, 'get', side_effect=self.svc.get) as req_mock:  # noqa
            m.get(f'{api_base_url}/team/memberships/{membership_id}', headers=response_headers,
                  payload=team_membership_info)
            data = await self.svc.get_membership(membership_id, **kwargs)
        req_mock.assert_called_once_with(membership_id, **kwargs)
        assert data == team_membership_info

    async def test_create_membership(self, api_base_url, response_headers, team_membership_info):
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
             mock.patch.object(self.svc, 'post', side_effect=self.svc.post) as req_mock:  # noqa
            m.post(f'{api_base_url}/team/memberships', headers=response_headers,
                   payload=team_membership_info)
            data = await self.svc.create_membership(
                team_id=team_membership_info['id'],
                person_id=team_membership_info['personId'],
                person_email=team_membership_info['personEmail'],
                is_moderator=team_membership_info['isModerator'],
                **kwargs
            )
        req_mock.assert_called_once_with(
            data={
                'teamId': team_membership_info['id'],
                'personId': team_membership_info['personId'],
                'personEmail': team_membership_info['personEmail'],
                'isModerator': team_membership_info['isModerator']
            },
            **kwargs
        )
        assert data == team_membership_info

    async def test_update_membership(self, api_base_url, response_headers, team_membership_info):
        team_membership_id = team_membership_info['id']
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
            mock.patch.object(self.svc, 'put', side_effect=self.svc.put) as req_mock:  # noqa
            m.put(f'{api_base_url}/team/memberships/{team_membership_id}', headers=response_headers,
                  payload=team_membership_info)
            data = await self.svc.update_membership(team_membership_id, is_moderator=False, **kwargs)
        req_mock.assert_called_once_with(team_membership_id, data={'isModerator': False}, **kwargs)
        assert data == team_membership_info

    async def test_delete_membership(self, api_base_url, team_membership_info, response_headers):
        team_membership_id = team_membership_info['id']
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
             mock.patch.object(self.svc, 'delete', side_effect=self.svc.delete) as req_mock:  # noqa
            m.delete(f'{api_base_url}/team/memberships/{team_membership_id}', status=204,
                     headers=response_headers)
            resp = await self.svc.delete_membership(team_membership_id, **kwargs)
        req_mock.assert_called_once_with(team_membership_id, **kwargs)
        assert resp.status == 204


class TestApiServiceTeams(BaseTestApiService):
    svc_class = aiociscospark.services.ApiServiceTeams

    async def test_list_teams(self, api_base_url, response_headers, teams_list):
        data = []
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
             mock.patch.object(self.svc, 'get_items',
                               side_effect=self.svc.get_items) as get_items_mock:  # noqa
            m.get(f'{api_base_url}/teams', headers=response_headers, payload=teams_list)
            async for item, cursor in self.svc.list_teams(limit=10, **kwargs):
                data.append(item)
        get_items_mock.assert_called_once_with(
            {'max': 10, 'cursor': None},
            paginate=True,
            **kwargs
        )
        assert data == teams_list['items']

    async def test_get_team(self, api_base_url, response_headers, team_info):
        team_id = team_info['id']
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
             mock.patch.object(self.svc, 'get', side_effect=self.svc.get) as req_mock:  # noqa
            m.get(f'{api_base_url}/teams/{team_id}', headers=response_headers, payload=team_info)
            data = await self.svc.get_team(team_id, **kwargs)
        req_mock.assert_called_once_with(team_id, **kwargs)
        assert data == team_info

    async def test_create_team(self, api_base_url, response_headers, team_info):
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
             mock.patch.object(self.svc, 'post', side_effect=self.svc.post) as req_mock:  # noqa
            m.post(f'{api_base_url}/teams', headers=response_headers, payload=team_info)
            data = await self.svc.create_team(
                name=team_info['name'],
                **kwargs
            )
        req_mock.assert_called_once_with(
            data={
                'name': team_info['name']
            },
            **kwargs
        )
        assert data == team_info

    async def test_update_teams(self, api_base_url, response_headers, team_info):
        team_id = team_info['id']
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
            mock.patch.object(self.svc, 'put', side_effect=self.svc.put) as req_mock:  # noqa
            m.put(f'{api_base_url}/teams/{team_id}', headers=response_headers, payload=team_info)
            data = await self.svc.update_team(team_id, name='New name', **kwargs)
        req_mock.assert_called_once_with(team_id, data={'name': 'New name'}, **kwargs)
        assert data == team_info

    async def test_delete_team(self, api_base_url, team_info, response_headers):
        team_id = team_info['id']
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
             mock.patch.object(self.svc, 'delete', side_effect=self.svc.delete) as req_mock:  # noqa
            m.delete(f'{api_base_url}/teams/{team_id}', status=204,
                     headers=response_headers)
            resp = await self.svc.delete_team(team_id, **kwargs)
        req_mock.assert_called_once_with(team_id, **kwargs)
        assert resp.status == 204


class TestApiServiceWebhooks(BaseTestApiService):
    svc_class = aiociscospark.services.ApiServiceWebhooks

    async def test_list_webhooks(self, api_base_url, response_headers, webhooks_list):
        data = []
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
             mock.patch.object(self.svc, 'get_items',
                               side_effect=self.svc.get_items) as get_items_mock:  # noqa
            m.get(f'{api_base_url}/webhooks', headers=response_headers, payload=webhooks_list)
            async for item, cursor in self.svc.list_webhooks(limit=10, **kwargs):
                data.append(item)
        get_items_mock.assert_called_once_with(
            {'max': 10, 'cursor': None},
            paginate=True,
            **kwargs
        )
        assert data == webhooks_list['items']

    async def test_get_webhook(self, api_base_url, response_headers, webhook_info):
        webhook_id = webhook_info['id']
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
             mock.patch.object(self.svc, 'get', side_effect=self.svc.get) as req_mock:  # noqa
            m.get(f'{api_base_url}/webhooks/{webhook_id}', headers=response_headers,
                  payload=webhook_info)
            data = await self.svc.get_webhook(webhook_id, **kwargs)
        req_mock.assert_called_once_with(webhook_id, **kwargs)
        assert data == webhook_info

    async def test_create_webhook(self, api_base_url, response_headers, webhook_info):
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
             mock.patch.object(self.svc, 'post', side_effect=self.svc.post) as req_mock:  # noqa
            m.post(f'{api_base_url}/webhooks', headers=response_headers, payload=webhook_info)
            data = await self.svc.create_webhook(
                name=webhook_info['name'],
                target_url=webhook_info['targetUrl'],
                resource_type=webhook_info['resource'],
                event_type=webhook_info['event'],
                secret=webhook_info['secret'],
                **kwargs
            )
        req_mock.assert_called_once_with(
            data={
                'name': webhook_info['name'],
                'targetUrl': webhook_info['targetUrl'],
                'resource': webhook_info['resource'],
                'event': webhook_info['event'],
                'filter': None,
                'secret': webhook_info['secret'],
            },
            **kwargs
        )
        assert data == webhook_info

    async def test_update_webhooks(self, api_base_url, response_headers, webhook_info):
        webhook_id = webhook_info['id']
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
            mock.patch.object(self.svc, 'put', side_effect=self.svc.put) as req_mock:  # noqa
            m.put(f'{api_base_url}/webhooks/{webhook_id}', headers=response_headers,
                  payload=webhook_info)
            data = await self.svc.update_webhook(webhook_id, name='New name', **kwargs)
        req_mock.assert_called_once_with(webhook_id,
                                         data={'name': 'New name', 'targetUrl': None}, **kwargs)
        assert data == webhook_info

    async def test_delete_webhook(self, api_base_url, webhook_info, response_headers):
        webhook_id = webhook_info['id']
        kwargs = {'timeout': 300}
        with aioresponses() as m, \
             mock.patch.object(self.svc, 'delete', side_effect=self.svc.delete) as req_mock:  # noqa
            m.delete(f'{api_base_url}/webhooks/{webhook_id}', status=204,
                     headers=response_headers)
            resp = await self.svc.delete_webhook(webhook_id, **kwargs)
        req_mock.assert_called_once_with(webhook_id, **kwargs)
        assert resp.status == 204
