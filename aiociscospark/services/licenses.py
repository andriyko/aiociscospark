import logging

from .service import ApiResource, ApiService

logger = logging.getLogger(__name__)


class ApiServiceLicenses(ApiService):
    """
    Documentation: https://developer.ciscospark.com/resource-licenses.html
    """
    _resource = ApiResource('licenses', 'cursor')

    def list_licenses(self, org_id=None, limit=None, cursor=None, paginate=True, **kwargs):
        """
        List all licenses for a given organization.

        :return: async_generator object that produces the list of items.
        """
        params = {
            'orgId': org_id,
            'max': limit,
            'cursor': cursor
        }
        logger.debug('Getting licenses using parameters: %s', params)
        return self.get_items(params, paginate=paginate, **kwargs)

    def get_license(self, license_id, **kwargs):
        logger.debug('Getting license details: %s', license_id)
        return self.get(license_id, **kwargs)
