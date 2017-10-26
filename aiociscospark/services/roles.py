import logging

from .service import ApiResource, ApiService

logger = logging.getLogger(__name__)


class ApiServiceRoles(ApiService):
    """
    Documentation: https://developer.ciscospark.com/endpoint-rooms-get.html
    """
    _resource = ApiResource('roles', 'cursor')

    def list_roles(self, limit=None, cursor=None, paginate=True, **kwargs):
        """
        Lists all roles.

        :return: async_generator object that produces the list of items.
        """
        params = {
            'max': limit,
            'cursor': cursor
        }
        logger.debug('Getting roles using parameters: %s', params)
        return self.get_items(params, paginate=paginate, **kwargs)

    def get_role(self, role_id, **kwargs):
        logger.debug('Getting role: %s', role_id)
        return self.get(role_id, **kwargs)
