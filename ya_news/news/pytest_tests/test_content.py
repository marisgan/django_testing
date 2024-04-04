from django.conf import settings  # type: ignore

import pytest

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, news_feed, home_url):
    response = client.get(home_url)
    news_count = response.context['object_list'].count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, news_feed, home_url):
    response = client.get(home_url)
    all_dates = [news.date for news in response.context['object_list']]
    assert all_dates == sorted(all_dates, reverse=True)


@pytest.mark.django_db
def test_comments_order(client, comment, comment2, detail_url):
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    assert news.comment_set.count() == 2
    timestamps = [comment.created for comment in news.comment_set.all()]
    assert timestamps == sorted(timestamps)


@pytest.mark.parametrize(
    'parametrized_client, available',
    (
        (pytest.lazy_fixture('reader_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
@pytest.mark.django_db
def test_form_availability(detail_url, parametrized_client, available):
    response = parametrized_client.get(detail_url)
    assert ('form' in response.context) is available
    if 'form' in response.context:
        assert isinstance(response.context['form'], CommentForm)
