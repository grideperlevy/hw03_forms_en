import pytest


class TestTemplateView:

    @pytest.mark.django_db(transaction=True)
    def test_about_author_tech(self, client):
        urls = ['/about/author/', '/about/tech/']
        for url in urls:
            try:
                response = client.get(url)
            except Exception as e:
                assert False, f'''The `{url}` page doesn't load properly. Error: `{e}`'''
            assert response.status_code != 404, f'The page `{url}` is not found, verify this path in *urls.py*'
            assert response.status_code == 200, (
                f'Error {response.status_code} when opening `{url}`. Check the corresponding view function'
            )
