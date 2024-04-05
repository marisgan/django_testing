from pytest_django.asserts import assertRedirects, assertFormError

from .constants import NEW_COMMENT, FORBIDDEN_TEXT
from news.forms import WARNING
from news.models import Comment


def test_anonym_cannot_add_comment(detail_url, client):
    before_test_count = Comment.objects.count()
    client.post(detail_url, data=NEW_COMMENT)
    assert Comment.objects.count() == before_test_count


def test_user_can_add_comment(
        detail_url, news, author, author_client, comments_url
):
    before_test_count = Comment.objects.count()
    response = author_client.post(detail_url, data=NEW_COMMENT)
    assertRedirects(response, comments_url)
    assert Comment.objects.count() == before_test_count + 1
    new_comment = Comment.objects.get(text=NEW_COMMENT['text'])
    assert new_comment.text == NEW_COMMENT['text']
    assert new_comment.news == news
    assert new_comment.author == author


def test_user_cannot_add_forbidden_words(author_client, detail_url):
    before_text_count = Comment.objects.count()
    assertFormError(
        author_client.post(detail_url, data=FORBIDDEN_TEXT),
        form='form', field='text', errors=WARNING
    )
    assert Comment.objects.count() == before_text_count


def test_author_can_delete_comment(delete_url, comments_url, author_client):
    before_test_count = Comment.objects.count()
    assertRedirects(
        author_client.delete(delete_url),
        comments_url
    )
    assert Comment.objects.count() == before_test_count - 1


def test_user_cannot_delete_others_comment(delete_url, reader_client):
    before_test_count = Comment.objects.count()
    reader_client.delete(delete_url)
    assert Comment.objects.count() == before_test_count


def test_author_can_edit_own_comment(
        author_client, edit_url, comments_url, author, news
):
    assertRedirects(
        author_client.post(edit_url, data=NEW_COMMENT),
        comments_url
    )
    edited_comment = Comment.objects.get(text=NEW_COMMENT['text'])
    assert edited_comment.text == NEW_COMMENT['text']
    assert edited_comment.news == news
    assert edited_comment.author == author


def test_user_cannot_edit_others_comment(reader_client, edit_url, comment):
    comment_before_test = comment
    reader_client.post(edit_url, data=NEW_COMMENT)
    comment.refresh_from_db()
    assert comment.text == comment_before_test.text
    assert comment.news == comment_before_test.news
    assert comment.author == comment_before_test.author
