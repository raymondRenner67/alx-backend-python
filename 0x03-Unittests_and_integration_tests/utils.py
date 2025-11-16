#!/usr/bin/env python3
"""Generic utilities for github org client.
This module provides utility functions for accessing nested data structures,
making HTTP requests, and caching function results.
"""
import requests
from functools import wraps
from typing import (
    Mapping,
    Sequence,
    Any,
    Dict,
    Callable,
)

__all__ = [
    "access_nested_map",
    "get_json",
    "memoize",
]


def access_nested_map(nested_map: Mapping, path: Sequence) -> Any:
    """Access a value in a nested map using a sequence of keys.

    This function traverses through a nested dictionary structure using
    the provided path sequence and returns the value at that path.
    Raises KeyError if any key in the path is not found.

    Args:
        nested_map: A nested mapping (dictionary) structure
        path: A sequence of keys representing the path to the value

    Returns:
        The value at the specified path in the nested map

    Raises:
        KeyError: If any key in the path is not found or if the path
                 tries to traverse through a non-mapping value

    Example:
        >>> nested_map = {"a": {"b": {"c": 1}}}
        >>> access_nested_map(nested_map, ("a", "b", "c"))
        1
    """
    for key in path:
        if not isinstance(nested_map, Mapping):
            raise KeyError(key)
        nested_map = nested_map[key]

    return nested_map


def get_json(url: str) -> Dict:
    """Fetch and return JSON data from a remote URL.

    This function makes an HTTP GET request to the specified URL and
    returns the JSON response as a dictionary.

    Args:
        url: The URL to fetch JSON data from

    Returns:
        The JSON response parsed as a dictionary

    Raises:
        requests.RequestException: If the HTTP request fails
        ValueError: If the response is not valid JSON
    """
    response = requests.get(url)
    return response.json()


def memoize(fn: Callable) -> Callable:
    """Decorator to memoize a method by converting it to a property.

    This decorator caches the result of a method call on an instance
    and returns the cached value on subsequent calls. It converts the
    decorated method into a property.

    Args:
        fn: The function to be memoized

    Returns:
        A property that caches the function's return value

    Example:
        >>> class MyClass:
        ...     @memoize
        ...     def expensive_method(self):
        ...         print("Computing...")
        ...         return 42
        >>> obj = MyClass()
        >>> obj.expensive_method  # Prints "Computing..."
        42
        >>> obj.expensive_method  # Returns cached value, no output
        42
    """
    attr_name = "_{}".format(fn.__name__)

    @wraps(fn)
    def memoized(self: Any) -> Any:
        """Memoized wrapper that stores and retrieves cached values."""
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)

    return property(memoized)
