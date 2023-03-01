import pytest
from django import forms
from posts.models import Post


class TestCreateView:

    @pytest.mark.django_db(transaction=True)
    def test_create_view_get(self, user_client):
        try:
            response = user_client.get('/create')
        except Exception as e:
            assert False, f'''The `/create` page doesn't load properly. Error: `{e}`'''
        if response.status_code in (301, 302):
            response = user_client.get('/create/')
        assert response.status_code != 404, 'The page `/create/`  is not found, verify this path in *urls.py*'
        assert 'form' in response.context, 'Make sure that you added `form` to the page context of `/create/`'
        assert len(response.context['form'].fields) == 2, 'Make sure that the form `form` on the `/create/` page has 2 fields'
        assert 'group' in response.context['form'].fields, (
            'Make sure that the form `form` on the `/create/` page has a `group` field'
        )
        assert type(response.context['form'].fields['group']) == forms.models.ModelChoiceField, (
            'Make sure that the form `form` on the `/create/` page has a `group` field of type `ModelChoiceField`'
        )
        assert not response.context['form'].fields['group'].required, (
            'Make sure that the form `form` on the `/create/` page has an optional `group` field'
        )

        assert 'text' in response.context['form'].fields, (
            'Make sure that the form `form` on the `/create/` page has a `text` field'
        )
        assert type(response.context['form'].fields['text']) == forms.fields.CharField, (
            'Make sure that the form `form` on the `/create/` page has a `text` field of type `CharField`'
        )
        assert response.context['form'].fields['text'].required, (
            'Make sure that the form `form` on the `/create/` page has a required `text` field'
        )

    @pytest.mark.django_db(transaction=True)
    def test_create_view_post(self, user_client, user, group):
        text = 'New post test!'
        try:
            response = user_client.get('/create')
        except Exception as e:
            assert False, f'''The `/create` page doesn't load properly. Error: `{e}`'''
        url = '/create/' if response.status_code in (301, 302) else '/create'

        response = user_client.post(url, data={'text': text, 'group': group.id})

        assert response.status_code in (301, 302), (
            'Make sure that after creating a post on the `/create/` page, '
            f'you redirect the user to their profile page `/profile/{user.username}`'
        )
        post = Post.objects.filter(author=user, text=text, group=group).first()
        assert post is not None, 'Make sure that you saved the new post when submitting the form on the `/create/` page'
        assert response.url == f'/profile/{user.username}/', (
            f'Make sure that you redirect the user to the author\'s profile page `/profile/{user.username}`'
        )

        text = 'New post test 2!'
        response = user_client.post(url, data={'text': text})
        assert response.status_code in (301, 302), (
            'Make sure that after creating a post on the `/create/` page, '
            f'you redirect the user to their profile page `/profile/{user.username}`'
        )
        post = Post.objects.filter(author=user, text=text, group__isnull=True).first()
        assert post is not None, 'Make sure that you saved the new post when submitting the form on the `/create/` page'
        assert response.url == f'/profile/{user.username}/', (
            f'Make sure that you redirect the user to the author\'s profile page `/profile/{user.username}`'
        )

        response = user_client.post(url)
        assert response.status_code == 200, (
            'Make sure that you display error messages in case of invalid `form` input on the `/create/` page'
        )
