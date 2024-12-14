from django.conf import settings

import pytest

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count(client, news_list, home_url):
    response = client.get(home_url)
    news_count = response.context['object_list'].count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, news_list, home_url):
    response = client.get(home_url)
    dates = [news.date for news in response.context['object_list']]
    sorted_dates = sorted(dates, reverse=True)
    assert dates == sorted_dates


def test_anon_client_no_form(client, detail_url):
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_aut_client_form(author_client, detail_url):
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


def test_comment_order(client,
                       news,
                       comments_list,
                       detail_url):
    response = client.get(detail_url)
    assert 'news' in response.context
    news_instance = response.context['news']
    comment = list(news_instance.comment_set.all())
    sorted_comments = sorted(comment, key=lambda comment: comment.created)
    assert comment == sorted_comments
