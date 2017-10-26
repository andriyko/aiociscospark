import pytest

from .context import aiociscospark


class TestResponsePaginator:
    @pytest.fixture(scope='function', autouse=True)
    def setup(self, event_loop, fake_resp_with_next_link):
        resp = event_loop.run_until_complete(fake_resp_with_next_link)
        self.paginator = aiociscospark.pagination.ResponsePaginator(resp)

    def test_parse_header_links(self, test_url):
        link_header = self.paginator.response.headers.get('link')
        links = self.paginator.parse_header_links(link_header)
        assert links == [
            {'rel': 'next', 'url': f'{test_url}?max=1&cursor=bGltaXQ9MiZzdGFydEluZGV4PTM='},
        ]
        assert self.paginator.parse_header_links('') == [{'url': ''}]

    def test_links_property_has_correct_values(self, test_url):
        assert self.paginator.links == {
            'next': {'rel': 'next', 'url': f'{test_url}?max=1&cursor=bGltaXQ9MiZzdGFydEluZGV4PTM='}
        }

    def test_links_property_is_lazy_loaded(self):
        assert getattr(self.paginator, '_lazy_links', None) is None
        links1 = self.paginator.links
        links2 = self.paginator.links
        assert links1 is links2 is self.paginator._lazy_links

    def test_is_last_page(self):
        assert not self.paginator.is_last_page

    def test_is_first_page(self):
        assert self.paginator.is_first_page

    def test_is_only_page(self):
        assert not self.paginator.is_only_page

    def test_next_url(self, test_url):
        assert self.paginator.next_url == f'{test_url}?max=1&cursor=bGltaXQ9MiZzdGFydEluZGV4PTM='

    def test_self_url(self, test_url):
        assert self.paginator.self_url == test_url

    def test_get_cursor(self):
        assert self.paginator.get_cursor() == 'bGltaXQ9MiZzdGFydEluZGV4PTM='

    def test_get_limit_parameter(self):
        assert self.paginator.get_limit_parameter() == 0
