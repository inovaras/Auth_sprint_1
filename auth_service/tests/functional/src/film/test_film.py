import asyncio
import pytest
from http import HTTPStatus

from settings import test_settings
from testdata.data.film import film_collections, one_film
from plugins import pytest_plugins

"""
все граничные случаи по валидации данных;
поиск конкретного фильма;+
вывести все фильмы;+
поиск с учётом кеша в Redis.
"""


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {},  # запрос без указания параметров
            {'status': HTTPStatus.UNAUTHORIZED},
        )
    ],
    ids=["unauthorized connection"],
)
@pytest.mark.asyncio
async def test_unauthorized(make_get_request, query_data: dict, expected_answer: dict):

    url = f"{test_settings.AUTH_SERVICE_URL}/api/v1/auth/me/"
    body, headers, status = await make_get_request(url, query_data)

    assert status == expected_answer['status']


@pytest.mark.parametrize(
    'payload, expected_answer',
    [
        (
            {"login": "test_user", "password": "test_user"},  # запрос без указания параметров
            {'status': HTTPStatus.CREATED},
        )
    ],
    ids=["test_register"],
)
@pytest.mark.asyncio
async def test_register(make_post_request, payload: dict, expected_answer: dict):

    url = f"{test_settings.AUTH_SERVICE_URL}/api/v1/auth/register/"
    body, headers, status = await make_post_request(url, payload)

    assert status == expected_answer['status']
