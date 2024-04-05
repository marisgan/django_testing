from http import HTTPStatus

from .settings import (
    ADD_URL, BaseSetup, DELETE_URL, DETAIL_URL, DELETE_URL, EDIT_URL,
    HOME_URL, LIST_URL, LOGIN_URL, LOGOUT_URL,
    SUCCESS_URL, SIGNUP_URL,
)


class TestRoutes(BaseSetup):

    def test_pages_availability(self):
        """Доступ к страницам для анонима и пользователя"""
        for client, url, expected_status in (
            (self.client, HOME_URL, HTTPStatus.OK),
            (self.client, LOGIN_URL, HTTPStatus.OK),
            (self.client, LOGOUT_URL, HTTPStatus.OK),
            (self.client, SIGNUP_URL, HTTPStatus.OK),
            (self.user_client, LIST_URL, HTTPStatus.OK),
            (self.user_client, ADD_URL, HTTPStatus.OK),
            (self.user_client, SUCCESS_URL, HTTPStatus.OK),
            (self.user_client, DETAIL_URL, HTTPStatus.NOT_FOUND),
            (self.user_client, EDIT_URL, HTTPStatus.NOT_FOUND),
            (self.user_client, DELETE_URL, HTTPStatus.NOT_FOUND),
            (self.author_client, DETAIL_URL, HTTPStatus.OK),
            (self.author_client, EDIT_URL, HTTPStatus.OK),
            (self.author_client, DELETE_URL, HTTPStatus.OK),

        ):
            with self.subTest(client=client, url=url):
                self.assertEqual(client.get(url).status_code, expected_status)

    def test_redirects_for_anonym(self):
        """Редирект анонима на страницу логина"""
        for url in (
            LIST_URL, SUCCESS_URL, ADD_URL, DETAIL_URL, EDIT_URL, DELETE_URL
        ):
            with self.subTest(url=url):
                self.assertRedirects(
                    self.client.get(url),
                    f'{LOGIN_URL}?next={url}'
                )
