import logging

from . import http_client  # noqa
from . import services  # noqa
from . import utils  # noqa
from . import exceptions  # noqa

from .constants import API_BASE_URL, API_V1  # noqa
from .exceptions import (SparkClientConfigurationError, SparkRateLimitExceeded, SparkResponseError,  # noqa
                         SparkResponseNotReceived)  # noqa
from .http_client import HTTPClient  # noqa
from .pagination import ResponsePaginator  # noqa
from .utils import Credentials, get_access_token, refresh_access_token  # noqa
from . __version__ import __version__  # noqa

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

__all__ = (
    http_client.__all__ +  # noqa
    utils.__all__ +  # noqa
    (
        'API_BASE_URL',
        'API_V1',
        'SparkClientConfigurationError',
        'SparkRateLimitExceeded',
        'SparkResponseError',
        'SparkResponseNotReceived',
        'ResponsePaginator',
        'APIClient',
        'get_client',
    )
)


class APIClient(object):
    http_client_class = http_client.HTTPClient

    def __init__(self, creds, *, loop=None, **kwargs):
        self.http_client = self.http_client_class(creds, loop=loop)

        self.contents = services.ApiServiceContents(self.http_client)
        self.licenses = services.ApiServiceLicenses(self.http_client)
        self.messages = services.ApiServiceMessages(self.http_client)
        self.organizations = services.ApiServiceOrganizations(self.http_client)
        self.people = services.ApiServicePeople(self.http_client)
        self.roles = services.ApiServiceRoles(self.http_client)
        self.room_memberships = services.ApiServiceRoomMemberships(self.http_client)
        self.rooms = services.ApiServiceRooms(self.http_client)
        self.team_memberships = services.ApiServiceTeamMemberships(self.http_client)
        self.teams = services.ApiServiceTeams(self.http_client)
        self.webhooks = services.ApiServiceWebhooks(self.http_client)


def get_client(credentials, *, register_response_handlers=True, loop=None, **kwargs):
    client = APIClient(credentials, loop=loop, **kwargs)
    if register_response_handlers:
        client.http_client.register_response_handlers()
    return client
