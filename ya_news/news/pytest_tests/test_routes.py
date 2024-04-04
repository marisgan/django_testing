from http import HTTPStatus

from django.urls import reverse  # type: ignore

from pytest_django.asserts import assertRedirects
import pytest


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news_id')),
        ('users:login', None), ('users:logout', None), ('users:signup', None),
    )
)
def test_pages_availability_for_anonymous(client, name, args):
    response = client.get(reverse(name, args=args))
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'auth_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND)
    )
)
@pytest.mark.parametrize(
    'url',
    (pytest.lazy_fixture('edit_url'), pytest.lazy_fixture('delete_url'))
)
@pytest.mark.django_db
def test_edit_delete_pages_availability(url, auth_client, expected_status):
    response = auth_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (pytest.lazy_fixture('edit_url'), pytest.lazy_fixture('delete_url'))
)
@pytest.mark.django_db
def test_redirect_for_anonymous(client, url):
    response = client.get(url)
    expected_url = reverse('users:login') + f'?next={url}'
    assertRedirects(response, expected_url)
