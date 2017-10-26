import logging

from .service import ApiResource, ApiService

logger = logging.getLogger(__name__)


class ApiServiceOrganizations(ApiService):
    """
    Documentation: https://developer.ciscospark.com/resource-organizations.html
    """
    _resource = ApiResource('organizations', 'cursor')

    def list_organizations(self, limit=None, cursor=None, paginate=True, **kwargs):
        """
        List all organizations visible by your account.

        :return: async_generator object that produces the list of items.
        """
        params = {
            'max': limit,
            'cursor': cursor
        }
        logger.debug('Getting organizations using parameters: %s', params)
        return self.get_items(params, paginate=paginate, **kwargs)

    def get_organization(self, org_id, **kwargs):
        logger.debug('Getting organization: %s', org_id)
        return self.get(org_id, **kwargs)
