import re

import pytest
from django.contrib.admin.sites import site
from django.contrib.auth import get_user_model
from django.db.models import fields
from django.template.loader import select_template

try:
    from posts.models import Post
except ImportError:
    assert False, 'The Post model is not found'

try:
    from posts.models import Group
except ImportError:
    assert False, 'The Group model is not found'


def search_field(fields, attname):
    for field in fields:
        if attname == field.attname:
            return field
    return None


def search_refind(execution, user_code):
    """Searching for launch"""
    for temp_line in user_code.split('\n'):
        if re.search(execution, temp_line):
            return True
    return False


class TestPost:

    def test_post_model(self):
        model_fields = Post._meta.fields
        text_field = search_field(model_fields, 'text')
        assert text_field is not None, 'Add the event name `text` to the `Post` model'
        assert type(text_field) == fields.TextField, (
            'The `text` attribute of the `Post` model must be of type `TextField`'
        )

        pub_date_field = search_field(model_fields, 'pub_date')
        assert pub_date_field is not None, 'Add the date and time of the event: the `pub_date` field of the `Post` model'
        assert type(pub_date_field) == fields.DateTimeField, (
            'The `pub_date`  attribute of the `Post` model must be of type `DateTimeField`'
        )
        assert pub_date_field.auto_now_add, 'The `pub_date` attribute of the `Post` model must be of type `auto_now_add`'

        author_field = search_field(model_fields, 'author_id')
        assert author_field is not None, 'Add author: the `author` field of the `Post` model'
        assert type(author_field) == fields.related.ForeignKey, (
            'The `author` field of the `Post` model must be a `ForeignKey`, a reference to another model'
        )
        assert author_field.related_model == get_user_model(), (
            'The `author` field of the `Post` model must be a reference to the `User` model'
        )

        group_field = search_field(model_fields, 'group_id')
        assert group_field is not None, 'Add a `group` attribute to the `Post` model'
        assert type(group_field) == fields.related.ForeignKey, (
            'The `group` field of the `Post` model must be a `ForeignKey`, a reference to another model'
        )
        assert group_field.related_model == Group, (
            'The `group` field of the `Post` model must be a reference to the `Group` model'
        )
        assert group_field.blank, (
            'The `group` attribute of the `Post` model must have the parameter `blank=True`'
        )
        assert group_field.null, (
            'The `group` attribute of the `Post` model must have the parameter `null=True`'
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_create(self, user):
        text = 'Test post'
        author = user

        assert Post.objects.all().count() == 0

        post = Post.objects.create(text=text, author=author)
        assert Post.objects.all().count() == 1
        assert Post.objects.get(text=text, author=author).pk == post.pk

    def test_post_admin(self):
        admin_site = site

        assert Post in admin_site._registry, 'Register the `Post` model in the admin site'

        admin_model = admin_site._registry[Post]

        assert 'text' in admin_model.list_display, (
            'Display `text` in the admin interface'
        )
        assert 'pub_date' in admin_model.list_display, (
            'Display `pub_date` in the admin interface'
        )
        assert 'author' in admin_model.list_display, (
            'Display `author` in the admin interface'
        )

        assert 'text' in admin_model.search_fields, (
            'Add an option to search by `text` in the admin interface'
        )

        assert 'pub_date' in admin_model.list_filter, (
            'Add a filter by `pub_date` in the admin interface'
        )

        assert hasattr(admin_model, 'empty_value_display'), (
            'Add a default value `-empty-` for empty fields'
        )
        assert admin_model.empty_value_display == '-empty-', (
            'Add a default value `-empty-` for empty fields'
        )


class TestGroup:

    def test_group_model(self):
        model_fields = Group._meta.fields
        title_field = search_field(model_fields, 'title')
        assert title_field is not None, 'Add the event name `title` to the `Group` model'
        assert type(title_field) == fields.CharField, (
            'The `title` attribute of the `Group` model must be of type `CharField`'
        )
        assert title_field.max_length == 200, 'Set the max length of the `title` model `Group` to 200'

        slug_field = search_field(model_fields, 'slug')
        assert slug_field is not None, 'Add a slug `slug` to the `Group` model'
        assert type(slug_field) == fields.SlugField, (
            'The `slug` attribute of the `Group` model must be of type `SlugField`'
        )
        assert slug_field.unique, 'The `slug` attribute of the `Group` model must be unique'

        description_field = search_field(model_fields, 'description')
        assert description_field is not None, 'Add a description `description` of the `Group` model'
        assert type(description_field) == fields.TextField, (
            'The `Group` model\'s `description` attribute must be a `TextField`'
        )

    @pytest.mark.django_db(transaction=True)
    def test_group_create(self, user):
        text = 'Test post'
        author = user

        assert Post.objects.all().count() == 0

        post = Post.objects.create(text=text, author=author)
        assert Post.objects.all().count() == 1
        assert Post.objects.get(text=text, author=author).pk == post.pk

        title = 'Test group'
        slug = 'test-link'
        description = 'Test group description'

        assert Group.objects.all().count() == 0
        group = Group.objects.create(title=title, slug=slug, description=description)
        assert Group.objects.all().count() == 1
        assert Group.objects.get(slug=slug).pk == group.pk

        post.group = group
        post.save()
        assert Post.objects.get(text=text, author=author).group == group


class TestGroupView:

    @pytest.mark.django_db(transaction=True)
    def test_group_view(self, client, post_with_group):
        try:
            response = client.get(f'/group/{post_with_group.group.slug}')
        except Exception as e:
            assert False, f'''The `/group/<slug>/` page doesn't load properly. Error: `{e}`'''
        if response.status_code in (301, 302):
            response = client.get(f'/group/{post_with_group.group.slug}/')
        if response.status_code == 404:
            assert False, 'The page `/group/<slug>/` is not found, verify this path in *urls.py*'

        if response.status_code != 200:
            assert False, 'The page `/group/<slug>/` does not load correctly.'
        group = post_with_group.group
        html = response.content.decode()

        templates_list = ['group_list.html', 'posts/group_list.html']
        html_template = select_template(templates_list).template.source

        assert search_refind(r'{%\s*for\s+.+in.*%}', html_template), (
            'Edit the HTML template, use a loop attribute'
        )
        assert search_refind(r'{%\s*endfor\s*%}', html_template), (
            'Edit the HTML template, the closing loop attribute is not found'
        )

        assert re.search(
            r'<\s*h1\s*>\s*' + group.title + r'\s*<\s*\/h1\s*>',
            html
        ), (
            'Edit the HTML template, the group title is not found '
            '`{% block header %}{{ group_name }}{% endblock %}`'
        )
        assert re.search(
            r'<\s*p\s*>\s*' + group.description + r'\s*<\s*\/p\s*>',
            html
        ), 'Edit the HTML template, the group description `<p>{{ group_description }}</p>`'
