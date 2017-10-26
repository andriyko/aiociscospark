import logging

from .service import ApiResource, ApiService

logger = logging.getLogger(__name__)


class ApiServiceRoomMemberships(ApiService):
    """
    Documentation: https://developer.ciscospark.com/resource-memberships.html
    """
    _resource = ApiResource('memberships', 'cursor')

    def list_memberships(self, room_id=None, person_id=None, person_email=None, limit=None,
                         cursor=None, paginate=True, **kwargs):
        """
        List all room memberships.

        :return: async_generator object that produces the list of items.
        """
        params = {
            'roomId': room_id,
            'personId': person_id,
            'personEmail': person_email,
            'max': limit,
            'cursor': cursor
        }
        logger.debug('Getting room memberships using parameters: %s', room_id)
        return self.get_items(params, paginate=paginate, **kwargs)

    def get_membership(self, membership_id, **kwargs):
        logger.info('Getting membership: %s', membership_id)
        return self.get(membership_id, **kwargs)

    def create_membership(self, room_id=None, person_id=None, person_email=None, is_moderator=None,
                          **kwargs):
        data = {
            'roomId': room_id,
            'personId': person_id,
            'personEmail': person_email,
            'isModerator': is_moderator,
        }
        logger.info('Creating membership: %s', data)
        return self.post(data=data, **kwargs)

    def update_membership(self, membership_id, is_moderator=None, **kwargs):
        data = {
            'isModerator': is_moderator,
        }
        logger.info('Updating membership: %s. Data: %s', membership_id, data)
        return self.put(membership_id, data=data, **kwargs)

    def delete_membership(self, membership_id, **kwargs):
        logger.info('Deleting membership: %s', membership_id)
        return self.delete(membership_id, **kwargs)
