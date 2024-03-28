#!/usr/bin/env python3
"""
Module containing tools for request caching and tracking
"""

import requests
import redis
import time
from functools import wraps
from typing import Callable


def cache_page(url: str, result: str, expiry: int, redis_conn: redis.Redis):
    """
    Caches the result of a URL with a given expiry time
    """
    redis_conn.setex(f"count:{url}", expiry, result)


def count_access(url: str, redis_conn: redis.Redis):
    """
    Increments the access count for a given URL
    """
    count_key = f"count:{url}"
    if not redis_conn.exists(count_key):
        redis_conn.set(count_key, 1)
    else:
        try:
            redis_conn.incr(count_key)
        except redis.exceptions.ResponseError:
            # If the value is not an integer or out of range, set it to 1
            redis_conn.set(count_key, 1)


def cached_get_page(expiry: int):
    """
    Decorator for caching the result of a function
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(url: str) -> str:
            redis_conn = redis.Redis()
            cached_result = redis_conn.get(f"count:{url}")
            if cached_result:
                count_access(url, redis_conn)
                return cached_result.decode('utf-8')
            else:
                result = func(url)
                cache_page(url, result, expiry, redis_conn)
                return result
        return wrapper
    return decorator


@cached_get_page(10)
def get_page(url: str) -> str:
    """
    Retrieves the HTML content of a URL
    """
    response = requests.get(url)
    return response.text


# Testing the get_page function
if __name__ == "__main__":
    url = "http://slowwly.robertomurray.co.uk"
    for i in range(5):
        print(get_page(url))
        time.sleep(1)
