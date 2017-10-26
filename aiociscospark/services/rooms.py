import logging

from .service import ApiResource, ApiService

logger = logging.getLogger(__name__)


class ApiServiceRooms(ApiService):
    """
    Documentation: https://developer.ciscospark.com/resource-rooms.html
    """
    _resource = ApiResource('rooms', 'cursor')

    def list_rooms(self, team_id=None, room_type=None, limit=None, sort_by=None, cursor=None,
                   paginate=True, **kwargs):
        """
        List rooms.

        :return: async_generator object that produces the list of items.
        """
        params = {
            'teamId': team_id,
            'type': room_type,
            'max': limit,
            'sortBy': sort_by,
            'cursor': cursor,
        }
        logger.debug('Getting rooms using parameters: %s', params)
        return self.get_items(params, paginate=paginate, **kwargs)

    def get_room(self, room_id, **kwargs):
        logger.debug('Getting room: %s', room_id)
        return self.get(room_id, **kwargs)

    def create_room(self, title=None, team_id=None, **kwargs):
        data = {
            'title': title,
            'teamId': team_id,
        }
        logger.debug('Creating room: %s', data)
        return self.post(data=data, **kwargs)

    def update_room(self, room_id, title=None, **kwargs):
        data = {
            'title': title,
        }
        logger.debug('Updating room: %s. Data: %s', room_id, data)
        return self.put(room_id, data=data, **kwargs)

    def delete_room(self, room_id, **kwargs):
        logger.debug('Deleting room: %s', room_id)
        return self.delete(room_id, **kwargs)
