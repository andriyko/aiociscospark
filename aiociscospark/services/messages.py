import logging

from .service import ApiResource, ApiService

logger = logging.getLogger(__name__)


class ApiServiceMessages(ApiService):
    """
    Documentation: https://developer.ciscospark.com/resource-messages.html
    """
    _resource = ApiResource('messages', 'beforeMessage')

    def list_messages(self, room_id, mentioned_people=None, before_date=None, before_message=None,
                      limit=None, cursor=None, paginate=True, **kwargs):
        """
        List all messages in a room.

        :return: async_generator object that produces the list of items.
        """
        params = {
            'roomId': room_id,
            'mentionedPeople': mentioned_people,
            'before': before_date,
            'beforeMessage': before_message,
            'max': limit,
            'cursor': cursor,
        }
        logger.debug('Getting messages using parameters: %s', params)
        return self.get_items(params, paginate=paginate, **kwargs)

    def get_message(self, message_id, **kwargs):
        logger.debug('Getting message: %s', message_id)
        return self.get(message_id, **kwargs)

    def create_message(self, room_id=None, to_person_id=None, to_person_email=None,
                       text=None, markdown=None, files=None, **kwargs):
        """
        Create new message.

        When uploading files directly from your local filesystem, your request will need to be a
        multipart/form-data request rather than JSON. If you have a file available via a
        publicly-accessible URL that you wish to share, you can use the URL as the value in the
        files JSON parameter instead of attaching your local file in a multipart message.
        """
        data = {
            'roomId': room_id,
            'toPersonId': to_person_id,
            'toPersonEmail': to_person_email,
            'text': text,
            'markdown': markdown,
            'files': files
        }
        logger.debug('Creating message: %s', data)
        return self.post(data=data, **kwargs)

    def delete_message(self, message_id, **kwargs):
        logger.debug('Deleting message: %s', message_id)
        return self.delete(message_id, **kwargs)
