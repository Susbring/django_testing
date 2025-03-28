# news/tests/test_routes.py
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

from .common import CommonTestSetup

User = get_user_model()


class TestRoutes(CommonTestSetup):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.urls_for_anonymous = (
            reverse('notes:home'),
            reverse('users:login'),
            reverse('users:logout'),
            reverse('users:signup'),
        )
        cls.urls_for_author = (
            reverse('notes:add'),
            reverse('notes:list'),
            reverse('notes:success'),
        )
        cls.urls_only_for_author = (
            reverse('notes:detail', args=(cls.note.slug,)),
            reverse('notes:edit', args=(cls.note.slug,)),
            reverse('notes:delete', args=(cls.note.slug,)),
        )
        cls.login_url = reverse('users:login')

    def test_pages_availability(self):
        """Проверка страниц доступных для ананимного пользователя"""
        urls_and_users = (
            (self.client, self.urls_for_anonymous, HTTPStatus.OK),
            (self.client, self.urls_for_author, HTTPStatus.FOUND),
            (self.client, self.urls_only_for_author, HTTPStatus.FOUND),
            (self.author_client, self.urls_for_author, HTTPStatus.OK),
            (self.author_client, self.urls_only_for_author, HTTPStatus.OK),
            (self.reader_client,
             self.urls_only_for_author,
             HTTPStatus.NOT_FOUND),
            (self.reader_client,
             self.urls_for_anonymous,
             HTTPStatus.OK),
            (self.reader_client,
             self.urls_for_author,
             HTTPStatus.FOUND),
        )
        for client, urls, expected_status in urls_and_users:
            for url in urls:
                with self.subTest(user=client, url=url):
                    response = client.get(url)
                    self.assertEqual(response.status_code, expected_status)

    def test_redirect_for_anonymous(self):
        """
        При попытке перехода ананимного пользователся на страницы заметок,
        успешного добавления записи,
        удаления записи
        его перебрасывает на логин
        """
        urls = self.urls_only_for_author + self.urls_for_author
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{self.login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
