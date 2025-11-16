#!/usr/bin/env python3
"""Unit and integration tests for the github client module.

This module contains tests for GithubOrgClient class including unit tests
and integration tests using parameterization and mocking patterns.
"""
import unittest
from unittest.mock import patch, Mock, PropertyMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient class."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name: str, mock_get_json: Mock) -> None:
        """Test that GithubOrgClient.org returns the correct value.

        Args:
            org_name: The organization name to test
            mock_get_json: The mocked get_json function
        """
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.return_value = {"key": "value"}

        client = GithubOrgClient(org_name)
        result = client.org

        mock_get_json.assert_called_once_with(expected_url)
        self.assertEqual(result, {"key": "value"})

    def test_public_repos_url(self) -> None:
        """Test that GithubOrgClient._public_repos_url returns correct URL.

        This test mocks GithubOrgClient.org to return a known payload
        and verifies that _public_repos_url extracts the correct URL.
        """
        with patch.object(
            GithubOrgClient, "org", new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = {"repos_url": "https://api.github.com/orgs/test/repos"}
            client = GithubOrgClient("test")
            self.assertEqual(
                client._public_repos_url,
                "https://api.github.com/orgs/test/repos"
            )

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json: Mock) -> None:
        """Test that GithubOrgClient.public_repos returns correct repo list.

        Args:
            mock_get_json: The mocked get_json function
        """
        test_payload = [
            {"name": "repo1", "license": {"key": "apache-2.0"}},
            {"name": "repo2", "license": {"key": "mit"}},
        ]
        mock_get_json.return_value = test_payload

        with patch.object(
            GithubOrgClient, "_public_repos_url", new_callable=PropertyMock
        ) as mock_repos_url:
            mock_repos_url.return_value = "https://api.github.com/orgs/test/repos"
            client = GithubOrgClient("test")
            repos = client.public_repos()

            self.assertEqual(repos, ["repo1", "repo2"])
            mock_get_json.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(
        self, repo: dict, license_key: str, expected: bool
    ) -> None:
        """Test that GithubOrgClient.has_license checks license correctly.

        Args:
            repo: The repository dictionary
            license_key: The license key to check for
            expected: The expected boolean result
        """
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    TEST_PAYLOAD,
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient using fixtures.

    This class is parameterized with fixtures from fixtures.py and tests
    the full integration of GithubOrgClient with mocked HTTP requests.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """Set up class-level test fixtures.

        This method mocks requests.get to return the fixture payloads
        based on the URL being requested.
        """
        cls.get_patcher = patch("requests.get")
        cls.mock_get = cls.get_patcher.start()

        def mock_get_side_effect(url: str) -> Mock:
            """Return appropriate mock response based on URL.

            Args:
                url: The URL being requested

            Returns:
                A mock response object with json method
            """
            mock_response = Mock()
            if url == "https://api.github.com/orgs/google":
                mock_response.json.return_value = cls.org_payload
            elif url == cls.org_payload["repos_url"]:
                mock_response.json.return_value = cls.repos_payload
            return mock_response

        cls.mock_get.side_effect = mock_get_side_effect

    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up after tests.

        This method stops the patcher and cleans up resources.
        """
        cls.get_patcher.stop()

    def test_public_repos(self) -> None:
        """Test that public_repos returns the correct list of repositories."""
        client = GithubOrgClient("google")
        repos = client.public_repos()
        self.assertEqual(repos, self.expected_repos)

    def test_public_repos_with_apache2_license(self) -> None:
        """Test that public_repos filters by Apache 2.0 license correctly."""
        client = GithubOrgClient("google")
        repos = client.public_repos(license="apache-2.0")
        self.assertEqual(repos, self.apache2_repos)


if __name__ == "__main__":
    unittest.main()
