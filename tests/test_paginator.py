import pytest
from django.core.paginator import Page, Paginator

pytestmark = [pytest.mark.django_db]


class TestGroupPaginatorView:

    def test_group_paginator_view_get(self, client, few_posts_with_group):
        try:
            response = client.get(f'/group/{few_posts_with_group.group.slug}')
        except Exception as e:
            assert False, f'''The `/group/<slug>/` page doesn't load properly. Error: `{e}`'''
        if response.status_code in (301, 302):
            response = client.get(f'/group/{few_posts_with_group.group.slug}/')
        assert response.status_code != 404, 'The page `/group/<slug>/` is not found, verify this path in *urls.py*'
        assert 'page_obj' in response.context, (
            'Make sure that you added the `page_obj` variable to the page context of `/group/<slug>/`'
        )
        assert isinstance(response.context['page_obj'], Page), (
            'Make sure that the `page_obj` variable on the `/group/<slug>/` page is of type `Page`'
        )

    def test_group_paginator_not_in_context_view(self, client, post_with_group):
        response = client.get(f'/group/{post_with_group.group.slug}/')
        assert response.status_code != 404, 'The page `/group/<slug>/` is not found, verify this path in *urls.py*'
        assert isinstance(response.context['page_obj'].paginator, Paginator), (
            'Make sure that the  `paginator` variable on the `/group/<slug>/` page is of type `Paginator`'
        )

    def test_index_paginator_not_in_view_context(self, client, few_posts_with_group):
        response = client.get('/')
        assert isinstance(response.context['page_obj'].paginator, Paginator), (
            'Make sure that the `paginator` variable of the `page_obj` object on the `/` page is of type `Paginator`'
        )

    def test_index_paginator_view(self, client, post_with_group):
        response = client.get('/')
        assert response.status_code != 404, 'The page `/` is not found, verify this path in *urls.py*'
        assert 'page_obj' in response.context, (
            'Make sure that you added the `page_obj` variable to the page context of `/`'
        )
        assert isinstance(response.context['page_obj'], Page), (
            'Make sure that the `page_obj` variable on the `/` page is of type `Page`'
        )

    def test_profile_paginator_view(self, client, few_posts_with_group):
        response = client.get(f'/profile/{few_posts_with_group.author.username}/')
        assert isinstance(response.context['page_obj'].paginator, Paginator), (
            'Make sure that the `paginator` variable of the `page_obj` object'
            ' on the `/profile/<username>/` page is of type `Paginator`'
        )
