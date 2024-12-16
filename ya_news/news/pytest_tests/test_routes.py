from http import HTTPStatus

from pytest_django.asserts import assertRedirects
import pytest


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url_fixture, client_fixture, expected_status',
    (
        ('home_url', 'client', HTTPStatus.OK),
        ('detail_url', 'client', HTTPStatus.OK),
        ('login_url', 'client', HTTPStatus.OK),
        ('logout_url', 'client', HTTPStatus.OK),
        ('signup_url', 'client', HTTPStatus.OK),
        ('edit_url', 'client', HTTPStatus.FOUND),
        ('delete_url', 'client', HTTPStatus.FOUND),
        ('home_url', 'admin_client', HTTPStatus.OK),
        ('detail_url', 'admin_client', HTTPStatus.OK),
        ('login_url', 'admin_client', HTTPStatus.OK),
        ('logout_url', 'admin_client', HTTPStatus.OK),
        ('signup_url', 'admin_client', HTTPStatus.OK),
        ('edit_url', 'admin_client', HTTPStatus.NOT_FOUND),
        ('delete_url', 'admin_client', HTTPStatus.NOT_FOUND),
        ('home_url', 'author_client', HTTPStatus.OK),
        ('detail_url', 'author_client', HTTPStatus.OK),
        ('login_url', 'author_client', HTTPStatus.OK),
        ('logout_url', 'author_client', HTTPStatus.OK),
        ('signup_url', 'author_client', HTTPStatus.OK),
        ('edit_url', 'author_client', HTTPStatus.OK),
        ('delete_url', 'author_client', HTTPStatus.OK),
    )
)
def test_pages_availability(request,
                            url_fixture,
                            client_fixture,
                            expected_status):
    """Проверяет доступность URL клиенту и ожидаемый код состояния"""
    url = request.getfixturevalue(url_fixture)
    client = request.getfixturevalue(client_fixture)
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_fixture',
    (
        'edit_url',
        'delete_url'
    )
)
def test_redirect_for_anon(
        request,
        client,
        login_url,
        url_fixture
):
    """
    Тестирует, что припопытке анонимного пользователя удалить
    или отредактировать комментарий его переносит на страницу входа
    """
    url = request.getfixturevalue(url_fixture)
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)
