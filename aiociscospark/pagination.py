import re
import urllib.parse

__all__ = (
    'ResponsePaginator',
)


def lazyproperty(func):
    name = '_lazy_{}'.format(func.__name__)

    @property
    def lazy(self):
        if hasattr(self, name):
            return getattr(self, name)
        else:
            value = func(self)
            setattr(self, name, value)
            return value
    return lazy


class ResponsePaginator(object):
    """
    A helper class that allows to walk through paged response.
    Documentation: https://developer.ciscospark.com/pagination.html
    """
    def __init__(self, response):
        self.response = response

    @staticmethod
    def parse_header_links(value):
        """
        Returns a dict of parsed link headers proxies.

        Borrowed from `requests.utils.parse_header_links`.
        :rtype: list
        """

        links = []

        replace_chars = ' \'"'

        for val in re.split(', *<', value):
            try:
                url, params = val.split(';', 1)
            except ValueError:
                url, params = val, ''

            link = {'url': url.strip('<> \'"')}

            for param in params.split(';'):
                try:
                    key, value = param.split('=')
                except ValueError:
                    break

                link[key.strip(replace_chars)] = value.strip(replace_chars)

            links.append(link)

        return links

    @lazyproperty
    def links(self):
        """
        Returns the parsed header links of the response, if any.

        Borrowed from: `requests.models.Response.links`.
        """
        header = self.response.headers.get('link')
        links = {}
        if header:
            header_links = self.parse_header_links(header)
            for link in header_links:
                key = link.get('rel') or link.get('url')
                links[key] = link
        return links

    @property
    def is_last_page(self):
        return not ('next' in self.links)

    @property
    def is_first_page(self):
        return not ('prev' in self.links)

    @property
    def is_only_page(self):
        return self.is_last_page and self.is_first_page

    @property
    def next_url(self):
        return urllib.parse.unquote(urllib.parse.unquote(self.links['next']['url']))

    @property
    def self_url(self):
        return self.links['self']['url'] \
            if 'self' in self.links else self.response.request_info.url

    def get_cursor(self, cursor='cursor'):
        if not self.is_last_page:
            parsed = urllib.parse.urlparse(self.next_url)
            return dict(urllib.parse.parse_qsl(parsed.query)).get(cursor, None)

    def get_limit_parameter(self):
        """
        Parses current (`self_url`) link URL and gets value of "max" parameter.

        :return: value of "max" parameter or zero "0" if no limit parameter defined
        :rtype: int
        """
        parsed = urllib.parse.urlparse(self.self_url)
        return int(dict(urllib.parse.parse_qsl(parsed.query)).get('max', 0))
