import mock

from .context import aiociscospark


class TestSparkAppClient:
    def test_initialization(self, event_loop, credentials):
        with mock.patch.object(aiociscospark.APIClient, 'http_client_class',
                               side_effect=aiociscospark.http_client.HTTPClient) as http_client_class_mock:  # noqa
            client = aiociscospark.APIClient(credentials, loop=event_loop)
        assert isinstance(client.http_client, aiociscospark.http_client.HTTPClient)
        http_client_class_mock.assert_called_once_with(credentials, loop=event_loop)
        for svc in ['contents', 'licenses', 'messages', 'organizations', 'people', 'roles',
                    'room_memberships', 'rooms', 'team_memberships', 'teams', 'webhooks']:
            assert isinstance(getattr(client, svc), aiociscospark.services.ApiService)


def test_get_client(event_loop, credentials):
    client = aiociscospark.get_client(credentials, loop=event_loop)
    assert isinstance(client, aiociscospark.APIClient)
