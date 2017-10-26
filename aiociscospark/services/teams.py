import logging

from .service import ApiResource, ApiService

logger = logging.getLogger(__name__)


class ApiServiceTeams(ApiService):
    """
    Documentation: https://developer.ciscospark.com/resource-teams.html
    """
    _resource = ApiResource('teams', 'cursor')

    def list_teams(self, limit=None, cursor=None, paginate=True, **kwargs):
        """
        Lists teams to which the authenticated user belongs.

        :return: async_generator object that produces the list of items.
        """
        params = {
            'max': limit,
            'cursor': cursor
        }
        logger.debug('Getting teams using parameters: %s', params)
        return self.get_items(params, paginate=paginate, **kwargs)

    def get_team(self, team_id, **kwargs):
        logger.debug('Getting team: %s', team_id)
        return self.get(team_id, **kwargs)

    def create_team(self, name=None, **kwargs):
        data = {'name': name}
        logger.debug('Creating team: %s', data)
        return self.post(data=data, **kwargs)

    def update_team(self, team_id, name=None, **kwargs):
        data = {'name': name}
        logger.debug('Updating team: %s. Data: %s', team_id, data)
        return self.put(team_id, data=data, **kwargs)

    def delete_team(self, team_id, **kwargs):
        logger.debug('Deleting team: %s', team_id)
        return self.delete(team_id, **kwargs)
