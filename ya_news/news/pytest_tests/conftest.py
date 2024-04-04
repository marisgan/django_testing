from datetime import datetime, timedelta

from django.conf import settings  # type: ignore
from django.test.client import Client  # type: ignore
from django.urls import reverse  # type: ignore
from django.utils import timezone  # type: ignore

import pytest

from news.forms import BAD_WORDS
from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Author')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Reader')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news():
    news = News.objects.create(title='Some Title', text='Some text')
    return news


@pytest.fixture
def news_id(news):
    return (news.id,)


@pytest.fixture
def news_feed():
    news_feed = News.objects.bulk_create(
        News(
            title=f'News {index}', text='More text',
            date=datetime.today() - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    return news_feed


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news, author=author, text='Comment text'
    )
    return comment


@pytest.fixture
def comment2(news, author):
    comment2 = Comment.objects.create(
        news=news, author=author, text='Other text'
    )
    comment2.created = timezone.now() - timedelta(days=2)
    comment2.save
    return comment2


@pytest.fixture
def comment_id(comment):
    return (comment.id,)


@pytest.fixture
def form_data():
    return {'text': 'New text'}


@pytest.fixture
def forbidden_data():
    return {'text': f'Text {BAD_WORDS[0]}'}


@pytest.fixture
def delete_url(comment_id):
    return reverse('news:delete', args=comment_id)


@pytest.fixture
def edit_url(comment_id):
    return reverse('news:edit', args=comment_id)


@pytest.fixture
def detail_url(news_id):
    return reverse('news:detail', args=news_id)


@pytest.fixture
def comments_url(detail_url):
    return f'{detail_url}#comments'


@pytest.fixture
def home_url():
    return reverse('news:home')
