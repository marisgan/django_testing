import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from .constants import NEW_COMMENT, FORBIDDEN_TEXTS
from news.forms import WARNING
from news.models import Comment


def test_anonym_cannot_add_comment(detail_url, client):
    comments_before = list(Comment.objects.all())
    client.post(detail_url, data=NEW_COMMENT)
    assert list(Comment.objects.all()) == comments_before


def test_user_can_add_comment(
        detail_url, news, author, author_client, comments_url
):
    comments_before = set(Comment.objects.all())
    response = author_client.post(detail_url, data=NEW_COMMENT)
    assertRedirects(response, comments_url)
    comments_after = set(Comment.objects.all())
    new_comments = comments_after.difference(comments_before)
    assert len(new_comments) == 1
    new_comment = new_comments.pop()
    assert new_comment.text == NEW_COMMENT['text']
    assert new_comment.news == news
    assert new_comment.author == author


@pytest.mark.parametrize(
    'forbidden_text',
    FORBIDDEN_TEXTS
)
def test_user_cannot_add_forbidden_words(
    author_client, detail_url, forbidden_text
):
    comments_before = list(Comment.objects.all())
    assertFormError(
        author_client.post(detail_url, data=forbidden_text),
        form='form', field='text', errors=WARNING
    )
    assert list(Comment.objects.all()) == comments_before


def test_author_can_delete_comment(
        delete_url, comments_url, author_client, comment
):
    comments_before = set(Comment.objects.all())
    assertRedirects(
        author_client.delete(delete_url),
        comments_url
    )
    comments_after = set(Comment.objects.all())
    deleted_comments = comments_before.difference(comments_after)
    assert len(deleted_comments) == 1
    deleted_comment = deleted_comments.pop()
    assert deleted_comment.text == comment.text
    assert deleted_comment.author == comment.author
    assert deleted_comment.news == comment.news


def test_user_cannot_delete_others_comment(delete_url, reader_client):
    comments_before = list(Comment.objects.all())
    reader_client.delete(delete_url)
    assert list(Comment.objects.all()) == comments_before


def test_author_can_edit_own_comment(
        author_client, edit_url, comments_url, comment
):
    original_comment = comment
    assertRedirects(
        author_client.post(edit_url, data=NEW_COMMENT),
        comments_url
    )
    edited_comment = Comment.objects.get(id=original_comment.id)
    assert edited_comment.text == NEW_COMMENT['text']
    assert edited_comment.news == original_comment.news
    assert edited_comment.author == original_comment.author


def test_user_cannot_edit_others_comment(reader_client, edit_url, comment):
    original_comment = comment
    reader_client.post(edit_url, data=NEW_COMMENT)
    edited_comment = Comment.objects.get(id=original_comment.id)
    assert edited_comment.text == original_comment.text
    assert edited_comment.news == original_comment.news
    assert edited_comment.author == original_comment.author
