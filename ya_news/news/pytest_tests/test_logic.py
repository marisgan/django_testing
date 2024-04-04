from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import WARNING
from news.models import Comment


@pytest.mark.parametrize(
    'parametrized_client, expected_count',
    (
        (pytest.lazy_fixture('client'), 0),
        (pytest.lazy_fixture('author_client'), 1)
    )
)
@pytest.mark.django_db
def test_adding_comments(
    parametrized_client, detail_url, comments_url, form_data,
    expected_count, news, author
):
    response = parametrized_client.post(detail_url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == expected_count
    if comments_count == 1:
        assertRedirects(response, comments_url)
        comment = Comment.objects.get()
        assert comment.text == form_data['text']
        assert comment.news == news
        assert comment.author == author


def test_user_cannot_add_forbidden_words(
        author_client, detail_url, forbidden_data
):
    response = author_client.post(detail_url, data=forbidden_data)
    assertFormError(
        response, form='form', field='text', errors=WARNING
    )
    assert Comment.objects.count() == 0


@pytest.mark.parametrize(
    'auth_client, expected_status, expected_count',
    (
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND, 1),
        (pytest.lazy_fixture('author_client'), HTTPStatus.FOUND, 0)
    )
)
@pytest.mark.django_db
def test_delete_comment_possibility(
    delete_url, comments_url, auth_client, expected_status, expected_count
):
    response = auth_client.delete(delete_url)
    assert response.status_code == expected_status
    if response.status_code == HTTPStatus.FOUND:
        assertRedirects(response, comments_url)
    assert Comment.objects.count() == expected_count


@pytest.mark.parametrize(
    'auth_client, expected_status',
    (
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.FOUND)
    )
)
@pytest.mark.django_db
def test_edit_comment_possibility(
    comment, edit_url, comments_url, auth_client, form_data, expected_status
):
    response = auth_client.post(edit_url, data=form_data)
    assert response.status_code == expected_status
    if response.status_code == HTTPStatus.NOT_FOUND:
        comment.refresh_from_db()
        assert comment.text != form_data['text']
    elif response.status_code == HTTPStatus.FOUND:
        comment.refresh_from_db()
        assert comment.text == form_data['text']
