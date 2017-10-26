import logging

from .service import ApiResource, ApiService

logger = logging.getLogger(__name__)


class ApiServicePeople(ApiService):
    """
    Documentation: https://developer.ciscospark.com/resource-people.html
    """
    _resource = ApiResource('people', 'cursor')

    def list_people(self, email=None, display_name=None, limit=None, cursor=None,
                    paginate=True, **kwargs):
        """
        List people in the organization.

        :return: async_generator object that produces the list of items.
        """
        params = {
            'email': email,
            'displayName': display_name,
            'max': limit,
            'cursor': cursor
        }
        logger.debug('Getting people using parameters: %s', params)
        return self.get_items(params, paginate=paginate, **kwargs)

    def get_person(self, person_id, **kwargs):
        logger.debug('Getting person details: %s', person_id)
        return self.get(person_id, **kwargs)

    def me(self, **kwargs):
        """
        Fetches the details of the authenticated user.
        """
        return self.get_person('me', **kwargs)

    @staticmethod
    def _normalize_data(emails=None, display_name=None, first_name=None, last_name=None,
                        avatar=None, org_id=None, roles=None, licenses=None):
        return {
            'emails': emails,
            'displayName': display_name,
            'firstName': first_name,
            'lastName': last_name,
            'avatar': avatar,
            'orgId': org_id,
            'roles': roles,
            'licenses': licenses
        }

    def create_person(self, emails=None, display_name=None, first_name=None, last_name=None,
                      avatar=None, org_id=None, roles=None, licenses=None, **kwargs):
        data = self._normalize_data(emails=emails, display_name=display_name, first_name=first_name,
                                    last_name=last_name, avatar=avatar, org_id=org_id, roles=roles,
                                    licenses=licenses)
        logger.debug('Creating person: %s', data)
        return self.post(data=data, **kwargs)

    def update_person(self, person_id, emails=None, display_name=None, first_name=None,
                      last_name=None, avatar=None, org_id=None, roles=None, licenses=None, **kwargs):
        data = self._normalize_data(emails=emails, display_name=display_name, first_name=first_name,
                                    last_name=last_name, avatar=avatar, org_id=org_id, roles=roles,
                                    licenses=licenses)
        logger.debug('Updating person: %s. Data: %s', person_id, data)
        return self.put(person_id, data=data, **kwargs)

    def delete_person(self, person_id, **kwargs):
        logger.debug('Deleting person: %s', person_id)
        return self.delete(person_id, **kwargs)
