import pytest

from news.forms import BAD_WORDS

HOME_URL = pytest.lazy_fixture('home_url')
LOGIN_URL = pytest.lazy_fixture('login_url')
SIGNUP_URL = pytest.lazy_fixture('signup_url')
LOGOUT_URL = pytest.lazy_fixture('logout_url')
DETAIL_URL = pytest.lazy_fixture('detail_url')
EDIT_URL = pytest.lazy_fixture('edit_url')
DELETE_URL = pytest.lazy_fixture('delete_url')
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')
READER_CLIENT = pytest.lazy_fixture('reader_client')
ANONYM_CLIENT = pytest.lazy_fixture('client')
REDIRECT_LOGIN_DELETE_URL = pytest.lazy_fixture('redirect_login_delete_url')
REDIRECT_LOGIN_EDIT_URL = pytest.lazy_fixture('redirect_login_edit_url')

NEW_COMMENT = {'text': 'New comment text'}
FORBIDDEN_TEXT = {'text': f'Text {BAD_WORDS[0]}'}
