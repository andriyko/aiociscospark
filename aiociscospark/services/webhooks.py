import logging

from .service import ApiResource, ApiService

logger = logging.getLogger(__name__)


class ApiServiceWebhooks(ApiService):
    """
    Documentation: https://developer.ciscospark.com/resource-webhooks.html
    """
    _resource = ApiResource('webhooks', 'cursor')

    def list_webhooks(self, limit=None, cursor=None, paginate=True, **kwargs):
        """
        List all of your webhooks.

        :return: async_generator object that produces the list of items.
        """
        params = {
            'max': limit,
            'cursor': cursor
        }
        logger.debug('Getting webhooks using parameters: %s', params)
        return self.get_items(params, paginate=paginate, **kwargs)

    def get_webhook(self, person_id, **kwargs):
        logger.debug('Getting person details: %s', person_id)
        return self.get(person_id, **kwargs)

    def create_webhook(self, name=None, target_url=None, resource_type=None, event_type=None,
                       afilter=None, secret=None, **kwargs):
        data = {
            'name': name,
            'targetUrl': target_url,
            'resource': resource_type,
            'event': event_type,
            'filter': afilter,
            'secret': secret,
        }
        logger.debug('Creating webhook: %s', data)
        return self.post(data=data, **kwargs)

    def update_webhook(self, webhook_id, name=None, target_url=None, **kwargs):
        data = {
            'name': name,
            'targetUrl': target_url,
        }
        logger.debug('Updating webhook: %s. Data: %s', webhook_id, data)
        return self.put(webhook_id, data=data, **kwargs)

    def delete_webhook(self, webhook_id, **kwargs):
        logger.debug('Deleting webhook: %s', webhook_id)
        return self.delete(webhook_id, **kwargs)
