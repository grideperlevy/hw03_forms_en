import pytest
from django import forms
from posts.forms import PostForm
from posts.models import Post

from tests.utils import get_field_from_context


class TestPostView:

    @pytest.mark.django_db(transaction=True)
    def test_post_view_get(self, client, post_with_group):
        try:
            response = client.get(f'/posts/{post_with_group.id}')
        except Exception as e:
            assert False, f'''The `/posts/<post_id>/` page doesn't load properly. Error: `{e}`'''
        if response.status_code in (301, 302):
            response = client.get(f'/posts/{post_with_group.id}/')
        assert response.status_code != 404, (
            'The page `/posts/<post_id>/`  is not found, verify this path in *urls.py*'
        )

        post_context = get_field_from_context(response.context, Post)
        assert post_context is not None, (
            'Make sure that you passed an article to the page context of `/posts/<post_id>/` of type `Post`'
        )


class TestPostEditView:

    @pytest.mark.django_db(transaction=True)
    def test_post_edit_view_get(self, client, post_with_group):
        try:
            response = client.get(f'/posts/{post_with_group.id}/edit')
        except Exception as e:
            assert False, f'''The `/posts/<post_id>/edit/` page doesn't load properly. Error: `{e}`'''
        if (
                response.status_code in (301, 302)
                and not response.url.startswith(f'/posts/{post_with_group.id}')
        ):
            response = client.get(f'/posts/{post_with_group.id}/edit/')
        assert response.status_code != 404, (
            'The page `/posts/<post_id>/edit/` is not found, verify this path in *urls.py*'
        )

        assert response.status_code in (301, 302), (
            'Make sure that you redirect the user from the page '
            '`/<username>/<post_id>/edit/` to the post page if they are not the author'
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_edit_view_author_get(self, user_client, post_with_group):
        try:
            response = user_client.get(f'/posts/{post_with_group.id}/edit')
        except Exception as e:
            assert False, f'''The `/posts/<post_id>/edit/`  page doesn't load properly. Error: `{e}`'''
        if response.status_code in (301, 302):
            response = user_client.get(f'/posts/{post_with_group.id}/edit/')
        assert response.status_code != 404, (
            'The page `/posts/<post_id>/edit/` is not found, verify this path in *urls.py*'
        )

        post_context = get_field_from_context(response.context, Post)
        postform_context = get_field_from_context(response.context, PostForm)
        assert any([post_context, postform_context]) is not None, (
            'Make sure that you passed an article to the page context of `/posts/<post_id>/edit/` of type `Post` or `PostForm`'
        )

        assert 'form' in response.context, (
            'Make sure that you added `form` to the page context of `/posts/<post_id>/edit/`'
        )
        assert len(response.context['form'].fields) == 2, (
            'Make sure that the form `form` on the `/posts/<post_id>/edit/` page has 2 fields'
        )
        assert 'group' in response.context['form'].fields, (
            'Make sure that the form `form` on the `/posts/<post_id>/edit/` page has a `group` field'
        )
        assert type(response.context['form'].fields['group']) == forms.models.ModelChoiceField, (
            'Make sure that the form `form` on the `/posts/<post_id>/edit/` page has a `group` field of type `ModelChoiceField`'
        )
        assert not response.context['form'].fields['group'].required, (
            'Make sure that the form `form` on the `/posts/<post_id>/edit/` page has an optional `group` field'
        )

        assert 'text' in response.context['form'].fields, (
            'Make sure that the form `form` on the `/posts/<post_id>/edit/` page has a `text` field'
        )
        assert type(response.context['form'].fields['text']) == forms.fields.CharField, (
            'Make sure that the form `form` on the `/posts/<post_id>/edit/` page has a `text` field of type `CharField`'
        )
        assert response.context['form'].fields['text'].required, (
            'Make sure that the form `form` on the `/posts/<post_id>/edit/` page has a required `group` field'
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_edit_view_author_post(self, user_client, post_with_group):
        text = 'Post edit check!'
        try:
            response = user_client.get(f'/posts/{post_with_group.id}/edit')
        except Exception as e:
            assert False, f'''The `/posts/<post_id>/edit/` page doesn't load properly. Error: `{e}`'''
        url = (
            f'/posts/{post_with_group.id}/edit/'
            if response.status_code in (301, 302)
            else f'/posts/{post_with_group.id}/edit'
        )

        response = user_client.post(url, data={'text': text, 'group': post_with_group.group_id})

        assert response.status_code in (301, 302), (
            'Make sure that you redirect the user from the page `/posts/<post_id>/edit/` '
            'to the post page after the post was created'
        )
        post = Post.objects.filter(author=post_with_group.author, text=text, group=post_with_group.group).first()
        assert post is not None, (
            'Make sure that you edit the post when submitting the form on the page `/posts/<post_id>/edit/`'
        )
        assert response.url.startswith(f'/posts/{post_with_group.id}'), (
            'Make sure that you redirect the user to the post page `/posts/<post_id>/`'
        )
