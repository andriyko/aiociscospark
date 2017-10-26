import logging
import re

from .service import ApiResource, ApiService

logger = logging.getLogger(__name__)


class ApiServiceContents(ApiService):
    _resource = ApiResource('contents', 'cursor')

    def _get_content_url(self, content_id=None, content_url=None):
        if not (content_id or content_url):
            raise ValueError('Either "content_id" or "content_url" of content is required')
        return self.get_resource_url(id_or_path=content_id) if content_id else content_url

    async def get_content_info(self, content_id=None, content_url=None, **kwargs):
        logger.debug('Getting content info: content_id="%s", content_url="%s"',
                     content_id, content_url)
        url = self._get_content_url(content_id=content_id, content_url=content_url)
        resp = await self.http_client.head(url, **kwargs)
        match = re.match(r'^attachment; filename="(?P<file_name>.*?)"$',
                         resp.headers['Content-Disposition'])
        return {
            'content_name': match.groupdict()['file_name'],
            'content_size': int(resp.headers['Content-Length']),
            'content_type': resp.headers['Content-Type'],
        }

    async def get_content(self, content_id=None, content_url=None, **kwargs):
        logger.debug('Getting content: content_id="%s", content_url="%s"', content_id, content_url)
        url = self._get_content_url(content_id=content_id, content_url=content_url)
        resp = await self.http_client.get(url, **kwargs)
        return await resp.text()
