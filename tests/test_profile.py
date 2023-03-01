import pytest
from django.contrib.auth import get_user_model
from django.core.paginator import Page

from tests.utils import get_field_from_context


class TestProfileView:

    @pytest.mark.django_db(transaction=True)
    def test_profile_view_get(self, client, post_with_group):
        try:
            response = client.get(f'/profile/{post_with_group.author.username}')
        except Exception as e:
            assert False, f'''The `/profile/<username>/` page doesn't load properly. Error: `{e}`'''
        if response.status_code in (301, 302):
            response = client.get(f'/profile/{post_with_group.author.username}/')
        assert response.status_code != 404, (
            'The page `/profile/<username>/` is not found, verify this path in *urls.py*'
        )

        profile_context = get_field_from_context(response.context, get_user_model())
        assert profile_context is not None, 'Make sure you added the author to the page context of `/profile/<username>/`'

        page_context = get_field_from_context(response.context, Page)
        assert page_context is not None, (
            'Make sure you added the author to the page context of the `/profile/<username>/` page of type `Page`'
        )
        assert len(page_context.object_list) == 1, (
            'Make sure you added the correct author articles to the page context of `/profile/<username>/`'
        )

        new_user = get_user_model()(username='new_user_87123478')
        new_user.save()
        try:
            new_response = client.get(f'/profile/{new_user.username}')
        except Exception as e:
            assert False, f'''The `/profile/<username>/` page doesn't load properly. Error: `{e}`'''
        if new_response.status_code in (301, 302):
            new_response = client.get(f'/profile/{new_user.username}/')

        page_context = get_field_from_context(new_response.context, Page)
        assert page_context is not None, (
            'Make sure you added the author to the page context of the `/profile/<username>/` page of type `Page`'
        )
        assert len(page_context.object_list) == 0, (
            'Make sure you added the correct author articles to the page context of `/profile/<username>/`'
        )
