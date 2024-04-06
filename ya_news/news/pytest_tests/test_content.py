from django.conf import settings

from news.forms import CommentForm


def test_news_count(client, news_feed, home_url):
    assert (
        client.get(home_url).context['object_list'].count()
        == settings.NEWS_COUNT_ON_HOME_PAGE
    )


def test_news_order(client, news_feed, home_url):
    all_dates = [
        news.date for news in client.get(home_url).context['object_list']
    ]
    assert all_dates == sorted(all_dates, reverse=True)


def test_comments_order(client, comments, detail_url):
    response = client.get(detail_url)
    assert 'news' in response.context
    timestamps = [
        comment.created
        for comment in response.context['news'].comment_set.all()
    ]
    assert timestamps == sorted(timestamps)


def test_form_availability_for_anonym(client, detail_url):
    assert 'form' not in client.get(detail_url).context


def test_form_availability_for_user(reader_client, detail_url):
    assert isinstance(
        reader_client.get(detail_url).context.get('form'),
        CommentForm
    )
