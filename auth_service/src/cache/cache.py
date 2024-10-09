import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

from auth_service.src.database.redis import get_redis
from redis.asyncio import Redis


class BaseCacheStorage(ABC):
    """Абстрактное хранилище кэша.

    Позволяет сохранять и получать кэш.
    Способ хранения кэша может варьироваться в зависимости
    от итоговой реализации. Например, можно хранить информацию
    в базе данных или в распределённом файловом хранилище.
    """

    @abstractmethod
    def save_cache(self, key: str, cache: Dict[str, Any], expire: int | None = None) -> None:
        """Сохранить кэш в хранилище."""

    @abstractmethod
    def retrieve_cache(self, key: str) -> Dict[str, Any]:
        """Получить кэш из хранилища."""

    # @abstractmethod
    # async def save_access_token(self, mapping: Dict[str,list]):
    #     """Сохранить токен в словарь"""

    # @abstractmethod
    # async def get_access_token(self, login:str):
    #     """Получить токен из словаря"""

class RedisCacheStorage(BaseCacheStorage):

    def __init__(self, redis_adapter: Redis) -> None:
        self.redis_adapter = redis_adapter

    async def save_cache(self, key: str, cache: Dict[str, Any], expire: int | None = None) -> None:
        """Сохранить кэш в хранилище."""
        await self.redis_adapter.set(key, cache, ex=expire)

    async def retrieve_cache(self, key) -> Dict[str, Any]:
        """Получить кэш из хранилища."""
        cache = await self.redis_adapter.get(key)
        logging.debug(cache)
        return cache

    # async def save_access_token(self, mapping: Dict[str,list], login:str, token: str):
    #     self.redis_adapter.hset(name="access_tokens", mapping=mapping)
    #     self.redis_adapter.rpush(f"access_tokens:{login}", token)

    # async def get_access_token(self, login:str):
    #     dct = self.redis_adapter.hget(name="access_tokens", key=login)
    #     return dct


# # Записываем элементы карты в Redis
# r.hset("user:1000", mapping=my_map)

# # Получаем все значения из хэша
# user_data = r.hgetall("user:1000")

# # Преобразуем данные обратно в обычный словарь
# user_data_decoded = {k.decode('utf-8'): v.decode('utf-8') for k, v in user_data.items()}

# Пример получения одного поля:
# name = r.hget("user:1000", "name").decode('utf-8')
# print(name)  # John

# Пример удаления поля:
# r.hdel("user:1000", "city")



class Cache:
    """Класс для работы с кэшэм."""

    def __init__(self, storage: BaseCacheStorage) -> None:
        self.storage = storage

    async def set_cache(self, key: str, value: Any, expire: int | None = None) -> None:
        """Установить кэш для определённого ключа."""
        await self.storage.save_cache(key, value, expire)

    async def get_cache(self, key: str) -> Any:
        """Получить кэш по определённому ключу."""
        cache = await self.storage.retrieve_cache(key)
        if cache is None:
            return None

        return cache

    # async def set_map_cache(self, mapping: Dict[str,list]):
    #     await self.storage.save_access_token(mapping)

    # async def get_map_cache(self, login: str):
    #     res = await self.storage.get_access_token(login)
    #     return res



async def get_cache_storage():
    redis = await get_redis()
    storage = RedisCacheStorage(redis_adapter=redis)

    return Cache(storage=storage)

import redis
import time

# # Подключение к Redis
# r = redis.Redis(host='localhost', port=6379, db=0)

# # Создаем пустой хэш (если его нет)
# hash_key = "my_map"
# r.hset(hash_key, mapping={})  # создаем пустой хэш

# # Функция для добавления значения в список по ключу с временем истечения
# def add_value_to_map_with_expiry(redis_conn, hash_key, field, values, expiry_times):
#     """
#     Добавляем список значений к полю хэша и устанавливаем время истечения для каждого элемента.
#     :param redis_conn: Объект соединения с Redis.
#     :param hash_key: Ключ хэша (карты) в Redis.
#     :param field: Поле внутри хэша.
#     :param values: Список значений для добавления.
#     :param expiry_times: Список времен истечения (в секундах) для каждого значения.
#     """
#     for i, value in enumerate(values):
#         list_key = f"{hash_key}:{field}:{i}"  # Генерируем уникальный ключ для каждого значения в списке
#         redis_conn.set(list_key, value)       # Устанавливаем значение
#         redis_conn.expire(list_key, expiry_times[i])  # Устанавливаем время истечения

# # Пример добавления значений и их времени истечения
# values = ["apple", "banana", "orange"]
# expiry_times = [10, 20, 30]  # Время истечения в секундах для каждого значения

# # Добавляем значения в Redis и устанавливаем время истечения
# add_value_to_map_with_expiry(r, hash_key, "fruits", values, expiry_times)

# # Получаем значения из Redis перед их истечением
# for i in range(len(values)):
#     list_key = f"{hash_key}:fruits:{i}"
#     value = r.get(list_key)
#     if value:
#         print(f"Value: {value.decode('utf-8')} still exists!")
#     else:
#         print(f"Value with key {list_key} has expired.")

# # Пауза для проверки времени истечения
# time.sleep(15)

# # Проверяем значения после истечения времени
# for i in range(len(values)):
#     list_key = f"{hash_key}:fruits:{i}"
#     value = r.get(list_key)
#     if value:
#         print(f"Value: {value.decode('utf-8')} still exists after 15 seconds!")
#     else:
#         print(f"Value with key {list_key} has expired after 15 seconds.")
