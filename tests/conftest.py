import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root_dir_content = os.listdir(BASE_DIR)
PROJECT_DIR_NAME = 'wordicum'
# Make sure that the root directory contains the project directory
if (
        PROJECT_DIR_NAME not in root_dir_content
        or not os.path.isdir(os.path.join(BASE_DIR, PROJECT_DIR_NAME))
):
    assert False, (
        f'The `{BASE_DIR}` directory does not contain the project folder `{PROJECT_DIR_NAME}`. '
        f'Make sure you have the correct project tree structure.'
    )

MANAGE_PATH = os.path.join(BASE_DIR, PROJECT_DIR_NAME)
project_dir_content = os.listdir(MANAGE_PATH)
FILENAME = 'manage.py'
# Make sure that the structure is correct and manage.py is in place
if FILENAME not in project_dir_content:
    assert False, (
        f'The `{MANAGE_PATH}` directory does not contain the `{FILENAME}` file. '
        f'Make sure you have the correct project tree structure.'
    )

from django.utils.version import get_version

assert get_version() < '3.0.0', 'Please use Django version < 3.0.0'

from wordicum.settings import INSTALLED_APPS

assert any(app in INSTALLED_APPS for app in ['posts.apps.PostsConfig', 'posts']), (
    'Please register the app in `settings.INSTALLED_APPS`'
)

pytest_plugins = [
    'tests.fixtures.fixture_user',
    'tests.fixtures.fixture_data',
]
