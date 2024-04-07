import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from .constants import NEW_COMMENT, FORBIDDEN_FORM_DATAS
from news.forms import WARNING
from news.models import Comment


def test_anonym_cannot_add_comment(detail_url, client):
    comments = set(Comment.objects.all())
    client.post(detail_url, data=NEW_COMMENT)
    assert set(Comment.objects.all()) == comments


def test_user_can_add_comment(
        detail_url, news, author, author_client, comments_url
):
    comments = set(Comment.objects.all())
    assertRedirects(
        author_client.post(detail_url, data=NEW_COMMENT),
        comments_url
    )
    comments = set(Comment.objects.all()) - comments
    assert len(comments) == 1
    comment = comments.pop()
    assert comment.text == NEW_COMMENT['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.parametrize(
    'forbidden_form_data',
    FORBIDDEN_FORM_DATAS
)
def test_user_cannot_add_forbidden_words(
    author_client, detail_url, forbidden_form_data
):
    comments = set(Comment.objects.all())
    assertFormError(
        author_client.post(detail_url, data=forbidden_form_data),
        form='form', field='text', errors=WARNING
    )
    assert set(Comment.objects.all()) == comments


def test_author_can_delete_comment(
        delete_url, comments_url, author_client, comment
):
    comments_count = Comment.objects.count()
    assertRedirects(
        author_client.delete(delete_url),
        comments_url
    )
    assert Comment.objects.count() == comments_count - 1
    assert not Comment.objects.filter(id=comment.id).exists()


def test_user_cannot_delete_others_comment(delete_url, reader_client, comment):
    comments = set(Comment.objects.all())
    reader_client.delete(delete_url)
    assert set(Comment.objects.all()) == comments
    not_deleted_comment = Comment.objects.get(id=comment.id)
    assert not_deleted_comment.text == comment.text
    assert not_deleted_comment.news == comment.news
    assert not_deleted_comment.author == comment.author


def test_author_can_edit_own_comment(
        author_client, edit_url, comments_url, comment
):
    assertRedirects(
        author_client.post(edit_url, data=NEW_COMMENT),
        comments_url
    )
    edited_comment = Comment.objects.get(id=comment.id)
    assert edited_comment.text == NEW_COMMENT['text']
    assert edited_comment.news == comment.news
    assert edited_comment.author == comment.author


def test_user_cannot_edit_others_comment(reader_client, edit_url, comment):
    reader_client.post(edit_url, data=NEW_COMMENT)
    edited_comment = Comment.objects.get(id=comment.id)
    assert edited_comment.text == comment.text
    assert edited_comment.news == comment.news
    assert edited_comment.author == comment.author
