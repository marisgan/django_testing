from datetime import datetime, timedelta

from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone
import pytest

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
    return News.objects.create(title='Some Title', text='Some text')


@pytest.fixture
def news_feed():
    return News.objects.bulk_create(
        News(
            title=f'News {index}', text='More text',
            date=datetime.today() - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(news=news, author=author, text='Text')


@pytest.fixture
def comment_feed(news, author):
    comment_feed = Comment.objects.bulk_create(
        Comment(news=news, author=author, text=f'Text {index}')
        for index in range(22)
    )
    for index in range(22):
        comment_feed[index].created = timezone.now() - timedelta(days=index)
        comment_feed[index].save()
    return comment_feed


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def comments_url(detail_url):
    return f'{detail_url}#comments'


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def redirect_login_edit_url(login_url, edit_url):
    return login_url + f'?next={edit_url}'


@pytest.fixture
def redirect_login_delete_url(login_url, delete_url):
    return login_url + f'?next={delete_url}'


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(
    db,  # noqa
):
    pass
