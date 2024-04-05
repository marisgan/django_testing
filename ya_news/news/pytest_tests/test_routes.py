from http import HTTPStatus

from pytest_django.asserts import assertRedirects
import pytest

from .constants import (
    AUTHOR_CLIENT, ANONYM_CLIENT, DELETE_URL, DETAIL_URL,
    EDIT_URL, HOME_URL, LOGIN_URL, LOGOUT_URL, READER_CLIENT,
    REDIRECT_LOGIN_DELETE_URL, REDIRECT_LOGIN_EDIT_URL, SIGNUP_URL,
)


@pytest.mark.parametrize(
    'parametrized_client, url, expected_status',
    (
        (ANONYM_CLIENT, HOME_URL, HTTPStatus.OK),
        (ANONYM_CLIENT, DETAIL_URL, HTTPStatus.OK),
        (ANONYM_CLIENT, LOGIN_URL, HTTPStatus.OK),
        (ANONYM_CLIENT, LOGOUT_URL, HTTPStatus.OK),
        (ANONYM_CLIENT, SIGNUP_URL, HTTPStatus.OK),
        (AUTHOR_CLIENT, EDIT_URL, HTTPStatus.OK),
        (AUTHOR_CLIENT, DELETE_URL, HTTPStatus.OK),
        (READER_CLIENT, EDIT_URL, HTTPStatus.NOT_FOUND),
        (READER_CLIENT, DELETE_URL, HTTPStatus.NOT_FOUND)
    )
)
def test_pages_availability(parametrized_client, url, expected_status):
    assert parametrized_client.get(url).status_code == expected_status


@pytest.mark.parametrize(
    'url, expected_redirect',
    (
        (EDIT_URL, REDIRECT_LOGIN_EDIT_URL),
        (DELETE_URL, REDIRECT_LOGIN_DELETE_URL)
    )
)
def test_redirects_for_anonym(client, url, expected_redirect):
    assertRedirects(client.get(url), expected_redirect)
