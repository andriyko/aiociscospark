import logging

from .service import ApiResource, ApiService

logger = logging.getLogger(__name__)


class ApiServiceTeamMemberships(ApiService):
    """
    Documentation: https://developer.ciscospark.com/resource-team-memberships.html
    """
    _resource = ApiResource('team/memberships', 'cursor')

    def list_memberships(self, team_id=None, limit=None, cursor=None, paginate=True, **kwargs):
        """
        List all team memberships.

        By default, lists memberships for teams to which the authenticated user belongs.

        :return: async_generator object that produces the list of items.
        """
        params = {
            'teamId': team_id,
            'max': limit,
            'cursor': cursor
        }
        logger.debug('Getting team memberships using parameters: %s', team_id)
        return self.get_items(params, paginate=paginate, **kwargs)

    def get_membership(self, team_membership_id, **kwargs):
        logger.debug('Getting team membership: %s', team_membership_id)
        return self.get(team_membership_id, **kwargs)

    def create_membership(self, team_id=None, person_id=None, person_email=None, is_moderator=None,
                          **kwargs):
        data = {
            'teamId': team_id,
            'personId': person_id,
            'personEmail': person_email,
            'isModerator': is_moderator,
        }
        logger.debug('Creating team membership: %s', data)
        return self.post(data=data, **kwargs)

    def update_membership(self, membership_id, is_moderator=None, **kwargs):
        data = {
            'isModerator': is_moderator,
        }
        logger.debug('Updating team membership: %s. Data: %s', membership_id, data)
        return self.put(membership_id, data=data, **kwargs)

    def delete_membership(self, membership_id, **kwargs):
        logger.debug('Deleting membership: %s', membership_id)
        return self.delete(membership_id, **kwargs)
