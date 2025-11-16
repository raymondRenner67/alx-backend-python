#!/usr/bin/env python3
"""Unit tests for the utils module.

This module contains unit tests for utility functions including
access_nested_map, get_json, and the memoize decorator. It uses
parameterized tests and mocking to ensure comprehensive test coverage.
"""
import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized
from utils import access_nested_map, get_json, memoize


class TestAccessNestedMap(unittest.TestCase):
    """Test cases for the access_nested_map function."""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(
        self, nested_map: dict, path: tuple, expected: any
    ) -> None:
        """Test that access_nested_map returns the expected value.

        Args:
            nested_map: The nested dictionary to access
            path: The path of keys to follow
            expected: The expected value at the path
        """
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), "a"),
        ({"a": 1}, ("a", "b"), "b"),
    ])
    def test_access_nested_map_exception(
        self, nested_map: dict, path: tuple, exception_key: str
    ) -> None:
        """Test that access_nested_map raises KeyError for invalid paths.

        Args:
            nested_map: The nested dictionary to access
            path: The path of keys to follow
            exception_key: The key that should raise KeyError
        """
        with self.assertRaises(KeyError) as context:
            access_nested_map(nested_map, path)
        self.assertEqual(str(context.exception), f"'{exception_key}'")


class TestGetJson(unittest.TestCase):
    """Test cases for the get_json function."""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch("utils.requests.get")
    def test_get_json(
        self, test_url: str, test_payload: dict, mock_get: Mock
    ) -> None:
        """Test that get_json returns the expected JSON payload.

        Args:
            test_url: The URL to fetch from
            test_payload: The expected JSON payload
            mock_get: The mocked requests.get function
        """
        mock_response = Mock()
        mock_response.json.return_value = test_payload
        mock_get.return_value = mock_response

        result = get_json(test_url)

        self.assertEqual(result, test_payload)
        mock_get.assert_called_once_with(test_url)


class TestMemoize(unittest.TestCase):
    """Test cases for the memoize decorator."""

    def test_memoize(self) -> None:
        """Test that memoize decorator caches function results.

        This test verifies that when a memoized method is called
        multiple times, the underlying method is only called once,
        and the cached result is returned on subsequent calls.
        """
        class TestClass:
            """Test class with a method and a memoized property."""

            def a_method(self) -> int:
                """Return a constant value."""
                return 42

            @memoize
            def a_property(self) -> int:
                """Memoized property that calls a_method."""
                return self.a_method()

        with patch.object(
            TestClass, "a_method", return_value=42
        ) as mock_method:
            obj = TestClass()
            # Call the memoized property twice
            result1 = obj.a_property
            result2 = obj.a_property
            # Verify both calls return 42
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)
            # Verify the underlying method was only called once
            mock_method.assert_called_once()


if __name__ == "__main__":
    unittest.main()
