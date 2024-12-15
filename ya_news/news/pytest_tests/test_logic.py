from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db

FORM_DATA = {'text': 'Новый комментарий'}


def test_anon_cant_comment(client, detail_url):
    comments_count = Comment.objects.count()
    client.post(detail_url, data=FORM_DATA)
    comment_count = Comment.objects.count()
    assert comments_count == comment_count


def test_auth_user_can_comment(
        author_client,
        detail_url,
        news,
        author
):
    Comment.objects.all().delete()
    comments_count = Comment.objects.count()
    response = author_client.post(
        detail_url,
        data=FORM_DATA
    )
    assertRedirects(response, f'{detail_url}#comments')
    comment_count = Comment.objects.count()
    assert comment_count == comments_count + 1
    comment = Comment.objects.get()
    assert comment.text == FORM_DATA['text']
    assert comment.news == news
    assert comment.author == author


def test_cant_use_bad_words(author_client, detail_url):
    bad_word_data = {'text': f'{BAD_WORDS[0]}'}
    comments_count = Comment.objects.count()
    response = author_client.post(detail_url, data=bad_word_data)
    assertFormError(response,
                    form='form',
                    field='text',
                    errors=WARNING)
    comment_count = Comment.objects.count()
    assert comments_count == comment_count


def test_auth_can_delete_comment(
        author_client,
        delete_url,
        url_to_comments,
        comment
):
    comments_count = Comment.objects.count()
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    with pytest.raises(Comment.DoesNotExist):
        Comment.objects.get(pk=comment.pk)
    comment_count = Comment.objects.count()
    assert comment_count == comments_count - 1


def test_auth_can_edit_comment(
        author_client,
        edit_url,
        url_to_comments,
        comment
):
    comments_count = Comment.objects.count()
    auth = comment.author
    nws = comment.news
    response = author_client.post(edit_url, data=FORM_DATA)
    assertRedirects(response, url_to_comments)
    update_comment = Comment.objects.get(pk=comment.pk)
    assert update_comment.text == FORM_DATA['text']
    assert update_comment.author == auth
    assert update_comment.news == nws
    comment_count = Comment.objects.count()
    assert comments_count == comment_count


def test_user_cant_delete_comment_another_user(
        admin_client,
        delete_url,
        comment
):
    comments_count = Comment.objects.count()
    response = admin_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_count = Comment.objects.count()
    assert comment_count == comments_count
    old_comment = Comment.objects.get(pk=comment.pk)
    assert old_comment.text == comment.text
    assert old_comment.author == comment.author
    assert old_comment.news == comment.news


def test_user_cant_edit_comment_another_user(
        admin_client,
        edit_url,
        comment
):
    comments_count = Comment.objects.count()
    txt = comment.text
    auth = comment.author
    nws = comment.news
    response = admin_client.post(edit_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    update = Comment.objects.get(id=comment.id)
    assert update.text == txt
    assert update.author == auth
    assert update.news == nws
    comment_count = Comment.objects.count()
    assert comments_count == comment_count
